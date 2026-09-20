import sqlite3

class DBManager:
    """
    SQLite Database Logger for Vori Session Biometrics
    """
    def __init__(self, db_name="vori_biometrics.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                tbr REAL,
                alpha_power REAL,
                hjorth_mobility REAL,
                kurtosis_val REAL,
                risk_score REAL,
                is_overload INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def log_features(self, timestamp, res):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO session_features 
            (timestamp, tbr, alpha_power, hjorth_mobility, kurtosis_val, risk_score, is_overload)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, 
            res["tbr"], 
            res["alphaPower"], 
            res["mobility"], 
            res["kurtosis"], 
            res["riskScore"], 
            int(res["isOverload"])
        ))
        conn.commit()
        conn.close()
