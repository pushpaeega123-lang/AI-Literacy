#!/usr/bin/env python3
import sqlite3
from werkzeug.security import generate_password_hash

DB = 'literacy.db'

users = [
    ('John Doe', 'john@example.com', 'Password123!', '28', 'UG', 'Student', 'English'),
    ('రామ్ కేసవ', 'ram@example.com', 'TeluguPass1!', '32', 'PG', 'Employee', 'Telugu'),
    ('Priya Sharma', 'priya@example.com', 'HindiPass1!', '25', 'UG', 'Beginner', 'Hindi')
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

for fullname,email,password,age,education,status,language in users:
    hashed = generate_password_hash(password)
    try:
        cur.execute('INSERT INTO users (fullname,email,password,age,education_level,learning_status,language) VALUES (?,?,?,?,?,?,?)',
                    (fullname,email,hashed,age,education,status,language))
        print('Inserted', email)
    except sqlite3.IntegrityError:
        print('Already exists', email)

conn.commit()
conn.close()
print('Done')
