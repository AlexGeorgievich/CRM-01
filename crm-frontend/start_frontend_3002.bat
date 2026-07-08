@echo off
cd /d "%~dp0"
echo Starting CRM frontend on port 3002 > dev-3002.cmd.log
echo Working directory: %CD% >> dev-3002.cmd.log
where node >> dev-3002.cmd.log 2>&1
where npm >> dev-3002.cmd.log 2>&1
call npm run dev >> dev-3002.cmd.log 2>&1
echo Frontend process exited with code %ERRORLEVEL% >> dev-3002.cmd.log
pause
