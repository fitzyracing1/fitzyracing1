use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Clone, Debug)]
pub struct Transaction {
    pub from: String,
    pub to: String,
    pub amount: f64,
    pub fee: f64,
    pub timestamp: u64,
}

impl Transaction {
    pub fn new(from: &str, to: &str, amount: f64, fee_percentage: f64) -> Self {
        let fee = amount * (fee_percentage / 100.0);
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        
        Transaction {
            from: from.to_string(),
            to: to.to_string(),
            amount,
            fee,
            timestamp,
        }
    }

    pub fn total_amount(&self) -> f64 {
        self.amount + self.fee
    }

    pub fn to_string_repr(&self) -> String {
        format!("{}->{}:{}", self.from, self.to, self.amount)
    }
}
