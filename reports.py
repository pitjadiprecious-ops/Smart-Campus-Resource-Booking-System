class ReportService:
    def __init__(self, db): self.db = db

    def campus_report(self, campus_id):
        totals = self.db.conn.execute("SELECT COUNT(*) AS c, AVG(duration_minutes) AS a FROM bookings WHERE campus_id=? AND status='active'", (campus_id,)).fetchone()
        top = self.db.conn.execute("SELECT r.name, COUNT(*) AS uses FROM bookings b JOIN resources r ON r.id = b.resource_id WHERE b.campus_id=? AND b.status='active' GROUP BY r.id ORDER BY uses DESC LIMIT 5", (campus_id,)).fetchall()
        return {"total": totals["c"] or 0, "avg": round(totals["a"], 1) if totals["a"] else 0, "top": top}

    def cross_campus(self):
        return self.db.conn.execute("SELECT c.name AS campus, COUNT(b.id) AS bookings, AVG(b.duration_minutes) AS avg_dur FROM campuses c LEFT JOIN bookings b ON b.campus_id = c.id AND b.status='active' GROUP BY c.id ORDER BY c.name").fetchall()