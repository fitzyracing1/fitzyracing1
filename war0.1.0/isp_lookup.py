import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests


def fetch_from_ipapi(ip: str = "") -> Dict[str, Any]:
    base = "https://ipapi.co"
    url = f"{base}/json/" if not ip else f"{base}/{ip}/json/"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("reason", "ipapi error"))
    # Normalize keys
    return {
        "source": "ipapi",
        "ip": data.get("ip"),
        "isp": data.get("org") or data.get("asn"),
        "city": data.get("city"),
        "region": data.get("region"),
        "country": data.get("country_name") or data.get("country"),
        "lat": data.get("latitude"),
        "lon": data.get("longitude"),
    }


def fetch_from_ip_api(ip: str = "") -> Dict[str, Any]:
    base = "http://ip-api.com"
    url = f"{base}/json" if not ip else f"{base}/json/{ip}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    if str(data.get("status")).lower() != "success":
        raise RuntimeError(data.get("message", "ip-api error"))
    return {
        "source": "ip-api",
        "ip": data.get("query"),
        "isp": data.get("isp") or data.get("org") or data.get("as"),
        "city": data.get("city"),
        "region": data.get("regionName") or data.get("region"),
        "country": data.get("country"),
        "lat": data.get("lat"),
        "lon": data.get("lon"),
    }


def fetch_ip_info(ip: str = "", provider: str = "auto") -> Dict[str, Any]:
    if provider == "ipapi":
        return fetch_from_ipapi(ip)
    if provider in {"ip-api", "ipapi"}:  # allow minor aliasing
        if provider == "ip-api":
            return fetch_from_ip_api(ip)
        return fetch_from_ipapi(ip)
    # auto: try ipapi then ip-api
    try:
        return fetch_from_ipapi(ip)
    except Exception:
        return fetch_from_ip_api(ip)


def summarize(data: Dict[str, Any]) -> str:
    ip = data.get("ip") or "unknown"
    isp = data.get("isp") or "unknown"
    city = data.get("city") or ""
    region = data.get("region") or ""
    country = data.get("country") or ""
    lat = data.get("lat")
    lon = data.get("lon")

    location_parts = [part for part in [city, region, country] if part]
    location = ", ".join(location_parts) if location_parts else "unknown location"
    coords = f" ({lat}, {lon})" if lat is not None and lon is not None else ""
    src = data.get("source")
    src_txt = f" via {src}" if src else ""
    return f"IP: {ip} | ISP: {isp} | Location: {location}{coords}{src_txt}"


def _save_results(
    results: list[Dict[str, Any]], output_file: str, format_type: str
) -> None:
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    if format_type == "json":
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
    elif format_type == "csv":
        if not results:
            return
        keys = results[0].keys()
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Results saved to {output_file}")


def run_lookup(
    ip: str,
    repeat: int,
    delay: float,
    provider: str,
    watch: bool = False,
    output_file: Optional[str] = None,
    output_format: str = "text",
) -> None:
    results: list[Dict[str, Any]] = []
    iteration = 0
    try:
        while True:
            iteration += 1
            try:
                data = fetch_ip_info(ip, provider)
                summary = summarize(data)
                print(summary)
                if output_format in {"csv", "json"}:
                    results.append(data)
            except Exception as exc:  # noqa: BLE001
                print(f"Lookup failed: {exc}")
            if not watch and iteration >= repeat:
                break
            if watch:
                print(f"[Watch mode: iteration {iteration}. Press Ctrl+C to stop.]")
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nLookup interrupted.")
    finally:
        if output_file and results:
            _save_results(results, output_file, output_format)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Look up ISP and approximate geolocation for IP address(es).",
    )
    parser.add_argument(
        "--ip",
        help="Single IP address to query (defaults to your public IP).",
        default="",
    )
    parser.add_argument(
        "--file",
        help="Path to file with one IP per line to batch query.",
        default="",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to repeat the lookup.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds to wait between repeated lookups.",
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "ipapi", "ip-api"],
        default="auto",
        help="Data source to use (default auto with fallback).",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Enable watch mode: repeat indefinitely until Ctrl+C.",
    )
    parser.add_argument(
        "--output",
        help="Save results to file (csv or json format based on extension).",
        default="",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    repeat = max(1, args.repeat)
    delay = max(0.0, args.delay)

    # Determine output format from file extension
    output_format = "text"
    if args.output:
        if args.output.endswith(".json"):
            output_format = "json"
        elif args.output.endswith(".csv"):
            output_format = "csv"

    # Process batch file or single IP
    if args.file:
        try:
            with open(args.file, "r") as f:
                ips = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(ips)} IP(s) from {args.file}")
            for ip in ips:
                print(f"\n--- Querying {ip} ---")
                run_lookup(
                    ip,
                    repeat,
                    delay,
                    args.provider,
                    args.watch,
                    args.output,
                    output_format,
                )
        except FileNotFoundError:
            print(f"Error: file '{args.file}' not found.")
            sys.exit(1)
    else:
        run_lookup(
            args.ip,
            repeat,
            delay,
            args.provider,
            args.watch,
            args.output,
            output_format,
        )


if __name__ == "__main__":
    main()
