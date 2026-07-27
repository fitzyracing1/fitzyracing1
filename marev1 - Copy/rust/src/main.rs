use marev1::{Blockchain, Transaction, Wallet};
use std::io;
use std::path::Path;

const CHAIN_PATH: &str = "data/chain.json";

fn main() -> io::Result<()> {
    println!("Mare Coin - Simple Rust Coin Demo");

    let mut chain = if Path::new(CHAIN_PATH).exists() {
        Blockchain::load_from_file(CHAIN_PATH)?
    } else {
        Blockchain::new()
    };
    let treasury = Wallet::new("Treasury");
    let alice = Wallet::new("Alice");
    let bob = Wallet::new("Bob");
    let miner = Wallet::new("Miner-01");

    println!("Coin: {} ({})", chain.coin_name, chain.coin_symbol);
    println!("Treasury: {}", treasury.address);
    println!("Alice: {}", alice.address);
    println!("Bob:   {}", bob.address);
    println!("Miner: {}", miner.address);

    if chain.chain.len() == 1 {
        chain
            .add_transaction(Transaction::new(
                &treasury.address,
                &alice.address,
                250.0,
                1.0,
            ))
            .expect("treasury should be able to fund Alice");
        chain
            .add_transaction(Transaction::new(
                &alice.address,
                &bob.address,
                40.0,
                2.0,
            ))
            .expect("Alice should be able to pay Bob");
        chain.mine_pending(&miner.address);
        chain.save_to_file(CHAIN_PATH)?;
        println!("Saved blockchain to {}", CHAIN_PATH);
    } else {
        println!("Loaded blockchain from {}", CHAIN_PATH);
    }

    println!("Blocks: {}", chain.chain.len());
    println!("Chain valid: {}", chain.is_valid());
    println!("Treasury balance: {:.2}", chain.get_balance(&treasury.address));
    println!("Alice balance: {:.2}", chain.get_balance(&alice.address));
    println!("Bob balance: {:.2}", chain.get_balance(&bob.address));
    println!("Miner balance: {:.2}", chain.get_balance(&miner.address));
    Ok(())
}
