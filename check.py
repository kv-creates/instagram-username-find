import os, json, itertools, string, time
import urllib.request, urllib.error

TOKEN = os.environ["GH_TOKEN"]
ALPHABET = string.ascii_lowercase   # add string.digits for 0-9 too
LENGTHS = [3, 4]
MAX_SECONDS = 50 * 60

def names():
    for n in LENGTHS:
        for combo in itertools.product(ALPHABET, repeat=n):
            yield "".join(combo)

def check(name):
    req = urllib.request.Request(
        f"https://api.github.com/users/{name}",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "name-checker",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, int(r.headers.get("X-RateLimit-Remaining", 1))
    except urllib.error.HTTPError as e:
        return e.code, int(e.headers.get("X-RateLimit-Remaining", 1))

state = {"index": 0}
if os.path.exists("state.json"):
    state = json.load(open("state.json"))

start = time.time()
found = []
i = state["index"]

for name in itertools.islice(names(), i, None):
    if time.time() - start > MAX_SECONDS:
        break
    status, remaining = check(name)
    if status == 404:
        found.append(name)
    elif status in (403, 429):
        break          # rate limited, retry this name next run
    i += 1
    if remaining <= 5:
        break

state["index"] = i
json.dump(state, open("state.json", "w"))
if found:
    with open("available.txt", "a") as f:
        f.write("\n".join(found) + "\n")
print(f"Checked up to index {i}, found {len(found)} this run")
if __name__ == "__main__":
    checker = InstagramChecker()
    
    # Read usernames from the environment variable set by GitHub Actions
    # If not set (e.g., running locally), use a default list
    usernames_input = os.getenv('USERNAMES_INPUT', 'instagram, cristiano, free_username_test_123')
    usernames_to_check = [name.strip() for name in usernames_input.split(',') if name.strip()]
    
    print(f"--- Checking {len(usernames_to_check)} usernames ---")
    for name in usernames_to_check:
        status = checker.is_available(name)
        if status is True:
            print(f"✅ {name}: AVAILABLE")
        elif status is False:
            print(f"⛔ {name}: TAKEN")
        else:
            print(f"❓ {name}: ERROR")
