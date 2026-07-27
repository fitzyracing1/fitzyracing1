use marev1::{Blockchain, Wallet, Transaction, Exchange};

fn main() {
    println!("═══════════════════════════════════════════════════════════════");
    println!("       MAREV1 CRYPTOCURRENCY - BLOCKCHAIN & TRADING DEMO       ");
    println!("═══════════════════════════════════════════════════════════════\n");

    // Part 1: Blockchain Demo
    println!("📦 PART 1: BLOCKCHAIN & MINING\n");
    let mut blockchain = Blockchain::new();
    
    let wallet1 = Wallet::new("Alice");
    let wallet2 = Wallet::new("Bob");
    
    println!("   Wallet 1 - {}: {}", wallet1.owner, wallet1.address);
    println!("   Wallet 2 - {}: {}", wallet2.owner, wallet2.address);
    
    let tx = Transaction::new(
        &wallet1.address,
        &wallet2.address,
        100.0,
        6.0, // 6% fee
    );
    
    println!("\n   ✓ Transaction created:");
    println!("     From:   {}", tx.from);
    println!("     To:     {}", tx.to);
    println!("     Amount: {} MAREV", tx.amount);
    println!("     Fee:    {} MAREV (6%)", tx.fee);
    
    blockchain.add_transaction(tx);
    blockchain.mine_block("Miner Address");
    
    println!("\n   ✓ Block mined successfully");
    println!("   ✓ Blockchain valid: {}", blockchain.is_chain_valid());
    println!("   ✓ Total blocks: {}\n", blockchain.chain.len());

    // Part 2: Exchange & Trading Demo
    println!("═══════════════════════════════════════════════════════════════");
    println!("💱 PART 2: DECENTRALIZED EXCHANGE (DEX)\n");
    
    let mut exchange = Exchange::new();
    
    // Register traders
    println!("   Registering traders...");
    let alice_addr = exchange.register_trader("Alice");
    let bob_addr = exchange.register_trader("Bob");
    let charlie_addr = exchange.register_trader("Charlie");
    
    println!("   ✓ Alice registered: {}", alice_addr);
    println!("   ✓ Bob registered: {}", bob_addr);
    println!("   ✓ Charlie registered: {}\n", charlie_addr);
    
    // Deposit funds
    println!("   Initial deposits:");
    exchange.deposit("Alice", 10000.0);
    exchange.deposit("Bob", 5000.0);
    exchange.deposit("Charlie", 7500.0);
    
    println!("   ✓ Alice: {} MAREV", exchange.get_balance("Alice").unwrap_or(0.0));
    println!("   ✓ Bob: {} MAREV", exchange.get_balance("Bob").unwrap_or(0.0));
    println!("   ✓ Charlie: {} MAREV\n", exchange.get_balance("Charlie").unwrap_or(0.0));
    
    // Place orders
    println!("   Order book activity:");
    
    match exchange.place_buy_order("Alice", 100.0, 50.0) {
        Ok(order_id) => println!("   ✓ Alice placed BUY order #{}: 100 MAREV @ 50.0", order_id),
        Err(e) => println!("   ✗ Error: {}", e),
    }
    
    match exchange.place_sell_order("Bob", 100.0, 45.0) {
        Ok(order_id) => println!("   ✓ Bob placed SELL order #{}: 100 MAREV @ 45.0", order_id),
        Err(e) => println!("   ✗ Error: {}", e),
    }
    
    match exchange.place_buy_order("Charlie", 50.0, 55.0) {
        Ok(order_id) => println!("   ✓ Charlie placed BUY order #{}: 50 MAREV @ 55.0", order_id),
        Err(e) => println!("   ✗ Error: {}", e),
    }
    
    // Market data
    println!("\n   Market data:");
    if let Some(price) = exchange.get_market_price() {
        println!("   ✓ Last traded price: {} MAREV", price);
    }
    
    let (bid, ask) = exchange.get_bid_ask();
    println!("   ✓ Best bid: {}", bid.map(|p| format!("{}", p)).unwrap_or("None".to_string()));
    println!("   ✓ Best ask: {}", ask.map(|p| format!("{}", p)).unwrap_or("None".to_string()));
    
    if let Some(spread) = exchange.get_spread() {
        println!("   ✓ Bid-ask spread: {}", spread);
    }
    
    // Final balances
    println!("\n   Final balances:");
    println!("   ✓ Alice: {} MAREV", exchange.get_balance("Alice").unwrap_or(0.0));
    println!("   ✓ Bob: {} MAREV", exchange.get_balance("Bob").unwrap_or(0.0));
    println!("   ✓ Charlie: {} MAREV", exchange.get_balance("Charlie").unwrap_or(0.0));
    
    println!("\n═══════════════════════════════════════════════════════════════");
    println!("   ✓ Demo complete! Blockchain & Trading systems operational");
    println!("═══════════════════════════════════════════════════════════════\n");
}
