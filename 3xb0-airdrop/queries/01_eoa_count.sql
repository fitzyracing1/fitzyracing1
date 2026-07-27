-- Q1: How many distinct EOAs have ever signed a transaction on Base?
-- Cheap (one aggregate). Run this first to size the airdrop.
-- Note: only EOAs can appear in transactions.from on an EVM chain, so this
-- gives a clean EOA count with no contract filtering needed.

SELECT
  COUNT(DISTINCT "from") AS eoa_count,
  MIN(block_time)        AS first_tx,
  MAX(block_time)        AS last_tx,
  COUNT(*)               AS total_txs
FROM base.transactions;
