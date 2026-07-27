// Copyright (c) 2024-present The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <node/persistentservice.h>

#include <logging.h>
#include <net.h>           // CConnman::GetNodeCount
#include <node/context.h>
#include <scheduler.h>
#include <txmempool.h>     // CTxMemPool
#include <util/thread.h>   // util::TraceThread
#include <validation.h>    // ChainstateManager

#include <chrono>
#include <string>

namespace node {

// ─────────────────────────────────────────────────────────────────────────────
// Construction / destruction
// ─────────────────────────────────────────────────────────────────────────────

NodePersistentService::NodePersistentService(NodeContext& node)
    : m_node(node)
    , m_start_time(std::chrono::steady_clock::now())
{
}

NodePersistentService::~NodePersistentService()
{
    Stop();
}

// ─────────────────────────────────────────────────────────────────────────────
// Start
// ─────────────────────────────────────────────────────────────────────────────

void NodePersistentService::Start(CScheduler& scheduler)
{
    if (m_running.exchange(true, std::memory_order_acq_rel)) {
        // Already started — idempotent.
        return;
    }

    m_start_time = std::chrono::steady_clock::now();
    m_interrupt.reset();
    {
        LOCK(m_token_mutex);
        m_diagnostic_tokens = DIAGNOSTIC_TOKEN_CAPACITY;
    }

    // ── Pattern 1: periodic scheduler tasks ──────────────────────────────────
    // These run on the shared "scheduler" thread, so they must be fast
    // (non-blocking).

    // Heartbeat: emit a brief log line every HEARTBEAT_INTERVAL.
    scheduler.scheduleEvery([this] {
        LogHeartbeat();
    }, HEARTBEAT_INTERVAL);

    // Diagnostic: offload a heavier snapshot to the thread pool every
    // DIAGNOSTIC_INTERVAL.  This keeps the scheduler thread free.
    scheduler.scheduleEvery([this] {
        ScheduleDiagnosticSnapshot();
    }, DIAGNOSTIC_INTERVAL);

    // ── Pattern 2: long-running background thread ─────────────────────────────
    // The thread loops, sleeps for MONITOR_INTERVAL, updates m_last_snapshot,
    // and exits as soon as m_interrupt is set.
    m_thread_pool.Start(/*num_workers=*/1);

    m_monitor_thread = std::thread(
        util::TraceThread, "persistmon",
        [this] { RunMonitorThread(); });

    LogInfo("[PersistentService] started — monitor thread, scheduler tasks, and thread pool active.\n");
}

// ─────────────────────────────────────────────────────────────────────────────
// Stop
// ─────────────────────────────────────────────────────────────────────────────

void NodePersistentService::Stop()
{
    if (!m_running.exchange(false, std::memory_order_acq_rel)) {
        return; // Already stopped.
    }

    // Signal the monitor thread to wake up and exit.
    m_interrupt();

    if (m_monitor_thread.joinable()) {
        m_monitor_thread.join();
    }

    // Drain and stop the thread pool.
    m_thread_pool.Stop();

    LogInfo("[PersistentService] stopped.\n");
}

// ─────────────────────────────────────────────────────────────────────────────
// Public accessors
// ─────────────────────────────────────────────────────────────────────────────

NodeHealthSnapshot NodePersistentService::GetLastSnapshot() const
{
    LOCK(m_snapshot_mutex);
    return m_last_snapshot;
}

// ─────────────────────────────────────────────────────────────────────────────
// Pattern 2 implementation: monitor thread
// ─────────────────────────────────────────────────────────────────────────────

void NodePersistentService::RunMonitorThread()
{
    LogInfo("[PersistentService] monitor thread started.\n");

    while (!m_interrupt) {
        // Collect and store a fresh snapshot while the node runs.
        NodeHealthSnapshot snap = CollectSnapshot();
        {
            LOCK(m_snapshot_mutex);
            m_last_snapshot = snap;
        }

        LogDebug(BCLog::ALL, "[PersistentService] monitor snapshot — peers=%d tip=%d "
                             "mempool_txs=%" PRIu64 " mempool_bytes=%" PRIu64
                             " uptime=%" PRId64 "s\n",
                 snap.peer_count,
                 snap.tip_height,
                 snap.mempool_tx_count,
                 snap.mempool_usage_bytes,
                 snap.service_uptime_seconds);

        // Interruptible sleep: wakes immediately when Stop() is called.
        m_interrupt.sleep_for(MONITOR_INTERVAL);
    }

    LogInfo("[PersistentService] monitor thread exiting.\n");
}

// ─────────────────────────────────────────────────────────────────────────────
// Internal helpers
// ─────────────────────────────────────────────────────────────────────────────

NodeHealthSnapshot NodePersistentService::CollectSnapshot() const
{
    NodeHealthSnapshot snap;
    snap.captured_at = std::chrono::steady_clock::now();
    snap.service_uptime_seconds =
        std::chrono::duration_cast<std::chrono::seconds>(
            snap.captured_at - m_start_time).count();

    // Peer count (connman may not be available during early startup).
    if (m_node.connman) {
        snap.peer_count = static_cast<int>(
            m_node.connman->GetNodeCount(ConnectionDirection::Both));
    }

    // Mempool metrics.
    if (m_node.mempool) {
        snap.mempool_tx_count   = static_cast<uint64_t>(m_node.mempool->size());
        snap.mempool_usage_bytes = m_node.mempool->DynamicMemoryUsage();
    }

    // Chain tip height.
    if (m_node.chainman) {
        snap.tip_height = m_node.chainman->ActiveHeight();
    }

    return snap;
}

void NodePersistentService::LogHeartbeat() const
{
    const NodeHealthSnapshot snap = GetLastSnapshot();
    LogInfo("[PersistentService] heartbeat — peers=%d tip=%d "
            "mempool_txs=%" PRIu64 " uptime=%" PRId64 "s\n",
            snap.peer_count,
            snap.tip_height,
            snap.mempool_tx_count,
            snap.service_uptime_seconds);
}

// ─────────────────────────────────────────────────────────────────────────────
// Pattern 3 implementation: thread pool burst work
// ─────────────────────────────────────────────────────────────────────────────

void NodePersistentService::ScheduleDiagnosticSnapshot()
{
    if (!ConsumeDiagnosticToken()) {
        return;
    }

    // Offload heavier diagnostic work to the pool so the scheduler thread
    // is never blocked.  We intentionally discard the future here — the
    // lambda guards against exceptions internally.
    [[maybe_unused]] auto result = m_thread_pool.Submit([this]() noexcept {
        try {
            NodeHealthSnapshot snap = CollectSnapshot();
            LogInfo("[PersistentService] diagnostic snapshot — "
                    "peers=%d tip=%d mempool_txs=%" PRIu64
                    " mempool_bytes=%" PRIu64 " uptime=%" PRId64 "s\n",
                    snap.peer_count,
                    snap.tip_height,
                    snap.mempool_tx_count,
                    snap.mempool_usage_bytes,
                    snap.service_uptime_seconds);
        } catch (const std::exception& e) {
            LogError("[PersistentService] diagnostic snapshot failed: %s\n", e.what());
        }
    });
}

bool NodePersistentService::ConsumeDiagnosticToken()
{
    LOCK(m_token_mutex);

    if (m_diagnostic_tokens <= 0) {
        m_diagnostic_tokens = DIAGNOSTIC_TOKEN_CAPACITY;
        LogInfo("[PersistentService] diagnostic tokens depleted, refilled to %d.\n",
                m_diagnostic_tokens);
    }

    --m_diagnostic_tokens;
    return true;
}

} // namespace node
