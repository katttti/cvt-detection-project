# Public Access Runbook

This document separates two modes of public access for the Mac mini backend.

## 1. Temporary Sharing Mode

Use this when you want to give a friend or teammate a working external URL right now.

Recommended setup:
- run `cvt-api` on local port `8000`
- run `cvt-ops` on local port `3000`
- expose both with `cloudflared tunnel --url ...`

Properties:
- fast to create
- good for short-term testing
- public URL is a random `trycloudflare.com` subdomain
- not appropriate as the project's long-lived address
- URL can change when the tunnel is recreated

Share format:
- API URL
- Ops URL
- shared API password for `X-Access-Password`
- ops basic auth username and password

## 2. Long-Lived Project Mode

Use this when you want stable public URLs for the whole project.

Recommended setup:
- Cloudflare account
- your own domain
- named Cloudflare Tunnel
- DNS records bound to the named tunnel
- optional Cloudflare Access policies

Recommended hostnames:
- `api.<your-domain>`
- `ops.<your-domain>`

Benefits:
- stable URLs
- easier restart and recovery
- easier to move from one process to another
- safer team sharing than raw passwords in chat

## 3. Current App-Level Auth

The current backend implementation protects public routes like this:

- API server:
  - send `X-Access-Password: <shared password>`
- Ops server:
  - use HTTP Basic auth

Environment variables:
- `CVT_SHARED_PASSWORD`
- `CVT_OPS_USERNAME`

## 4. Commands For Temporary Sharing

Start the two local services:

```bash
CVT_SHARED_PASSWORD="replace-me" \
pm2 start "backend/.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000" \
  --name cvt-api \
  --cwd /Users/katykim/Desktop/Finnect-challenge/cvt-detection-project

CVT_SHARED_PASSWORD="replace-me" \
CVT_OPS_USERNAME="friend" \
pm2 start "backend/.venv/bin/python -m uvicorn backend.app.ops:ops_app --host 127.0.0.1 --port 3000" \
  --name cvt-ops \
  --cwd /Users/katykim/Desktop/Finnect-challenge/cvt-detection-project
```

Create temporary public URLs:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
cloudflared tunnel --url http://127.0.0.1:3000
```

## 5. Commands For Long-Lived URLs

Authenticate cloudflared:

```bash
cloudflared tunnel login
```

Create a named tunnel:

```bash
cloudflared tunnel create cvt-detection
```

Create DNS routes:

```bash
cloudflared tunnel route dns cvt-detection api.your-domain.com
cloudflared tunnel route dns cvt-detection ops.your-domain.com
```

Create config:

```yaml
tunnel: cvt-detection
credentials-file: /Users/katykim/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: api.your-domain.com
    service: http://127.0.0.1:8000
  - hostname: ops.your-domain.com
    service: http://127.0.0.1:3000
  - service: http_status:404
```

Run the named tunnel:

```bash
cloudflared tunnel run cvt-detection
```

## 6. What To Share With The App Developer

For temporary sharing:
- API URL
- API password header name: `X-Access-Password`
- Ops URL
- Ops username
- Ops password

For long-lived sharing:
- stable API URL
- stable ops URL
- same auth values, or migrate to Cloudflare Access
