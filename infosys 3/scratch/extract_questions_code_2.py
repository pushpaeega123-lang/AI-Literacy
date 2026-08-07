with open(r"c:\Users\user\Downloads\infosys40\infosys 3\app.py", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

output = []
for i in range(1750, min(2200, len(lines))):
    output.append(f"{i+1}: {lines[i]}")

with open(r"c:\Users\user\Downloads\infosys40\infosys 3\scratch\extracted_questions_2.txt", "w", encoding="utf-8") as out:
    out.writelines(output)
print("Extracted successfully.")
