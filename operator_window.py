import tkinter as tk
from tkinter import ttk
from services import CampusService, BookingService
from reports import ReportService

class OperatorWindow:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user
        self.campus_service = CampusService(db)
        self.booking_service = BookingService(db, self.campus_service)
        self.report_service = ReportService(db)
        self._build()

    def _build(self):
        bar = ttk.Frame(self.root, padding=8); bar.pack(fill="x")
        ttk.Label(bar, text=f"System Operator: {self.user.full_name}", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(bar, text="Logout", command=self._logout).pack(side="right", padx=5)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        ab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(ab, text="All Bookings")
        cols = ("id", "campus", "resource", "user", "date", "start", "duration", "status")
        self.all_bookings_tree = ttk.Treeview(ab, columns=cols, show="headings")
        for c in cols:
            self.all_bookings_tree.heading(c, text=c.title())
            self.all_bookings_tree.column(c, width=100, anchor="w")
        self.all_bookings_tree.pack(fill="both", expand=True)
        ttk.Button(ab, text="Refresh", command=self._refresh_all_bookings).pack(anchor="w", pady=5)

        cr = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(cr, text="Cross-Campus Report")
        self.cross_tree = ttk.Treeview(cr, columns=("campus", "total_bookings", "average_duration"), show="headings", height=8)
        for c in ("campus", "total_bookings", "average_duration"):
            self.cross_tree.heading(c, text=c.replace("_", " ").title())
            self.cross_tree.column(c, width=180)
        self.cross_tree.pack(fill="both", expand=True)
        ttk.Button(cr, text="Refresh", command=self._refresh_cross_report).pack(anchor="w", pady=5)

        self._refresh_all_bookings()
        self._refresh_cross_report()

    def _logout(self):
        from gui.login import LoginWindow
        for w in self.root.winfo_children(): w.destroy()
        LoginWindow(self.root, self.db)

    def _refresh_all_bookings(self):
        self.all_bookings_tree.delete(*self.all_bookings_tree.get_children())
        for r in self.booking_service.all_bookings():
            self.all_bookings_tree.insert("", "end", values=(r["id"], r["campus_name"], r["resource_name"], r["user_name"], r["booking_date"], r["start_time"], r["duration_minutes"], r["status"]))

    def _refresh_cross_report(self):
        self.cross_tree.delete(*self.cross_tree.get_children())
        for r in self.report_service.cross_campus():
            avg = round(r["avg_dur"], 1) if r["avg_dur"] else 0
            self.cross_tree.insert("", "end", values=(r["campus"], r["bookings"], avg))