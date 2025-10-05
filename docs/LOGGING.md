
# Logging in SecureSMS

This project uses Python `logging` with:
- **Rotating file logs** (default `logs/app.log` created by existing code)
- **Structured JSON logs** at `logs/structured.jsonl` (added by `app/logging_setup.py`)
- **Audit logs** at `logs/audit.log` for security-relevant events

## Environment Variables

- `LOG_LEVEL` = `DEBUG` | `INFO` | `WARNING` (default: `INFO`)
- `LOG_TO_CONSOLE` = `true|false` (default: `false`)

## Request Correlation

A unique `request_id` is attached to each request and emitted in logs, making it easy to trace the lifecycle of a request across entries.

## Shipping Logs to ELK (Optional)

A sample `deploy/filebeat.yml` is provided to ship `logs/*.log` and `logs/structured.jsonl` to Elasticsearch/Kibana. This is **optional** and does not affect runtime.
