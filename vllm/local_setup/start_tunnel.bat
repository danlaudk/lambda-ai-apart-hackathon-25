@echo off
REM SSH Tunnel Script for vLLM Server (Windows)
REM This creates secure tunnels to access the vLLM server from your local computer

echo ================================================================================
echo                     vLLM Server - SSH Tunnel
echo ================================================================================
echo.
echo Creating SSH tunnels to vLLM server...
echo.
echo Server: ubuntu@192.222.53.238
echo.
echo Tunnels:
echo   * Port 8000 -^> vLLM Inference API
echo   * Port 8001 -^> Model Manager API
echo.
echo ================================================================================
echo   IMPORTANT: Keep this window open!
echo ================================================================================
echo.
echo Press Ctrl+C to disconnect
echo.

REM Create SSH tunnel with both ports
ssh -L 8000:localhost:8000 -L 8001:localhost:8001 ubuntu@192.222.53.238

