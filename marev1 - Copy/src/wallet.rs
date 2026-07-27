use sha2::{Sha256, Digest};

pub struct Wallet {
    pub owner: String,
    pub address: String,
    pub balance: f64,
}

impl Wallet {
    pub fn new(owner: &str) -> Self {
        let address = Self::generate_address(owner);
        
        Wallet {
            owner: owner.to_string(),
            address,
            balance: 1000.0, // Initial balance
        }
    }

    fn generate_address(owner: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(owner.as_bytes());
        format!("0x{}", hex::encode(hasher.finalize())[..40].to_string())
    }

    pub fn send(&mut self, amount: f64, fee: f64) -> bool {
        if self.balance >= amount + fee {
            self.balance -= amount + fee;
            true
        } else {
            false
        }
    }

    pub fn receive(&mut self, amount: f64) {
        self.balance += amount;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_wallet_creation() {
        let wallet = Wallet::new("Alice");
        assert_eq!(wallet.owner, "Alice");
        assert_eq!(wallet.balance, 1000.0);
        assert!(wallet.address.starts_with("0x"));
    }

    #[test]
    fn test_send_sufficient_balance() {
        let mut wallet = Wallet::new("Alice");
        assert!(wallet.send(100.0, 6.0));
        assert_eq!(wallet.balance, 894.0);
    }

    #[test]
    fn test_send_insufficient_balance() {
        let mut wallet = Wallet::new("Alice");
        assert!(!wallet.send(2000.0, 120.0));
        assert_eq!(wallet.balance, 1000.0);
    }
}
