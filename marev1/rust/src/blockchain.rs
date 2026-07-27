use crate::block::Block;
use crate::storage::ensure_parent_dir;
use crate::transaction::Transaction;
use crate::wallet::Wallet;
use serde::{Deserialize, Serialize};
use std::fs;
use std::io;
use std::path::Path;

const SYSTEM_ADDRESS: &str = "SYSTEM";

#[derive(Debug, Serialize, Deserialize)]
pub struct Blockchain {
    pub chain: Vec<Block>,
    pub pending_transactions: Vec<Transaction>,
    pub difficulty: usize,
    pub mining_reward: f64,
    pub coin_name: String,
    pub coin_symbol: String,
    pub total_supply: f64,
}

impl Blockchain {
    pub fn new() -> Self {
        let treasury = Wallet::new("Treasury");
        Self::new_with_genesis("Mare Coin", "MARE", 1_000_000.0, &treasury.address)
    }

    pub fn new_with_genesis(
        coin_name: &str,
        coin_symbol: &str,
        total_supply: f64,
        founder_address: &str,
    ) -> Self {
        let genesis_tx = Transaction::new(SYSTEM_ADDRESS, founder_address, total_supply, 0.0);
        let genesis = Block::new(0, vec![genesis_tx], "0".to_string());

        let blockchain = Self {
            chain: vec![genesis],
            pending_transactions: vec![],
            difficulty: 2,
            mining_reward: 10.0,
            coin_name: coin_name.to_string(),
            coin_symbol: coin_symbol.to_string(),
            total_supply,
        };
        blockchain
    }

    pub fn add_transaction(&mut self, transaction: Transaction) -> Result<(), String> {
        self.validate_transaction(&transaction)?;
        self.pending_transactions.push(transaction);
        Ok(())
    }

    pub fn mine_pending(&mut self, miner_address: &str) {
        let fees = self.pending_transactions.iter().map(|tx| tx.fee).sum::<f64>();
        let reward_tx =
            Transaction::new(SYSTEM_ADDRESS, miner_address, self.mining_reward + fees, 0.0);
        self.pending_transactions.push(reward_tx);

        let previous_hash = self.chain.last().map(|b| b.hash.clone()).unwrap();
        let mut block = Block::new(
            self.chain.len() as u64,
            self.pending_transactions.clone(),
            previous_hash,
        );
        block.mine(self.difficulty);

        self.chain.push(block);
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
                    balance -= tx.total();
                }
            }
        }

        balance
    }

    pub fn get_available_balance(&self, address: &str) -> f64 {
        let mut balance = self.get_balance(address);

        for tx in &self.pending_transactions {
            if tx.to == address {
                balance += tx.amount;
            }

            if tx.from == address {
                balance -= tx.total();
            }
        }

        balance
    }

    pub fn save_to_file<P: AsRef<Path>>(&self, path: P) -> io::Result<()> {
        let path = path.as_ref();
        ensure_parent_dir(path)?;
        let json = serde_json::to_string_pretty(self)
            .map_err(|error| io::Error::new(io::ErrorKind::InvalidData, error))?;
        fs::write(path, json)
    }

    pub fn load_from_file<P: AsRef<Path>>(path: P) -> io::Result<Self> {
        let json = fs::read_to_string(path)?;
        let blockchain = serde_json::from_str::<Self>(&json)
            .map_err(|error| io::Error::new(io::ErrorKind::InvalidData, error))?;

        if !blockchain.is_valid() {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                "saved blockchain failed validation",
            ));
        }

        Ok(blockchain)
    }

    pub fn is_valid(&self) -> bool {
        for i in 1..self.chain.len() {
            let current = &self.chain[i];
            let previous = &self.chain[i - 1];

            if current.hash != current.calculate_hash() {
                return false;
            }

            if current.previous_hash != previous.hash {
                return false;
            }
        }

        if let Some(genesis) = self.chain.first() {
            if genesis.transactions.len() != 1 {
                return false;
            }

            let tx = &genesis.transactions[0];
            if tx.from != SYSTEM_ADDRESS || tx.amount != self.total_supply {
                return false;
            }
        }

        true
    }

    fn validate_transaction(&self, transaction: &Transaction) -> Result<(), String> {
        if transaction.from == SYSTEM_ADDRESS {
            return Err("system transactions can only be created during genesis or mining".into());
        }

        if transaction.from.trim().is_empty() || transaction.to.trim().is_empty() {
            return Err("from and to addresses must be present".into());
        }

        if transaction.amount <= 0.0 {
            return Err("transaction amount must be greater than zero".into());
        }

        let available_balance = self.get_available_balance(&transaction.from);
        if available_balance < transaction.total() {
            return Err(format!(
                "insufficient funds: available {:.2}, required {:.2}",
                available_balance,
                transaction.total()
            ));
        }

        Ok(())
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
    use std::fs;
    use std::path::PathBuf;

    fn test_file(name: &str) -> PathBuf {
        std::env::temp_dir().join(format!("marev1-{name}-{}.json", std::process::id()))
    }

    #[test]
    fn creates_blockchain() {
        let chain = Blockchain::new();
        let treasury = Wallet::new("Treasury");
        assert_eq!(chain.chain.len(), 1);
        assert_eq!(chain.coin_symbol, "MARE");
        assert_eq!(chain.get_balance(&treasury.address), 1_000_000.0);
        assert!(chain.is_valid());
    }

    #[test]
    fn mines_block() {
        let mut chain = Blockchain::new_with_genesis("Mare Coin", "MARE", 250.0, "Alice");
        chain
            .add_transaction(Transaction::new("Alice", "Bob", 25.0, 6.0))
            .unwrap();
        chain.mine_pending("Miner");
        assert_eq!(chain.chain.len(), 2);
        assert_eq!(chain.get_balance("Bob"), 25.0);
        assert_eq!(chain.get_balance("Miner"), 11.5);
        assert!(chain.is_valid());
    }

    #[test]
    fn rejects_overspending() {
        let mut chain = Blockchain::new_with_genesis("Mare Coin", "MARE", 50.0, "Alice");
        let result = chain.add_transaction(Transaction::new("Alice", "Bob", 100.0, 1.0));
        assert!(result.is_err());
    }

    #[test]
    fn saves_and_loads_chain() {
        let path = test_file("save-load");
        let mut chain = Blockchain::new_with_genesis("Mare Coin", "MARE", 250.0, "Alice");
        chain
            .add_transaction(Transaction::new("Alice", "Bob", 25.0, 2.0))
            .unwrap();
        chain.mine_pending("Miner");

        chain.save_to_file(&path).unwrap();
        let loaded = Blockchain::load_from_file(&path).unwrap();

        assert_eq!(loaded.coin_symbol, "MARE");
        assert_eq!(loaded.chain.len(), 2);
        assert_eq!(loaded.get_balance("Bob"), 25.0);
        assert!(loaded.pending_transactions.is_empty());
        assert!(loaded.is_valid());

        let _ = fs::remove_file(path);
    }
}
