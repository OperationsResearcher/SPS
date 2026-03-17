
import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'spsv2.db')
print(f"Connecting to DB: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check max id
    cursor.execute("SELECT MAX(id) FROM task")
    max_id = cursor.fetchone()[0]
    print(f"MAX Task ID: {max_id}")
    
    # Try inserting manually
    print("Attempting manual insertion via SQLite3...")
    cursor.execute("""
        INSERT INTO task (project_id, title, reporter_id, status, created_at, priority, is_archived)
        VALUES (2, 'Manual SQLite Test', 2, 'Yapılacak', CURRENT_TIMESTAMP, 'Orta', 0)
    """)
    conn.commit()
    print("Insertion committed.")
    
    # Verify
    cursor.execute("SELECT id, title FROM task WHERE title = 'Manual SQLite Test'")
    row = cursor.fetchone()
    if row:
        print(f"SUCCESS: Found inserted task ID {row[0]}")
    else:
        print("FAILED: Inserted task NOT found!")
        
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
