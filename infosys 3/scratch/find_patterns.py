import re

with open(r"c:\Users\user\Downloads\infosys40\infosys 3\app.py", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print("Searching for routes and functions:")
for idx, line in enumerate(lines):
    if "@app.route" in line or "def " in line:
        print(f"Line {idx+1}: {line.strip()}")
