import sqlite3
from C2_Variables import DB_PATH


####################################################################################################################

# Initialize the DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            unique_id TEXT PRIMARY KEY,
            btc_address TEXT,
            paid BOOLEAN DEFAULT 0,
            uuid TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

####################################################################################################################