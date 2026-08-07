import os

app_path = r"c:\Users\user\Downloads\infosys40\infosys 3\app.py"
extracted_path = r"c:\Users\user\Downloads\infosys40\infosys 3\scratch\extracted_multilingual_questions.py"

# Read extracted multilingual questions
with open(extracted_path, "r", encoding="utf-8") as f:
    replacement_str = f.read().strip()

# Convert line endings of replacement_str to \r\n to match app.py standard
replacement_str = replacement_str.replace("\r\n", "\n").replace("\n", "\r\n")

# Read current app.py as bytes
with open(app_path, "rb") as f:
    app_data = f.read()

start_marker = b"multilingual_questions = {"
end_marker = b"def _get_assessment_profile(level, age_band):"

start_idx = app_data.find(start_marker)
end_idx = app_data.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Start or end marker not found in app.py")
    exit(1)

# Construct the new code
# We replace the bytes from start_idx up to end_idx with replacement_str as bytes, plus a trailing \r\n\r\n
replacement_bytes = replacement_str.encode("utf-8") + b"\r\n\r\n"

new_app_data = app_data[:start_idx] + replacement_bytes + app_data[end_idx:]

# Backup original app.py
backup_path = app_path + ".bak"
with open(backup_path, "wb") as f:
    f.write(app_data)
print("Backup created at:", backup_path)

# Write modified app.py
with open(app_path, "wb") as f:
    f.write(new_app_data)
print("app.py successfully patched!")
