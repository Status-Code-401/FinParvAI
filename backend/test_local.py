from fastapi.testclient import TestClient
from main import app
import sys

client = TestClient(app)
try:
    response = client.get("/api/dashboard")
    print("STATUS:", response.status_code)
    print("BODY:", response.json())
except Exception as e:
    import traceback
    traceback.print_exc()
