# ISP Lookup CLI

Simple Python CLI to detect ISP and approximate geolocation for an IP address. Defaults to your current public IP when no IP is provided.

The tool queries public APIs with automatic fallback:
- Primary: `ipapi.co`
- Fallback: `ip-api.com`

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python isp_lookup.py               # lookup your current IP
python isp_lookup.py --ip 8.8.8.8  # lookup specific IP
python isp_lookup.py --repeat 3 --delay 1
python isp_lookup.py --provider ip-api  # force fallback provider
```

## Notes
- Output includes IP, ISP/organization, city/region/country, and coordinates when available.
- Repeat prints run sequentially with configurable delay.
- Public APIs may rate-limit; provide a specific IP, switch provider with `--provider`, or retry later if you see 429 errors.
