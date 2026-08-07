import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if '@app.route("/lesson/<int:lesson_id>")' in line and i > 2500:
        skip = True
    if skip and '@app.route("/complete_lesson' in line:
        skip = False
    if not skip:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Duplicate lesson route removed successfully!")
