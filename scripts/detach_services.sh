#!/bin/bash

echo "Stopping all kubectl port-forward processes..."

# Find and kill all kubectl port-forward processes
if pgrep -f "kubectl port-forward" > /dev/null; then
    pkill -f "kubectl port-forward"
    echo "✓ All port-forward processes stopped"
else
    echo "✓ No port-forward processes found"
fi

# Wait a moment and verify
sleep 1

# Check if any processes remain
REMAINING=$(ps aux | grep "kubectl port-forward" | grep -v grep | wc -l)
if [ "$REMAINING" -gt 0 ]; then
    echo "⚠ Warning: $REMAINING port-forward process(es) still running"
    echo "Attempting force kill..."
    pkill -9 -f "kubectl port-forward"
    sleep 1
    echo "✓ Force kill completed"
else
    echo "✓ All port forwards successfully terminated"
fi
