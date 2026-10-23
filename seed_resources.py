# seed_resources.py
from database import Database


def seed_all_resources():
    db = Database()
    campuses = db.conn.execute("SELECT id, name FROM campuses").fetchall()

    # Standard resources to add
    resource_types = [
        ("LAB", "Computer Lab"),
        ("PROJ", "Multimedia Projector"),
        ("SEM", "Seminar Room"),
        ("PRES", "Presentation Equipment")
    ]

    count = 0
    for campus in campuses:
        campus_id = campus["id"]
        # Create a 3-letter prefix based on campus name (e.g., JOH, CAP, DUR)
        prefix = campus["name"][:3].upper()

        for r_code, r_type in resource_types:
            # Make unique code per campus, e.g., "JOH-LAB-01"
            code = f"{prefix}-{r_code}-01"
            name = f"{campus['name']} {r_type}"

            # Check if it already exists to prevent duplicates
            existing = db.conn.execute("SELECT id FROM resources WHERE resource_code=?", (code,)).fetchone()
            if not existing:
                db.conn.execute(
                    "INSERT INTO resources(resource_code, name, resource_type, campus_id) VALUES (?, ?, ?, ?)",
                    (code, name, r_type, campus_id)
                )
                print(f"Added: {code} - {name}")
                count += 1
            else:
                print(f"Skipped (already exists): {code}")

    db.conn.commit()
    print(f"\nSuccessfully added {count} resources across all campuses.")


if __name__ == "__main__":
    seed_all_resources()