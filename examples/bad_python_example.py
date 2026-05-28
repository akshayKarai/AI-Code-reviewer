"""
Example: Vulnerable Python code with SQL injection, plain-text passwords, no error handling.
Use this to test the AI Code Reviewer's bug and security detection.
"""

import sqlite3

# ❌ Bad: SQL injection vulnerability
def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()

# ❌ Bad: Plaintext password comparison, no hashing
def login(username, password):
    user = get_user(username)
    if user and user[2] == password:
        return True
    return False

# ❌ Bad: Storing credentials in plaintext file
def save_credentials(username, password):
    with open("creds.txt", "a") as f:
        f.write(f"{username}:{password}\n")

# ❌ Bad: No input validation, division by zero possible
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total = total + n
    return total / len(numbers)

# ❌ Bad: Global mutable state, no thread safety
user_sessions = {}

def create_session(user_id):
    import random
    token = str(random.randint(1000, 9999))  # Weak token
    user_sessions[user_id] = token
    return token
