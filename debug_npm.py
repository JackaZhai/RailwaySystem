import subprocess
import sys
import os

print(f"Platform: {sys.platform}")
use_shell = sys.platform == 'win32'
print(f"Shell: {use_shell}")
print(f"Path: {os.environ.get('PATH')}")

try:
    print("Running npm --version...")
    result = subprocess.run(["npm", "--version"], capture_output=True, check=True, shell=use_shell)
    print("Success!")
    print(result.stdout.decode())
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
