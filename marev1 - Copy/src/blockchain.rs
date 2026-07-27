use crate::block::Block;
use crate::transaction::Transaction;

pub struct Blockchain {
    pub chain: Vec<Block>,
    pub pending_transactions: Vec<Transaction>,
    pub difficulty: usize,
    pub mining_reward: f64,
}

impl Blockchain {
    pub fn new() -> Self {
        let mut blockchain = Blockchain {
            chain: vec![],
            pending_transactions: vec![],
            difficulty: 2,
            mining_reward: 10.0,
        };

        // Create genesis block
        let genesis_block = Block::new(0, vec![], "0".to_string());
        blockchain.chain.push(genesis_block);

        blockchain
    }

    pub fn add_transaction(&mut self, transaction: Transaction) {
        self.pending_transactions.push(transaction);
    }

    pub fn mine_block(&mut self, miner_address: &str) {
        // Add mining reward transaction
        let reward_tx = Transaction::new(
            "System",
            miner_address,
            self.mining_reward,
            0.0,
        );

        self.pending_transactions.push(reward_tx);

        // Create new block
        let previous_block = &self.chain[self.chain.len() - 1];
        let mut new_block = Block::new(
            self.chain.len() as u64,
            self.pending_transactions.clone(),
            previous_block.hash.clone(),
        );

        // Mine the block
        new_block.mine_block(self.difficulty);

        self.chain.push(new_block);
        self.pending_transactions.clear();
    }

    pub fn get_balance(&self, address: &str) -> f64 {
        let mut balance = 0.0;

        for block in &self.chain {
            for tx in &block.transactions {
                if tx.to == address {
                    balance += tx.amount;
                }
                if tx.from == address {
                    balance -= tx.amount + tx.fee;
                }
            }
        }

        balance
    }

    pub fn is_chain_valid(&self) -> bool {
        for i in 1..self.chain.len() {
            let current_block = &self.chain[i];
            let previous_block = &self.chain[i - 1];

            // Verify current block's hash
            if current_block.hash != current_block.calculate_hash() {
                return false;
            }

            // Verify link to previous block
            if current_block.previous_hash != previous_block.hash {
                return false;
            }
        }

        true
    }
}

impl Default for Blockchain {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_blockchain_creation() {
        let blockchain = Blockchain::new();
        assert_eq!(blockchain.chain.len(), 1);
    }

    #[test]
    fn test_chain_validity() {
        let blockchain = Blockchain::new();
        assert!(blockchain.is_chain_valid());
    }

    #[test]
    fn test_mine_block() {
        let mut blockchain = Blockchain::new();
        let tx = Transaction::new("Alice", "Bob", 50.0, 6.0);
        blockchain.add_transaction(tx);
        blockchain.mine_block("Miner");

        assert_eq!(blockchain.chain.len(), 2);
        assert!(blockchain.is_chain_valid());
    }
}
