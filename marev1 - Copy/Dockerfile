FROM rust:1.93

WORKDIR /app

COPY Cargo.toml .
COPY src src

RUN cargo build --release

EXPOSE 8080

CMD ["./target/release/marev1"]
