mod webserver;

use webserver::WebServer;

fn main() {
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║         MAREV1 DEX - WEB INTERFACE WITH METAMASK        ║");
    println!("╚══════════════════════════════════════════════════════════╝");
    
    let server = WebServer::new(8080);
    server.start();
}
