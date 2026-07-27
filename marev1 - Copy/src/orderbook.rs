#[derive(Clone, Debug, Copy, PartialEq)]
pub enum OrderType {
    Buy,
    Sell,
}

#[derive(Clone, Debug)]
pub struct Order {
    pub id: u64,
    pub order_type: OrderType,
    pub trader: String,
    pub amount: f64,
    pub price: f64,
    pub timestamp: u64,
    pub filled: f64,
}

impl Order {
    pub fn new(id: u64, order_type: OrderType, trader: String, amount: f64, price: f64) -> Self {
        use std::time::{SystemTime, UNIX_EPOCH};
        
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        Order {
            id,
            order_type,
            trader,
            amount,
            price,
            timestamp,
            filled: 0.0,
        }
    }

    pub fn is_complete(&self) -> bool {
        (self.filled - self.amount).abs() < 0.0001
    }

    pub fn remaining(&self) -> f64 {
        self.amount - self.filled
    }
}

pub struct OrderBook {
    buy_orders: Vec<Order>,
    sell_orders: Vec<Order>,
    next_order_id: u64,
    trades: Vec<(Order, Order, f64, f64)>, // (buy_order, sell_order, amount, price)
}

impl OrderBook {
    pub fn new() -> Self {
        OrderBook {
            buy_orders: vec![],
            sell_orders: vec![],
            next_order_id: 1,
            trades: vec![],
        }
    }

    pub fn place_order(&mut self, order_type: OrderType, trader: String, amount: f64, price: f64) -> u64 {
        let order_id = self.next_order_id;
        self.next_order_id += 1;

        let order = Order::new(order_id, order_type, trader, amount, price);

        match order_type {
            OrderType::Buy => {
                self.buy_orders.push(order);
                self.match_orders();
            }
            OrderType::Sell => {
                self.sell_orders.push(order);
                self.match_orders();
            }
        }

        order_id
    }

    fn match_orders(&mut self) {
        // Sort orders by price and timestamp
        self.buy_orders.sort_by(|a, b| {
            if (b.price - a.price).abs() > 0.0001 {
                b.price.partial_cmp(&a.price).unwrap_or(std::cmp::Ordering::Equal)
            } else {
                a.timestamp.cmp(&b.timestamp)
            }
        });

        self.sell_orders.sort_by(|a, b| {
            if (a.price - b.price).abs() > 0.0001 {
                a.price.partial_cmp(&b.price).unwrap_or(std::cmp::Ordering::Equal)
            } else {
                a.timestamp.cmp(&b.timestamp)
            }
        });

        // Match orders
        let mut matched = vec![];
        for (buy_idx, buy_order) in self.buy_orders.iter_mut().enumerate() {
            if buy_order.is_complete() {
                continue;
            }

            for (sell_idx, sell_order) in self.sell_orders.iter_mut().enumerate() {
                if sell_order.is_complete() {
                    continue;
                }

                // Check if prices match
                if buy_order.price >= sell_order.price {
                    let trade_price = sell_order.price; // Take seller's price
                    let trade_amount = buy_order.remaining().min(sell_order.remaining());

                    buy_order.filled += trade_amount;
                    sell_order.filled += trade_amount;

                    matched.push((buy_idx, sell_idx, trade_amount, trade_price));

                    if buy_order.is_complete() {
                        break;
                    }
                }
            }
        }

        // Record trades
        for (buy_idx, sell_idx, amount, price) in matched {
            let buy_order = self.buy_orders[buy_idx].clone();
            let sell_order = self.sell_orders[sell_idx].clone();
            self.trades.push((buy_order, sell_order, amount, price));
        }
    }

    pub fn get_best_bid(&self) -> Option<f64> {
        self.buy_orders
            .iter()
            .filter(|o| !o.is_complete())
            .map(|o| o.price)
            .max_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal))
    }

    pub fn get_best_ask(&self) -> Option<f64> {
        self.sell_orders
            .iter()
            .filter(|o| !o.is_complete())
            .map(|o| o.price)
            .min_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal))
    }

    pub fn get_spread(&self) -> Option<f64> {
        match (self.get_best_bid(), self.get_best_ask()) {
            (Some(bid), Some(ask)) => Some(ask - bid),
            _ => None,
        }
    }

    pub fn get_open_orders(&self, trader: &str, order_type: Option<OrderType>) -> Vec<Order> {
        let mut orders = vec![];

        match order_type {
            Some(OrderType::Buy) => {
                orders.extend(
                    self.buy_orders
                        .iter()
                        .filter(|o| o.trader == trader && !o.is_complete())
                        .cloned(),
                );
            }
            Some(OrderType::Sell) => {
                orders.extend(
                    self.sell_orders
                        .iter()
                        .filter(|o| o.trader == trader && !o.is_complete())
                        .cloned(),
                );
            }
            None => {
                orders.extend(
                    self.buy_orders
                        .iter()
                        .filter(|o| o.trader == trader && !o.is_complete())
                        .cloned(),
                );
                orders.extend(
                    self.sell_orders
                        .iter()
                        .filter(|o| o.trader == trader && !o.is_complete())
                        .cloned(),
                );
            }
        }

        orders
    }

    pub fn get_trades(&self) -> &Vec<(Order, Order, f64, f64)> {
        &self.trades
    }

    pub fn get_market_price(&self) -> Option<f64> {
        if self.trades.is_empty() {
            return None;
        }

        let sum: f64 = self.trades.iter().map(|t| t.3).sum();
        Some(sum / self.trades.len() as f64)
    }
}

impl Default for OrderBook {
    fn default() -> Self {
        Self::new()
    }
}
