import subprocess

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
cmd = [edge_path, "--headless=new", "--disable-gpu", "--dump-dom", "http://localhost:5173/"]
res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

root_idx = res.stdout.find('id="root"')
if root_idx != -1:
    print("Found #root:")
    print(res.stdout[root_idx:root_idx+1000])
else:
    print("No #root found!")
