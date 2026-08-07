import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('literacy.db')
cur = conn.cursor()
cur.execute('DELETE FROM users WHERE email = ?', ('ram@example.com',))
hashed = generate_password_hash('TeluguPass1!')
cur.execute('INSERT INTO users (fullname, email, password, age, education_level, learning_status, language) VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('రామ్ కేసవ', 'ram@example.com', hashed, '32', 'PG', 'Employee', 'Telugu'))
conn.commit()
conn.close()
print('Reset complete!')
