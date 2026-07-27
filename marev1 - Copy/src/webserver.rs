use std::net::{TcpListener, TcpStream};
use std::io::{Read, Write};
use std::fs;

pub struct WebServer {
    port: u16,
}

impl WebServer {
    pub fn new(port: u16) -> Self {
        WebServer { port }
    }

    pub fn start(&self) {
        let address = format!("127.0.0.1:{}", self.port);
        let listener = TcpListener::bind(&address).unwrap();
        
        println!("\n🌐 Marev1 Web Interface");
        println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        println!("✓ Server running at: http://{}", address);
        println!("✓ MetaMask integration ready");
        println!("✓ Press Ctrl+C to stop");
        println!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

        for stream in listener.incoming() {
            match stream {
                Ok(stream) => {
                    self.handle_connection(stream);
                }
                Err(e) => {
                    eprintln!("Connection error: {}", e);
                }
            }
        }
    }

    fn handle_connection(&self, mut stream: TcpStream) {
        let mut buffer = [0; 1024];
        stream.read(&mut buffer).unwrap();

        let request = String::from_utf8_lossy(&buffer);
        let request_line = request.lines().next().unwrap_or("");

        let (status_line, content) = if request_line.starts_with("GET / ") {
            let contents = fs::read_to_string("web/index.html")
                .unwrap_or_else(|_| self.get_default_html());
            ("HTTP/1.1 200 OK", contents)
        } else {
            ("HTTP/1.1 404 NOT FOUND", "<h1>404 Not Found</h1>".to_string())
        };

        let response = format!(
            "{}\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: {}\r\n\r\n{}",
            status_line,
            content.len(),
            content
        );

        stream.write_all(response.as_bytes()).unwrap();
        stream.flush().unwrap();
    }

    fn get_default_html(&self) -> String {
        r#"<!DOCTYPE html>
<html><head><title>Marev1 DEX</title></head>
<body><h1>Marev1 DEX</h1><p>Web interface not found. Please ensure web/index.html exists.</p></body>
</html>"#.to_string()
    }
}
