-- Q3: Snapshot the airdrop list with a fixed cutoff block.
-- Tweak :cutoff_block and :min_txs once you've seen Q1/Q2 results.
-- Default: ≥2 txs to drop the worst sybil layer; pre-cutoff so it's reproducible.
-- Expected row count: in the tens of millions — Dune free tier WILL time out
-- or truncate. Plan to use the Dune API + pagination, or run this on a self-
-- indexed Base node / Allium / Goldsky if it fails on Dune.

-- Parameters (Dune: use {{cutoff_block}} / {{min_txs}} as query params)
-- :cutoff_block  e.g. 25000000
-- :min_txs       e.g. 2

SELECT
  "from"             AS address,
  COUNT(*)           AS tx_count,
  MIN(block_time)    AS first_seen,
  MAX(block_time)    AS last_seen,
  MIN(block_number)  AS first_block,
  MAX(block_number)  AS last_block
FROM base.transactions
WHERE block_number <= {{cutoff_block}}
GROUP BY "from"
HAVING COUNT(*) >= {{min_txs}}
ORDER BY tx_count DESC;
