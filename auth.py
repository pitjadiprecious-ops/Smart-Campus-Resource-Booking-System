import hashlib
from models import User

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

class AuthService:
    def __init__(self, db):
        self.db = db

    def register_lecturer(self, username, password, full_name, campus_id):
        if not all([username, password, full_name, campus_id]):
            return False, "All fields are required."
        try:
            self.db.conn.execute(
                "INSERT INTO users(username,password_hash,full_name,role,campus_id) VALUES (?,?,?,?,?)",
                (username, hash_password(password), full_name, "lecturer", campus_id))
            self.db.conn.commit()
            return True, "Lecturer account created."
        except Exception:
            return False, "Username already exists."

    def login(self, username, password):
        row = self.db.conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if row and row["password_hash"] == hash_password(password):
            return User.from_row(row)
        return None