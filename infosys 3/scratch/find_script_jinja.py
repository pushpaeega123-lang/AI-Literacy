import re

with open(r"c:\Users\user\Downloads\infosys 3\infosys 3\templates\dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find all script blocks
script_pattern = re.compile(r"<script\b[^>]*>(.*?)</script>", re.DOTALL)
for match in script_pattern.finditer(content):
    script_content = match.group(1)
    script_start_pos = match.start(1)
    # Count newlines up to script_start_pos to get line numbers
    start_line_no = content[:script_start_pos].count("\n") + 1
    
    # Check for Jinja tags in this script content
    lines = script_content.split("\n")
    for i, line in enumerate(lines):
        line_no = start_line_no + i
        if "{%" in line or "{{" in line:
            print(f"Line {line_no}: {line.strip()}")
