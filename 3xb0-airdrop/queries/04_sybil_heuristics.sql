-- Q4: Optional sybil scoring to prune the list further.
-- Flags addresses with patterns that suggest farming/automation.
-- Run AFTER Q3 to mark/exclude before generating the merkle root.
-- Heuristics (each independent — combine with WHERE/AND as you like):
--   a) Only outbound to one contract  → probably a farm leg
--   b) Created and emptied within 1 day → throwaway
--   c) Wallet age < 7 days at snapshot → fresh sybil
--   d) Exact same gas-paid amount across all txs → script

WITH stats AS (
  SELECT
    "from"                                                AS addr,
    COUNT(*)                                              AS tx_count,
    COUNT(DISTINCT "to")                                  AS distinct_destinations,
    MIN(block_time)                                       AS first_seen,
    MAX(block_time)                                       AS last_seen,
    DATE_DIFF('day', MIN(block_time), MAX(block_time))    AS lifespan_days,
    DATE_DIFF('day', MIN(block_time), CURRENT_TIMESTAMP)  AS age_days,
    APPROX_DISTINCT(gas_price)                            AS distinct_gas_prices
  FROM base.transactions
  GROUP BY "from"
)
SELECT
  addr,
  tx_count,
  distinct_destinations,
  lifespan_days,
  age_days,
  CASE WHEN distinct_destinations = 1            THEN 1 ELSE 0 END AS flag_single_dest,
  CASE WHEN lifespan_days <= 1 AND tx_count > 3  THEN 1 ELSE 0 END AS flag_burst_and_dead,
  CASE WHEN age_days < 7                         THEN 1 ELSE 0 END AS flag_fresh,
  CASE WHEN distinct_gas_prices = 1              THEN 1 ELSE 0 END AS flag_uniform_gas
FROM stats
WHERE tx_count >= 2;
