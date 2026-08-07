import os

replacements = {
    '<th>Name</th>': '<th>{{ translations.full_name or \'Name\' }}</th>',
    '<th>Email</th>': '<th>{{ translations.email or \'Email\' }}</th>',
    '<th>Age</th>': '<th>{{ translations.age or \'Age\' }}</th>',
    '<th>Role</th>': '<th>{{ translations.admin_col_category or \'Role\' }}</th>',
    '<th>Level</th>': '<th>{{ translations.learning_level or \'Level\' }}</th>'
}

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
filepath = os.path.join(base_dir, "templates", "admin_dashboard.html")

if os.path.exists(filepath):
    print("Reading admin_dashboard.html...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    print("Replacing rest of column headers...")
    for orig, rep in replacements.items():
        if orig in content:
            content = content.replace(orig, rep)
        else:
            print(f"Warning: String not found: {orig}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated admin_dashboard.html!")
else:
    print("Error: admin_dashboard.html not found.")
