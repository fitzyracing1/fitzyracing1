-- Q2: Activity histogram — how many wallets at each activity level.
-- Tells you the sybil/dust ratio. Most chains: ~60-80% of addresses are
-- 1-tx accounts (airdrop farmers, throwaway, failed onboardings).
-- Use this to pick a sensible activity threshold for the airdrop list.

WITH per_addr AS (
  SELECT
    "from"     AS addr,
    COUNT(*)   AS tx_count
  FROM base.transactions
  GROUP BY "from"
)
SELECT
  CASE
    WHEN tx_count = 1                   THEN '01_one_tx'
    WHEN tx_count BETWEEN 2   AND 5     THEN '02_two_to_five'
    WHEN tx_count BETWEEN 6   AND 20    THEN '03_six_to_twenty'
    WHEN tx_count BETWEEN 21  AND 100   THEN '04_21_to_100'
    WHEN tx_count BETWEEN 101 AND 1000  THEN '05_101_to_1k'
    ELSE                                     '06_over_1k'
  END                          AS bucket,
  COUNT(*)                     AS addr_count,
  SUM(tx_count)                AS total_txs_in_bucket
FROM per_addr
GROUP BY 1
ORDER BY 1;
