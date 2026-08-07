import sqlite3

output = []

def check_db(db_name):
    output.append(f"=== Checking {db_name} ===\n")
    try:
        conn = sqlite3.connect(db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check table schema for users
        cursor.execute("PRAGMA table_info(users)")
        cols = [r["name"] for r in cursor.fetchall()]
        output.append(f"Columns: {', '.join(cols)}\n")
        
        # Find admins
        if "role" in cols:
            cursor.execute("SELECT * FROM users WHERE role = 'admin'")
        else:
            cursor.execute("SELECT * FROM users")
        
        rows = cursor.fetchall()
        for r in rows:
            user_dict = dict(r)
            # Remove password hash for cleaner output, or keep it if needed
            user_dict.pop("password", None)
            output.append(f"User: {user_dict}\n")
            
        conn.close()
    except Exception as e:
        output.append(f"Error checking {db_name}: {e}\n")

check_db(r"c:\Users\user\Downloads\infosys40\infosys 3\literacy.db")
check_db(r"c:\Users\user\Downloads\infosys40\infosys 3\foundational_literacy.db")

with open(r"c:\Users\user\Downloads\infosys40\infosys 3\scratch\admin_info.txt", "w", encoding="utf-8") as f:
    f.write("".join(output))

print("Done checking databases.")
