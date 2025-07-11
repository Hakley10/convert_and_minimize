import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="Automata"
    )
    print("Successfully connected to database!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")