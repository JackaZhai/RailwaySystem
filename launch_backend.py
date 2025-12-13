#!/usr/bin/env python3
"""
Launch backend server with correct Python path
"""
import os
import sys
import time
import requests
import subprocess
from pathlib import Path

# Get project root
project_root = Path(__file__).parent
backend_dir = project_root / "backend"

print("=" * 60)
print("Launching Railway System Backend Server")
print("=" * 60)

# Check database
print("\n[1] Checking database...")
# We'll check via direct SQLite access
db_path = backend_dir / "db" / "railway.sqlite3"
if db_path.exists():
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM data_management_passengerrecord")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"    Database has {count} passenger records")
else:
    print("    Database file not found")

# Check if server is already running
print("\n[2] Checking if server is already running...")
try:
    response = requests.get("http://localhost:8000/api/analytics/flow/", timeout=2)
    if response.status_code == 200:
        print("    Server is already running!")
        print("\n" + "=" * 60)
        print("Frontend should show data at http://localhost:5173")
        print("If not, refresh the page.")
        sys.exit(0)
except requests.exceptions.ConnectionError:
    print("    Server not running")
except Exception as e:
    print(f"    Error checking: {e}")

# Launch server
print("\n[3] Starting backend server...")
print(f"    Project root: {project_root}")
print(f"    Backend dir: {backend_dir}")

# Set PYTHONPATH
env = os.environ.copy()
env['PYTHONPATH'] = str(project_root) + os.pathsep + env.get('PYTHONPATH', '')

# Build command
cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]

print(f"    Command: {' '.join(cmd)}")
print(f"    Working dir: {backend_dir}")
print("\n    Starting server... (Press Ctrl+C to stop)")

# Start server
try:
    process = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Wait a bit for server to start
    time.sleep(3)

    # Check if server started
    print("\n[4] Testing server startup...")
    try:
        response = requests.get("http://localhost:8000/api/analytics/flow/", timeout=5)
        if response.status_code == 200:
            print("    SUCCESS: Server is responding!")
            data = response.json()
            if isinstance(data, list):
                print(f"    API returned {len(data)} items")
            else:
                print(f"    API returned {type(data).__name__}")

            print("\n" + "=" * 60)
            print("✅ Backend server is running!")
            print("\nYour frontend at http://localhost:5173 should now show data.")
            print("Refresh the page if it was already open.")
            print("\nServer output will be shown below...")
            print("=" * 60 + "\n")

            # Print server output
            for line in process.stdout:
                print(line.rstrip())

        else:
            print(f"    Server responded with HTTP {response.status_code}")
            print("\nStopping server...")
            process.terminate()
            sys.exit(1)

    except requests.exceptions.ConnectionError:
        print("    ERROR: Server not responding after 3 seconds")
        print("\nServer output:")
        # Print any output so far
        for line in process.stdout:
            print(line.rstrip())
        print("\nStopping server...")
        process.terminate()
        sys.exit(1)

except KeyboardInterrupt:
    print("\n\nStopping server...")
    if 'process' in locals():
        process.terminate()
    sys.exit(0)
except Exception as e:
    print(f"\nERROR: {e}")
    sys.exit(1)