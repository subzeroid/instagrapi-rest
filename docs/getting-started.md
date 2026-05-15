# Getting Started

## Run With Docker Compose

```bash
docker compose up api
```

Open <http://localhost:8000/docs> for Swagger UI.

## Run Locally

```bash
python3.13 -m venv .venv
. .venv/bin/activate
python3.13 -m pip install -U pip
python3.13 -m pip install -e ".[test,docs]"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Create A Session

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=<USERNAME>&password=<PASSWORD>"
```

The response is the session ID. In Swagger UI, click **Authorize** and paste it
once. For direct HTTP calls, send it as `X-Session-ID`:

```bash
curl "http://localhost:8000/user/info/by/username?username=instagram" \
  -H "X-Session-ID: <SESSIONID>"
```

Older clients may still pass `sessionid` in query parameters or form data, but
new integrations should use `X-Session-ID`.

## Check The Service

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/deps
```
