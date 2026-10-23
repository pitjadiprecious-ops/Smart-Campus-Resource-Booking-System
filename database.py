
import os
import hashlib
import secrets
import sqlite3

# Database file is created in the same folder as this Python file.
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "smart_campus.db"
)


def _hash(pw: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with a random salt.
    The salt is stored with the hash so it can be checked later.
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        pw.encode("utf-8"),
        bytes.fromhex(salt),
        200_000
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(pw: str, stored_hash: str) -> bool:
    """Check whether a password matches its stored hash."""
    try:
        salt, expected_hash = stored_hash.split("$", 1)
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            pw.encode("utf-8"),
            bytes.fromhex(salt),
            200_000
        ).hex()

        return secrets.compare_digest(actual_hash, expected_hash)
    except (ValueError, TypeError):
        return False


class Database:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row

        # Enable foreign-key checks.
        self.conn.execute("PRAGMA foreign_keys = ON")

        self._create_tables()
        self._seed()

    def _create_tables(self):
        """Create the database tables if they do not exist."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS campuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                max_duration INTEGER NOT NULL,
                open_hour INTEGER NOT NULL,
                close_hour INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK(role IN ('lecturer', 'admin', 'operator')),
                campus_id INTEGER REFERENCES campuses(id)
            );

            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                campus_id INTEGER NOT NULL REFERENCES campuses(id)
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER NOT NULL REFERENCES resources(id),
                user_id INTEGER NOT NULL REFERENCES users(id),
                campus_id INTEGER NOT NULL REFERENCES campuses(id),
                booking_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active'
            );
        """)
        self.conn.commit()

    def _seed(self):
        """Insert initial campuses, users, and resources."""
        cur = self.conn.cursor()

        existing = cur.execute(
            "SELECT COUNT(*) FROM campuses"
        ).fetchone()[0]

        if existing > 0:
            print("Database already contains data. Skipping seed.")
            return

        print("Empty database detected. Adding seed data...")

        try:
            # 1. Add campuses.
            campuses = [
                ("Centurion", 120, 8, 17),
                ("Pretoria", 90, 9, 16),
                ("Durban", 180, 7, 18),
            ]

            for campus in campuses:
                cur.execute("""
                    INSERT INTO campuses
                    (name, max_duration, open_hour, close_hour)
                    VALUES (?, ?, ?, ?)
                """, campus)

                print(f" -> Added Campus: {campus[0]}")

            # 2. Add the system operator.
            cur.execute("""
                INSERT INTO users
                (username, password_hash, full_name, role, campus_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "operator",
                _hash("thati123"),
                "System Operator",
                "operator",
                None
            ))

            print(" -> Added User: operator")

            # 3. Define resource types.
            resource_types = [
                ("LAB", "Computer Lab"),
                ("PROJ", "Multimedia Projector"),
                ("SEM", "Seminar Room"),
                ("PRES", "Presentation Equipment"),
            ]

            # 4. Add an administrator and resources per campus.
            campus_rows = cur.execute(
                "SELECT id, name FROM campuses"
            ).fetchall()

            for row in campus_rows:
                campus_id = row["id"]
                campus_name = row["name"]

                username = "admin_" + campus_name.lower()

                cur.execute("""
                    INSERT INTO users
                    (username, password_hash, full_name, role, campus_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    username,
                    _hash("thati123"),
                    f"Admin {campus_name}",
                    "admin",
                    campus_id
                ))

                print(f" -> Added User: {username}")

                prefix = campus_name[:3].upper()

                for resource_code, resource_type in resource_types:
                    code = f"{prefix}-{resource_code}-01"
                    resource_name = f"{campus_name} {resource_type}"

                    cur.execute("""
                        INSERT INTO resources
                        (resource_code, name, resource_type, campus_id)
                        VALUES (?, ?, ?, ?)
                    """, (
                        code,
                        resource_name,
                        resource_type,
                        campus_id
                    ))

                print(f" -> Added 4 Resources for {campus_name}")

            self.conn.commit()
            print("Seed data successfully added to database!")

        except sqlite3.Error:
            self.conn.rollback()
            raise

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None


if __name__ == "__main__":
    # Run this file directly to create and initialize the database.
    db = Database()

    try:
        print("\nDatabase initialized successfully.")

        campuses = db.conn.execute(
            "SELECT * FROM campuses"
        ).fetchall()

        print(f"Total campuses: {len(campuses)}")

        resources = db.conn.execute(
            "SELECT COUNT(*) FROM resources"
        ).fetchone()[0]

        print(f"Total resources: {resources}")

        users = db.conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        print(f"Total users: {users}")

        # Demonstrate password verification.
        operator = db.conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            ("operator",)
        ).fetchone()

        if operator:
            print(
                "Operator password verification:",
                verify_password("thati123", operator["password_hash"])
            )

    finally:
        db.close()
