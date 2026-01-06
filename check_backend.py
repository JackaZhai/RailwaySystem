import urllib.request
import urllib.error

try:
    print("Checking backend...")
    response = urllib.request.urlopen("http://localhost:8080/api/stations/", timeout=5)
    print(f"Status: {response.status}")
except Exception as e:
    print(f"Failed: {e}")
