import requests
url = "http://localhost:8000/api/ingest/document"
files = {'file': ('test.txt', b'Vendor: Alpha Traders\nAmount: 5000\nType: invoice')}
response = requests.post(url, files=files)
data = response.json()
print("Persisted As:", data.get('persisted_as'))
print(data)

# Test dashboard data fetching to make sure the app isn't crashing
dash = requests.get("http://localhost:8000/api/dashboard")
print("\nDashboard Status:", dash.status_code)
print("Total Payables:", dash.json().get('total_payables'))
