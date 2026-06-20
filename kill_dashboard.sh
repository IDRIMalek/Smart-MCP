#!/bin/bash
# Kill existing dashboard on port 8050
PID=$(lsof -ti:8050 2>/dev/null)
if [ -n "$PID" ]; then
    kill -9 "$PID" 2>/dev/null
    echo "Killed PID $PID on port 8050"
else
    echo "Nothing on port 8050"
fi