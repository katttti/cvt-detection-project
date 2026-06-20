# App Developer Access Template

Send the following to the app developer after the router forwarding rules are active.

## Current Values

- Public IP: `58.142.28.163`
- API route: `http://58.142.28.163:10808`
- API password header: `X-Access-Password`
- API password: `AHXs1c_pzY-0sLeSio_rg4da`
- Ops route: `http://58.142.28.163:10809`
- Ops username: `friend`
- Ops password: `AHXs1c_pzY-0sLeSio_rg4da`

## Message Template

```text
Backend test access info:

1. API base URL
http://58.142.28.163:10808

2. API auth
Add this header to protected API requests:
X-Access-Password: AHXs1c_pzY-0sLeSio_rg4da

3. Ops URL
http://58.142.28.163:10809

4. Ops auth
Username: friend
Password: AHXs1c_pzY-0sLeSio_rg4da

5. Notes
- API health check: GET /health
- Main scoring endpoint: POST /v1/risk-assessments
- If 10809 does not open yet, the router forwarding rule for 10809 -> 3001 still needs to be added.
```

## Before Sending

Confirm these first:

1. `pm2 status` shows `cvt-api` and `cvt-ops` as `online`
2. Router forwarding for `10808 -> 3000` is active
3. Router forwarding for `10809 -> 3001` is active
4. External test from LTE or another network succeeds
