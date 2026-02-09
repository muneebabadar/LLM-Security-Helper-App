import sqlite3
 
def login(username, password):

    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()
 
    # ❌ Vulnerable: string concatenation with user input

    query = f"""

        SELECT * FROM users

        WHERE username = '{username}'

        AND password = '{password}'

    """

    print("Executing query:", query)
 
    cursor.execute(query)

    result = cursor.fetchone()
 
    conn.close()

    return result is not None
 
 
# ---- DEMO ----

print("Normal login:", login("alice", "password123"))
 
# Attacker input

malicious_password = "' OR '1'='1"

print("Injected login:", login("alice", malicious_password))
 