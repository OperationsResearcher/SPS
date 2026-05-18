import time
import urllib.request
import sys

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1/health"

for i in range(1, 21):
    start = time.time()
    try:
        with urllib.request.urlopen(URL, timeout=5) as resp:
            resp.read()
            print(f"{i:02d} OK code={resp.status} sec={time.time() - start:.3f}")
    except Exception as exc:
        print(f"{i:02d} ERR sec={time.time() - start:.3f} {exc}")
    time.sleep(1)
