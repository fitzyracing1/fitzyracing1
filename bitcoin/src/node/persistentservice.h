// Copyright (c) 2024-present The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BITCOIN_NODE_PERSISTENTSERVICE_H
#define BITCOIN_NODE_PERSISTENTSERVICE_H

/**
 * @file persistentservice.h
 * @brief Persistent background service for Bitcoin Core node health monitoring.
 *
 * This module demonstrates all three persistent-process patterns used in Bitcoin Core:
 *
 *  1. Periodic scheduled tasks  — registered on the shared CScheduler so they run
 *     on the existing lightweight scheduler thread (no extra thread cost).
 *
 *  2. Long-running background thread — a dedicated thread that sleeps between
 *     work cycles and exits cleanly when interrupted; uses CThreadInterrupt for
 *     cooperative cancellation.
 *
 *  3. Thread pool (burst work) — offloads occasional CPU-intensive diagnostic
 *     snapshots to the shared ThreadPool so the node's hot paths are never
 *     blocked.
 *
 * Lifecycle
 * ---------
 *   NodePersistentService svc(node);
 *   svc.Start();   // typically called from AppInitMain()
 *   ...
 *   svc.Stop();    // called from Shutdown() before destroying the node context
 */

#include <util/threadinterrupt.h>
#include <util/threadpool.h>

#include <atomic>
#include <chrono>
#include <cstdint>
#include <string>
#include <thread>

class CScheduler;

namespace node {

struct NodeContext;

// ─────────────────────────────────────────────────────────────────────────────
// NodeHealthSnapshot
// ─────────────────────────────────────────────────────────────────────────────

/** Point-in-time health metrics collected by the persistent service. */
struct NodeHealthSnapshot {
    std::chrono::steady_clock::time_point captured_at;

    // Memory-pool metrics (zero when mempool not available)
    uint64_t mempool_tx_count{0};
    uint64_t mempool_usage_bytes{0};

    // Peer metrics (zero when connman not available)
    int peer_count{0};

    // Block chain tip height (-1 when chainman not available)
    int tip_height{-1};

    // Uptime of this monitoring instance (seconds)
    int64_t service_uptime_seconds{0};
};

// ─────────────────────────────────────────────────────────────────────────────
// NodePersistentService
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Persistent node-health monitor.
 *
 * Thread-safety: Start() / Stop() must be called from the same controlling
 * thread. GetLastSnapshot() may be called from any thread.
 */
class NodePersistentService
{
public:
    /** How often the long-running monitor thread wakes up. */
    static constexpr std::chrono::seconds MONITOR_INTERVAL{30};

    /** How often a detailed diagnostic snapshot is scheduled via the scheduler. */
    static constexpr std::chrono::minutes DIAGNOSTIC_INTERVAL{10};

    /** How often a lightweight heartbeat log entry is emitted. */
    static constexpr std::chrono::minutes HEARTBEAT_INTERVAL{5};

    /** Maximum burst size for diagnostic snapshots. */
    static constexpr int DIAGNOSTIC_TOKEN_CAPACITY{5};

    explicit NodePersistentService(NodeContext& node);
    ~NodePersistentService();

    // Non-copyable, non-movable (owns threads).
    NodePersistentService(const NodePersistentService&) = delete;
    NodePersistentService& operator=(const NodePersistentService&) = delete;

    /**
     * Start all persistent processes:
     *   - Register periodic scheduler tasks on @p scheduler.
     *   - Launch the dedicated monitor thread.
     *   - Start the internal thread pool (1 worker by default).
     */
    void Start(CScheduler& scheduler);

    /**
     * Signal all processes to stop and wait for them to finish.
     * Safe to call multiple times (idempotent).
     */
    void Stop();

    /** Thread-safe read of the most recently captured health snapshot. */
    NodeHealthSnapshot GetLastSnapshot() const;

    /** Return true if the service is running. */
    bool IsRunning() const { return m_running.load(std::memory_order_relaxed); }

private:
    // ── Internal helpers ────────────────────────────────────────────────────

    /** Entry point for the dedicated monitor thread. */
    void RunMonitorThread();

    /** Collect a NodeHealthSnapshot from the node context. */
    NodeHealthSnapshot CollectSnapshot() const;

    /** Emit a brief heartbeat log line. */
    void LogHeartbeat() const;

    /** Offload a detailed diagnostic snapshot to the thread pool. */
    void ScheduleDiagnosticSnapshot();

    /** Consume one diagnostic token and auto-refill when depleted. */
    bool ConsumeDiagnosticToken();

    // ── State ────────────────────────────────────────────────────────────────

    NodeContext& m_node;

    CThreadInterrupt m_interrupt;
    std::thread      m_monitor_thread;

    ThreadPool m_thread_pool{"persistent_service"};

    std::atomic<bool> m_running{false};

    mutable Mutex               m_snapshot_mutex;
    NodeHealthSnapshot          m_last_snapshot GUARDED_BY(m_snapshot_mutex);

    Mutex m_token_mutex;
    int   m_diagnostic_tokens GUARDED_BY(m_token_mutex){DIAGNOSTIC_TOKEN_CAPACITY};

    std::chrono::steady_clock::time_point m_start_time;
};

} // namespace node

#endif // BITCOIN_NODE_PERSISTENTSERVICE_H
