import os
import re

search_terms = ["admin@example.com", "admin_test@example.com", "admin_login", "insert_admin", "insert", "seed"]
workspace = r"c:\Users\user\Downloads\infosys40"

results = []
for root, dirs, files in os.walk(workspace):
    if ".venv" in root or ".git" in root or "__pycache__" in root or ".pytest_cache" in root:
        continue
    for file in files:
        if file.endswith((".py", ".json", ".txt", ".md", ".sh", ".sql")):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                for idx, line in enumerate(lines):
                    for term in search_terms:
                        if term in line:
                            results.append(f"{path}:{idx+1}: {line.strip()}")
            except Exception as e:
                pass

with open(r"c:\Users\user\Downloads\infosys40\infosys 3\scratch\search_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print(f"Done. Found {len(results)} matches.")
