import re

with open(r"c:\Users\user\Downloads\infosys40\infosys 3\app.py", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

output = []

# Find assessment route
matches = re.finditer(r"def\s+\w*assessment\w*\(", content, re.IGNORECASE)
for m in matches:
    start_pos = max(0, m.start() - 100)
    end_pos = min(len(content), m.end() + 2000)
    output.append(f"Match found at position {m.start()}:\n")
    output.append(content[start_pos:end_pos])
    output.append("\n" + "-" * 50 + "\n")

# Also let's search for assessment questions setup or initialization
matches2 = re.finditer(r"questions\s*=\s*\[", content)
for m in matches2:
    start_pos = max(0, m.start() - 100)
    end_pos = min(len(content), m.end() + 1500)
    output.append(f"Match questions= at position {m.start()}:\n")
    output.append(content[start_pos:end_pos])
    output.append("\n" + "-" * 50 + "\n")

with open(r"c:\Users\user\Downloads\infosys40\infosys 3\scratch\assessment_code.txt", "w", encoding="utf-8") as f:
    f.write("".join(output))

print("Done writing findings.")
