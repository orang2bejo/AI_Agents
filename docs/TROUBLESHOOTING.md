# Troubleshooting

## GPU Not Detected
- Ensure CUDA drivers are installed.
- Set `JARVIS_STT_DEVICE=cuda` to force GPU for Whisper.

## Playwright Failures
- Install browsers with `playwright install`.
- Check allowlist and network access.

## Office COM Crashes
- Verify Microsoft Office is installed and updated.
- Run the agent with administrator privileges if required.

## PowerShell Permission Errors
- Constrained Language Mode may block certain cmdlets.
- Ensure commands are in the whitelist and do not require elevated rights.
