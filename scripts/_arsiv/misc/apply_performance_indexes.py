"""
SQLite Index Creation Script Runner
Applies performance indexes to the database
"""
import sqlite3
import os

def apply_indexes():
    """Apply all performance indexes to the database"""
    db_path = os.path.join(os.path.dirname(__file__), 'spsv2.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    print(f"📊 Applying performance indexes to: {db_path}")
    
    # Read SQL file
    sql_file = os.path.join(os.path.dirname(__file__), 'add_sqlite_indexes.sql')
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute each statement
        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        
        success_count = 0
        for statement in statements:
            if statement:
                try:
                    cursor.execute(statement)
                    success_count += 1
                    # Extract index name from CREATE INDEX statement
                    if 'CREATE INDEX' in statement:
                        idx_name = statement.split('idx_')[1].split(' ')[0] if 'idx_' in statement else 'unknown'
                        print(f"  ✅ Created index: idx_{idx_name}")
                except sqlite3.OperationalError as e:
                    if 'already exists' in str(e).lower():
                        continue  # Index already exists, skip
                    else:
                        print(f"  ⚠️ Warning: {e}")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Successfully applied {success_count} index statements!")
        print("📈 Performance optimization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying indexes: {e}")
        return False

if __name__ == '__main__':
    apply_indexes()
