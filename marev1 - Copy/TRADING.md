# Marev1 Trading System Documentation

## Overview

Marev1 now includes a **Decentralized Exchange (DEX)** with order matching, market data, and balance management.

## Components

### 1. Order Book (`orderbook.rs`)
Manages buy and sell orders with automatic matching.

**Key Features:**
- Order placement (Buy/Sell)
- Automatic price matching
- Order tracking and execution
- Market data (bid, ask, spread, price)

**Order Structure:**
```rust
pub struct Order {
    pub id: u64,
    pub order_type: OrderType,    // Buy or Sell
    pub trader: String,
    pub amount: f64,              // Quantity in MAREV
    pub price: f64,               // Price per MAREV
    pub timestamp: u64,
    pub filled: f64,              // Amount filled
}
```

### 2. Exchange (`exchange.rs`)
Manages traders, deposits, withdrawals, and balance tracking.

**Key Features:**
- Trader registration
- Balance management (deposits/withdrawals)
- Order placement with automatic matching
- Market price tracking
- Order history

### 3. Trading Features

#### Order Types
- **Buy Order** - Trader wants to purchase MAREV tokens
- **Sell Order** - Trader wants to sell MAREV tokens

#### Matching Algorithm
Orders are matched based on:
1. **Price Priority** - Best prices first (highest bids, lowest asks)
2. **Time Priority** - Earlier orders first (FIFO)

#### Fee Structure
- **6% transaction fee** on all matched trades
- Fee is deducted from buyer's balance
- Applied automatically on order placement

## Usage Examples

### Register a Trader
```rust
let mut exchange = Exchange::new();
let address = exchange.register_trader("Alice");
```

### Deposit Funds
```rust
exchange.deposit("Alice", 10000.0);  // Deposit 10,000 MAREV
```

### Place Buy Order
```rust
match exchange.place_buy_order("Alice", 100.0, 50.0) {
    Ok(order_id) => println!("Buy order placed: {}", order_id),
    Err(e) => println!("Error: {}", e),
}
// Purchases 100 MAREV @ 50.0 MAREV each = 5,000 MAREV
// With 6% fee = 5,300 MAREV total deducted
```

### Place Sell Order
```rust
match exchange.place_sell_order("Bob", 100.0, 45.0) {
    Ok(order_id) => println!("Sell order placed: {}", order_id),
    Err(e) => println!("Error: {}", e),
}
// Sells 100 MAREV @ 45.0 MAREV each
```

### Get Market Data
```rust
// Last traded price
if let Some(price) = exchange.get_market_price() {
    println!("Last price: {}", price);
}

// Bid and Ask
let (bid, ask) = exchange.get_bid_ask();

// Spread
if let Some(spread) = exchange.get_spread() {
    println!("Spread: {}", spread);
}

// Check balance
let balance = exchange.get_balance("Alice").unwrap_or(0.0);
```

## Order Matching Example

**Step 1: Alice places buy order**
```
Buy Order #1: 100 MAREV @ 50.0
Alice's balance: 10,000 - 5,300 = 4,700 MAREV (5,300 held for order)
```

**Step 2: Bob places sell order**
```
Sell Order #2: 100 MAREV @ 45.0
Price match: 50.0 >= 45.0 ✓
Trade executed at 45.0 (seller's price)

Alice receives: 100 MAREV tokens
Bob receives: 4,500 MAREV (100 * 45.0)
Fee: 300 MAREV (6% of 5,000)
```

**Step 3: Market State**
```
Last traded price: 45.0 MAREV
Best bid: 55.0 (from Charlie's buy order)
Best ask: None (all sell orders filled)
Spread: N/A
```

## Fee Structure

### Transaction Fees
- **Base fee:** 6% on transaction value
- **Applied to:** Buyer at order placement
- **Collected:** Held in order escrow

### Example Calculation
```
Trade: 100 tokens @ 50.0 each
Transaction value: 100 * 50.0 = 5,000 MAREV
Fee (6%): 5,000 * 0.06 = 300 MAREV
Total deducted: 5,000 + 300 = 5,300 MAREV
```

## Market Data APIs

### Get Market Price
```rust
exchange.get_market_price() -> Option<f64>
```
Returns the average price of all executed trades.

### Get Best Bid
```rust
exchange.order_book.get_best_bid() -> Option<f64>
```
Returns the highest buy order price.

### Get Best Ask
```rust
exchange.order_book.get_best_ask() -> Option<f64>
```
Returns the lowest sell order price.

### Get Bid-Ask Spread
```rust
exchange.get_spread() -> Option<f64>
```
Returns the difference between best ask and best bid.

## Order States

1. **Open** - Order is active and waiting for matches
2. **Partially Filled** - Part of the order has been matched
3. **Completely Filled** - Order is fully executed

## Limitations & Future Enhancements

### Current Version (0.1.0)
- ✅ Basic order matching
- ✅ Market data tracking
- ✅ 6% fee system
- ✅ Trader balance management

### Planned Features
- [ ] Order cancellation
- [ ] Partial order fills
- [ ] Order history/audit trail
- [ ] Advanced order types (limit, stop-loss, etc.)
- [ ] WebSocket real-time updates
- [ ] REST API for trading
- [ ] Margin trading
- [ ] Shorting

## Running the Trading Demo

```bash
cargo run
```

This executes the demo which:
1. Creates a blockchain with sample transactions
2. Initializes the exchange with 3 traders
3. Deposits initial balances
4. Places buy/sell orders
5. Shows market data and final balances

## Testing

Run unit tests:
```bash
cargo test --lib
```

## Architecture

```
Exchange (Main Trading Interface)
├── OrderBook (Order Management)
│   ├── Buy Orders (Sorted by price/time)
│   ├── Sell Orders (Sorted by price/time)
│   └── Trade History
├── Wallets (Balance Tracking)
│   └── User Balances
└── Transaction History
```

## Security Considerations

1. **Balance Verification** - Orders verify sufficient balance before placement
2. **Atomic Execution** - Trades execute atomically (all-or-nothing)
3. **Immutable History** - Transaction history cannot be modified
4. **Fee Escrow** - Fees are held during order matching

## Performance Notes

- Order matching: O(n*m) where n=buy orders, m=sell orders
- Balance lookup: O(1) hash map access
- Current implementation suitable for ~10,000 orders
- For production, consider Redis orderbook

## Contact & Support

For questions or contributions, refer to the main README.md and DEPLOYMENT.md files.
