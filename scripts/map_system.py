import os
import re

routes = []
with open("backend/main.py", "r", encoding="utf-8") as f:
    for line in f:
        m = re.search(r"@app\.(get|post|put|delete|patch|websocket)\(\s*[\"']([^\"']+)[\"']", line)
        if m:
            routes.append((m.group(1).upper(), m.group(2)))

print(f"Total Routes ({len(routes)}):")
for r in routes:
    print(f"  {r[0]} {r[1]}")

models = []
with open("backend/models.py", "r", encoding="utf-8") as f:
    for line in f:
        m = re.match(r"class\s+([A-Za-z0-9_]+)\(Base\):", line)
        if m:
            models.append(m.group(1))

print(f"\nSQLAlchemy Models ({len(models)}):")
for m in models:
    print(f"  {m}")

agents = []
for f in os.listdir("agents"):
    if f.endswith("_agent.py") and not f.startswith("__"):
        agents.append(f)

print(f"\nAgents ({len(agents)}):")
for a in agents:
    print(f"  {a}")

frontend_fetches = set()
for root, _, files in os.walk("frontend/src"):
    for f in files:
        if f.endswith(".jsx") or f.endswith(".js"):
            content = open(os.path.join(root, f), "r", encoding="utf-8").read()
            matches = re.findall(r"fetch\(\s*[`\"'](\$?[^`\"'\)]+)[\`\"']", content)
            for match in matches:
                frontend_fetches.add((f, match))

print(f"\nFrontend Fetch Calls ({len(frontend_fetches)}):")
for src, call in sorted(frontend_fetches):
    print(f"  [{src}] {call}")
