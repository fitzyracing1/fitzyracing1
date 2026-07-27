use std::collections::HashMap;
use sha2::{Sha256, Digest};

pub struct Web3Bridge {
    accounts: HashMap<String, String>, // MetaMask address -> Internal address
    balances: HashMap<String, f64>,
    nonces: HashMap<String, u64>,
}

impl Web3Bridge {
    pub fn new() -> Self {
        Web3Bridge {
            accounts: HashMap::new(),
            balances: HashMap::new(),
            nonces: HashMap::new(),
        }
    }

    /// Connect a MetaMask wallet address
    pub fn connect_wallet(&mut self, metamask_address: &str) -> Result<String, String> {
        if !self.is_valid_ethereum_address(metamask_address) {
            return Err("Invalid Ethereum address".to_string());
        }

        // Generate internal Marev1 address from MetaMask address
        let internal_address = self.derive_internal_address(metamask_address);
        
        self.accounts.insert(metamask_address.to_string(), internal_address.clone());
        self.balances.insert(metamask_address.to_string(), 0.0);
        self.nonces.insert(metamask_address.to_string(), 0);

        Ok(internal_address)
    }

    /// Check if Ethereum address is valid (0x + 40 hex chars)
    fn is_valid_ethereum_address(&self, address: &str) -> bool {
        if !address.starts_with("0x") {
            return false;
        }
        if address.len() != 42 {
            return false;
        }
        address[2..].chars().all(|c| c.is_ascii_hexdigit())
    }

    /// Derive internal Marev1 address from MetaMask address
    fn derive_internal_address(&self, metamask_address: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(format!("marev1:{}", metamask_address).as_bytes());
        format!("0x{}", hex::encode(hasher.finalize())[..40].to_string())
    }

    /// Get internal address for a MetaMask address
    pub fn get_internal_address(&self, metamask_address: &str) -> Option<String> {
        self.accounts.get(metamask_address).cloned()
    }

    /// Get balance for MetaMask address
    pub fn get_balance(&self, metamask_address: &str) -> Option<f64> {
        self.balances.get(metamask_address).copied()
    }

    /// Update balance
    pub fn set_balance(&mut self, metamask_address: &str, balance: f64) -> bool {
        if self.accounts.contains_key(metamask_address) {
            self.balances.insert(metamask_address.to_string(), balance);
            true
        } else {
            false
        }
    }

    /// Get and increment nonce
    pub fn get_next_nonce(&mut self, metamask_address: &str) -> Option<u64> {
        if let Some(nonce) = self.nonces.get_mut(metamask_address) {
            let current = *nonce;
            *nonce += 1;
            Some(current)
        } else {
            None
        }
    }

    /// Sign transaction (simplified - in production use proper cryptography)
    pub fn sign_transaction(&self, metamask_address: &str, data: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(format!("{}:{}", metamask_address, data).as_bytes());
        format!("0x{}", hex::encode(hasher.finalize()))
    }

    /// Verify signature (simplified)
    pub fn verify_signature(&self, metamask_address: &str, data: &str, signature: &str) -> bool {
        let expected = self.sign_transaction(metamask_address, data);
        expected == signature
    }

    /// Get all connected accounts
    pub fn get_accounts(&self) -> Vec<String> {
        self.accounts.keys().cloned().collect()
    }

    /// Disconnect wallet
    pub fn disconnect_wallet(&mut self, metamask_address: &str) -> bool {
        if self.accounts.remove(metamask_address).is_some() {
            self.balances.remove(metamask_address);
            self.nonces.remove(metamask_address);
            true
        } else {
            false
        }
    }
}

impl Default for Web3Bridge {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_connect_wallet() {
        let mut bridge = Web3Bridge::new();
        let address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1";
        let result = bridge.connect_wallet(address);
        assert!(result.is_ok());
    }

    #[test]
    fn test_invalid_address() {
        let mut bridge = Web3Bridge::new();
        let result = bridge.connect_wallet("invalid");
        assert!(result.is_err());
    }

    #[test]
    fn test_balance_management() {
        let mut bridge = Web3Bridge::new();
        let address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1";
        bridge.connect_wallet(address).unwrap();
        
        assert_eq!(bridge.get_balance(address), Some(0.0));
        bridge.set_balance(address, 1000.0);
        assert_eq!(bridge.get_balance(address), Some(1000.0));
    }
}
