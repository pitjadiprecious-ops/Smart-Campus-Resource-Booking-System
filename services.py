from datetime import datetime, timedelta
from booking_rules import rule_from_row

def parse_dt(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

class CampusService:
    def __init__(self, db): self.db = db
    def list_campuses(self): return self.db.conn.execute("SELECT * FROM campuses ORDER BY name").fetchall()
    def get_campus(self, campus_id): return self.db.conn.execute("SELECT * FROM campuses WHERE id=?", (campus_id,)).fetchone()
    def get_rule(self, campus_id):
        row = self.get_campus(campus_id)
        return rule_from_row(row) if row else None

class ResourceService:
    def __init__(self, db): self.db = db
    def add_resource(self, code, name, rtype, campus_id):
        code, name, rtype = (code or "").strip(), (name or "").strip(), (rtype or "").strip()
        if not (code and name and rtype): return False, "Code, name, and type are required."
        try:
            self.db.conn.execute("INSERT INTO resources(resource_code,name,resource_type,campus_id) VALUES (?,?,?,?)", (code, name, rtype, campus_id))
            self.db.conn.commit()
            return True, "Resource added."
        except Exception:
            return False, "Resource code already exists."

    def update_resource(self, resource_id, name, rtype):
        self.db.conn.execute("UPDATE resources SET name=?, resource_type=? WHERE id=?", (name, rtype, resource_id))
        self.db.conn.commit()
        return True, "Resource updated."

    def delete_resource(self, resource_id):
        active = self.db.conn.execute("SELECT COUNT(*) c FROM bookings WHERE resource_id=? AND status='active'", (resource_id,)).fetchone()["c"]
        if active: return False, "Cannot delete — active bookings exist."
        self.db.conn.execute("DELETE FROM resources WHERE id=?", (resource_id,))
        self.db.conn.commit()
        return True, "Resource deleted."

    def list_by_campus(self, campus_id):
        return self.db.conn.execute("SELECT * FROM resources WHERE campus_id=? ORDER BY name", (campus_id,)).fetchall()

class BookingService:
    def __init__(self, db, campus_service):
        self.db = db
        self.campus_service = campus_service

    def is_available(self, resource_id, start_dt, duration):
        new_end = start_dt + timedelta(minutes=duration)
        rows = self.db.conn.execute("SELECT booking_date, start_time, duration_minutes FROM bookings WHERE resource_id=? AND status='active'", (resource_id,)).fetchall()
        for r in rows:
            s = parse_dt(r["booking_date"], r["start_time"])
            e = s + timedelta(minutes=r["duration_minutes"])
            if start_dt < e and s < new_end: return False
        return True

    def create_booking(self, user_id, campus_id, resource_id, date_str, time_str, duration):
        try: start_dt = parse_dt(date_str, time_str)
        except ValueError: return False, "Invalid date/time."
        if start_dt < datetime.now(): return False, "Cannot book in the past."
        rule = self.campus_service.get_rule(campus_id)
        ok, errors = rule.validate(start_dt, duration)
        if not ok: return False, " ".join(errors)
        if not self.is_available(resource_id, start_dt, duration): return False, "Resource is not available."
        self.db.conn.execute("INSERT INTO bookings(resource_id,user_id,campus_id,booking_date,start_time,duration_minutes) VALUES (?,?,?,?,?,?)", (resource_id, user_id, campus_id, date_str, time_str, duration))
        self.db.conn.commit()
        return True, "Booking confirmed."

    def cancel_booking(self, booking_id, user_id=None):
        row = self.db.conn.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()
        if not row: return False, "Booking not found."
        if user_id is not None and row["user_id"] != user_id: return False, "You cannot cancel someone else's booking."
        if parse_dt(row["booking_date"], row["start_time"]) <= datetime.now(): return False, "Only future bookings can be cancelled."
        self.db.conn.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
        self.db.conn.commit()
        return True, "Booking cancelled."

    def lecturer_bookings(self, user_id):
        return self.db.conn.execute("""SELECT b.*, r.name AS resource_name, c.name AS campus_name FROM bookings b JOIN resources r ON r.id = b.resource_id JOIN campuses c ON c.id = b.campus_id WHERE b.user_id=? ORDER BY b.booking_date DESC""", (user_id,)).fetchall()

    def campus_bookings(self, campus_id):
        return self.db.conn.execute("""SELECT b.*, r.name AS resource_name, u.full_name AS user_name FROM bookings b JOIN resources r ON r.id = b.resource_id JOIN users u ON u.id = b.user_id WHERE b.campus_id=? ORDER BY b.booking_date DESC""", (campus_id,)).fetchall()

    def all_bookings(self):
        return self.db.conn.execute("""SELECT b.*, r.name AS resource_name, u.full_name AS user_name, c.name AS campus_name FROM bookings b JOIN resources r ON r.id = b.resource_id JOIN users u ON u.id = b.user_id JOIN campuses c ON c.id = b.campus_id ORDER BY b.booking_date DESC""").fetchall()