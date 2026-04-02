import urllib.request, urllib.error
try:
    req = urllib.request.Request('https://finparvai.onrender.com/api/dashboard', headers={'User-Agent': 'Mozilla'})
    print(urllib.request.urlopen(req).read().decode())
except urllib.error.HTTPError as e:
    print("HTTP ERROR:")
    print(e.read().decode())
except Exception as e:
    print(e)
