```markdown
## Healthcheck
Run a quick system check:

```bash
python scripts/healthcheck.py
```

Expected output:
```json
{
  "cpu_percent": 12.5,
  "mem_percent": 43.2
}
```
- **cpu_percent** – overall CPU usage
- **mem_percent** – RAM usage
Values consistently above 80% indicate resource pressure.
```
