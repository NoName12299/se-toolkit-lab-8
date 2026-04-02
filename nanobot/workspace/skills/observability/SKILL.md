# Observability Skill

You have access to observability tools that can query **VictoriaLogs** and **VictoriaTraces**. Use these tools when users ask about errors, failures, debugging, or system health.

## Available Tools

### Log Tools (VictoriaLogs)

- **`obs_logs_search`** — Search logs using LogsQL queries
  - Use when user asks to "find errors", "search logs", or "what happened"
  - Example query: `_time:10m service.name:"Learning Management Service" severity:ERROR`
  - Time format: `_time:10m` (last 10 minutes), `_time:1h` (last hour)
  - Filter by severity: `severity:ERROR`, `severity:WARN`, `severity:INFO`
  - Filter by service: `service.name:"backend"`

- **`obs_logs_error_count`** — Count errors for a service over a time window
  - Use as a quick check: "any errors in the last hour?"
  - Returns count and time window

### Trace Tools (VictoriaTraces)

- **`obs_traces_list`** — List recent traces for a service
  - Use to find traces for debugging
  - Returns trace IDs that can be used with `obs_traces_get`

- **`obs_traces_get`** — Fetch a specific trace by ID
  - Use when you have a `trace_id` from logs
  - Shows full request flow across services

## Reasoning Flow

When user asks about errors or issues:

1. **Start with `obs_logs_error_count`** — Quick check if there are recent errors
   - Example: "Any LMS backend errors in the last 10 minutes?"
   - Query: service="Learning Management Service", minutes=10

2. **If errors exist, use `obs_logs_search`** — Inspect the actual error messages
   - Look for `trace_id` in the log entries
   - Identify which service/component failed

3. **If you found a trace_id, use `obs_traces_get`** — See the full request flow
   - Shows which spans succeeded/failed
   - Helps identify the root cause

4. **Summarize findings concisely** — Don't dump raw JSON
   - What failed
   - When it happened
   - Which service was affected
   - Any trace information

## Example Queries

**User:** "Any errors in the last hour?"

**You:**
1. Call `obs_logs_error_count` with service="Learning Management Service", minutes=60
2. If count > 0, call `obs_logs_search` to see the errors
3. Summarize: "Found X errors in the last hour. The most recent was... [brief description]"

**User:** "What went wrong with the backend?"

**You:**
1. Call `obs_logs_search` with query: `_time:30m service.name:"Learning Management Service" severity:ERROR`
2. Look for trace_id in results
3. Call `obs_traces_get` with the trace_id
4. Summarize the failure point from the trace

**User:** "Show me recent traces for the backend"

**You:**
1. Call `obs_traces_list` with service="Learning Management Service"
2. Show trace IDs and timestamps
3. Offer to fetch details with `obs_traces_get`

## Tips

- Always specify a time range in logs queries (e.g., `_time:10m`)
- Use narrow time windows for fresh data (10-30 minutes)
- Filter by `service.name` to reduce noise
- Look for `trace_id` in error logs to correlate with traces
- Summarize, don't dump raw JSON responses
