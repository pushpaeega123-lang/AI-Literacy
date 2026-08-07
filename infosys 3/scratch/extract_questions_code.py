with open(r"c:\Users\user\Downloads\infosys40\infosys 3\app.py", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

start = -1
for idx, line in enumerate(lines):
    if "def _legacy_get_assessment_questions(" in line:
        start = idx
        break

if start != -1:
    output = []
    for i in range(start, start + 350):
        if i < len(lines):
            output.append(f"{i+1}: {lines[i]}")
    with open(r"c:\Users\user\Downloads\infosys40\infosys 3\scratch\extracted_questions.txt", "w", encoding="utf-8") as out:
        out.writelines(output)
    print("Extracted successfully.")
else:
    print("Function not found.")
