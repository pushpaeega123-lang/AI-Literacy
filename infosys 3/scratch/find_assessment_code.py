import re

with open(r"c:\Users\user\Downloads\infosys40\infosys 3\app.py", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Find assessment route
matches = re.finditer(r"def\s+\w*assessment\w*\(", content, re.IGNORECASE)
for m in matches:
    start_pos = max(0, m.start() - 100)
    end_pos = min(len(content), m.end() + 2000)
    print(f"Match found at position {m.start()}:")
    print(content[start_pos:end_pos])
    print("-" * 50)

# Also let's search for assessment questions setup or initialization
matches2 = re.finditer(r"questions\s*=\s*\[", content)
for m in matches2:
    start_pos = max(0, m.start() - 100)
    end_pos = min(len(content), m.end() + 1500)
    print(f"Match questions= at position {m.start()}:")
    print(content[start_pos:end_pos])
    print("-" * 50)
