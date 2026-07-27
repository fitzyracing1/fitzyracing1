use std::collections::HashMap;
use crate::orderbook::{OrderBook, OrderType};
use crate::wallet::Wallet;
use crate::transaction::Transaction;

pub struct Exchange {
    order_book: OrderBook,
    wallets: HashMap<String, Wallet>,
    transaction_history: Vec<Transaction>,
}

impl Exchange {
    pub fn new() -> Self {
        Exchange {
            order_book: OrderBook::new(),
            wallets: HashMap::new(),
            transaction_history: vec![],
        }
    }

    pub fn register_trader(&mut self, name: &str) -> String {
        let wallet = Wallet::new(name);
        let address = wallet.address.clone();
        self.wallets.insert(name.to_string(), wallet);
        address
    }

    pub fn get_balance(&self, trader: &str) -> Option<f64> {
        self.wallets.get(trader).map(|w| w.balance)
    }

    pub fn deposit(&mut self, trader: &str, amount: f64) -> bool {
        if let Some(wallet) = self.wallets.get_mut(trader) {
            wallet.balance += amount;
            true
        } else {
            false
        }
    }

    pub fn place_buy_order(&mut self, trader: &str, amount: f64, price: f64) -> Result<u64, String> {
        let total_cost = amount * price * 1.06; // Include 6% fee

        if let Some(wallet) = self.wallets.get(trader) {
            if wallet.balance < total_cost {
                return Err("Insufficient balance".to_string());
            }
        } else {
            return Err("Trader not found".to_string());
        }

        // Deduct balance (hold for order)
        if let Some(wallet) = self.wallets.get_mut(trader) {
            wallet.balance -= total_cost;
        }

        let order_id = self.order_book.place_order(OrderType::Buy, trader.to_string(), amount, price);
        
        // Process any matched trades
        self.process_trades();

        Ok(order_id)
    }

    pub fn place_sell_order(&mut self, trader: &str, amount: f64, price: f64) -> Result<u64, String> {
        if self.wallets.get(trader).is_none() {
            return Err("Trader not found".to_string());
        }

        // TODO: Verify trader has tokens to sell

        let order_id = self.order_book.place_order(OrderType::Sell, trader.to_string(), amount, price);
        
        // Process any matched trades
        self.process_trades();

        Ok(order_id)
    }

    fn process_trades(&mut self) {
        // Get completed trades and process them
        let trades = self.order_book.get_trades().clone();
        
        for (buy_order, sell_order, amount, price) in trades {
            let transaction = Transaction::new(
                &sell_order.trader,
                &buy_order.trader,
                amount,
                6.0, // 6% fee
            );
            self.transaction_history.push(transaction);

            // Update balances
            if let Some(buyer_wallet) = self.wallets.get_mut(&buy_order.trader) {
                buyer_wallet.balance += amount; // Add tokens
            }

            if let Some(seller_wallet) = self.wallets.get_mut(&sell_order.trader) {
                seller_wallet.balance += price * amount; // Add cash
            }
        }
    }

    pub fn get_market_price(&self) -> Option<f64> {
        self.order_book.get_market_price()
    }

    pub fn get_bid_ask(&self) -> (Option<f64>, Option<f64>) {
        (self.order_book.get_best_bid(), self.order_book.get_best_ask())
    }

    pub fn get_spread(&self) -> Option<f64> {
        self.order_book.get_spread()
    }

    pub fn get_order_book_depth(&self) -> (usize, usize) {
        // Returns (buy_orders, sell_orders)
        (0, 0) // TODO: Implement
    }

    pub fn get_trader_orders(&self, trader: &str) -> Vec<String> {
        let orders = self.order_book.get_open_orders(trader, None);
        orders
            .iter()
            .map(|o| format!("{:?} {} @ {}", o.order_type, o.amount, o.price))
            .collect()
    }
}

impl Default for Exchange {
    fn default() -> Self {
        Self::new()
    }
}
