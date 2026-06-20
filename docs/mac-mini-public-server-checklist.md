# Mac mini Public Server Checklist

This checklist assumes one Mac mini will expose two public services:

1. `api` service for the CVT backend
2. `ops` service for monitoring, admin access, or guardian operations

## Recommended Exposure Pattern

Use this setup for the first deployment:

1. Run both services locally on the Mac mini
2. Keep them alive with `pm2`
3. Expose them with Cloudflare Tunnel
4. Bind each public hostname to a local port

Why this is the safest first choice:
- no router port forwarding
- no dynamic home IP problem
- automatic HTTPS
- easier rollback than opening raw inbound ports

## Step 1: Prepare the Mac mini

Install required tools:

```bash
brew install python@3.12
brew install cloudflared
npm install -g pm2
```

Confirm the tools:

```bash
python3 --version
cloudflared --version
pm2 --version
```

## Step 2: Decide the two local ports

Recommended ports:

- backend API: `127.0.0.1:8000`
- ops service: `127.0.0.1:3000`

Do not expose raw development servers directly to the internet without a tunnel or proxy.

## Step 3: Build the backend service

First backend slice:

1. `POST /v1/pressure-events`
2. `POST /v1/transfer-events`
3. `POST /v1/risk-assessments`
4. `GET /health`

The service should:
- receive the mobile app's `pressure_score`
- receive transfer metadata
- compute a final `risk_score`
- save the result to Supabase

## Step 4: Build the second service

Use the second public endpoint for one of these:

1. admin or monitoring dashboard
2. guardian operations endpoint
3. read-only notification history UI

Recommended first version:
- a simple ops dashboard with health state and recent risk events

## Step 5: Keep both services alive with PM2

Example commands:

```bash
pm2 start "python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000" --name cvt-api
pm2 start "python3 -m http.server 3000 --bind 127.0.0.1" --name cvt-ops
pm2 save
pm2 startup
```

Replace the second example service with the real ops app later.

## Step 6: Create the tunnel

Log into Cloudflare:

```bash
cloudflared tunnel login
```

Create a named tunnel:

```bash
cloudflared tunnel create cvt-detection
```

## Step 7: Map the two public hostnames

Example hostnames:

- `api.your-domain.com` -> `http://127.0.0.1:8000`
- `ops.your-domain.com` -> `http://127.0.0.1:3000`

Create a tunnel config file:

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

## Step 8: Run the tunnel as a service

```bash
cloudflared tunnel route dns cvt-detection api.your-domain.com
cloudflared tunnel route dns cvt-detection ops.your-domain.com
cloudflared service install
```

Then start the tunnel:

```bash
cloudflared tunnel run cvt-detection
```

## Step 9: Verify public access

Check all of these:

1. `https://api.your-domain.com/health` opens externally
2. `https://ops.your-domain.com` opens from mobile data, not only local Wi-Fi
3. PM2 restarts the services after reboot
4. Cloudflare tunnel reconnects after reboot

## Step 10: Add production basics

Before real use, add:

1. request logging
2. rate limiting
3. auth and role checks
4. error tracking
5. backup and restore for Supabase data
6. health alerts for service downtime

## What You Need To Do Next

In order:

1. Finish Supabase MCP browser login
2. Confirm the backend stack choice
3. Create Supabase tables and migrations
4. Scaffold the backend API
5. Add risk scoring logic
6. Expose the API and ops services from the Mac mini
7. Test from an external network
