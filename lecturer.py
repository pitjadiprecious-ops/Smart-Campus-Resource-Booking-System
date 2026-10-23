import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from services import CampusService, ResourceService, BookingService

class LecturerWindow:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user
        self.campus_service = CampusService(db)
        self.resource_service = ResourceService(db)
        self.booking_service = BookingService(db, self.campus_service)

        self.active_campus_id = user.campus_id or self.campus_service.list_campuses()[0]["id"]
        self._build()

    def _build(self):
        bar = ttk.Frame(self.root, padding=8);
        bar.pack(fill="x")
        ttk.Label(bar, text=f"Lecturer: {self.user.full_name}", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(bar, text="Logout", style="Pink.TButton", command=self._logout).pack(side="right", padx=5)

        ttk.Label(bar, text="Campus:").pack(side="left", padx=(20, 5))
        self.campus_map = {r["name"]: r["id"] for r in self.campus_service.list_campuses()}
        self.campus_var = tk.StringVar(value=self.campus_service.get_campus(self.active_campus_id)["name"])
        cb = ttk.Combobox(bar, textvariable=self.campus_var, state="readonly", values=list(self.campus_map.keys()),
                          width=18)
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", self._on_campus_change)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Book
        book_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(book_tab, text="Book Resource")

        self.policy_var = tk.StringVar()
        ttk.Label(book_tab, textvariable=self.policy_var, foreground="#1976D2", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=(0, 10))

        form = ttk.Frame(book_tab);
        form.pack(anchor="w", fill="x")
        ttk.Label(form, text="Resource").grid(row=0, column=0, sticky="w", pady=4)
        self.resource_map = {}
        self.resource_var = tk.StringVar()
        self.resource_combo = ttk.Combobox(form, textvariable=self.resource_var, width=42, state="readonly")
        self.resource_combo.grid(row=0, column=1, padx=5, pady=4)
        ttk.Button(form, text="Refresh", style="Blue.TButton", command=self._refresh_resources).grid(row=0, column=2)
        self.resource_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_availability())

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", pady=4)
        self.date_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.date_var, width=44).grid(row=1, column=1, padx=5, pady=4, sticky="w")

        ttk.Label(form, text="Start (HH:MM)").grid(row=2, column=0, sticky="w", pady=4)
        self.time_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.time_var, width=44).grid(row=2, column=1, padx=5, pady=4, sticky="w")

        ttk.Label(form, text="Duration (min)").grid(row=3, column=0, sticky="w", pady=4)
        self.duration_var = tk.IntVar(value=60)
        ttk.Spinbox(form, from_=15, to=480, increment=15, textvariable=self.duration_var, width=42).grid(row=3,
                                                                                                         column=1,
                                                                                                         padx=5, pady=4,
                                                                                                         sticky="w")

        ttk.Button(form, text="Book Resource", style="Blue.TButton", command=self._book).grid(row=4, column=1,
                                                                                              sticky="w", pady=10)
        ttk.Button(form, text="Check Availability", style="Blue.TButton", command=self._check_availability).grid(row=4,
                                                                                                                 column=2,
                                                                                                                 pady=10)

        avail_frame = ttk.LabelFrame(book_tab, text="Existing bookings for selected resource")
        avail_frame.pack(fill="both", expand=True, pady=(8, 0))
        self.avail_tree = ttk.Treeview(avail_frame, columns=("date", "start", "duration", "user"), show="headings",
                                       height=6)
        for c in ("date", "start", "duration", "user"):
            self.avail_tree.heading(c, text=c.title())
            self.avail_tree.column(c, width=160, anchor="w")
        self.avail_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 2: My Bookings
        mb = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(mb, text="My Bookings")

        cols = ("id", "resource", "campus", "date", "start", "duration", "status")
        self.my_bookings_tree = ttk.Treeview(mb, columns=cols, show="headings")
        for c in cols:
            self.my_bookings_tree.heading(c, text=c.title())
            self.my_bookings_tree.column(c, width=110, anchor="w")
        self.my_bookings_tree.pack(fill="both", expand=True)

        btns = ttk.Frame(mb);
        btns.pack(fill="x", pady=5)
        ttk.Button(btns, text="Refresh", style="Blue.TButton", command=self._refresh_my_bookings).pack(side="left")
        ttk.Button(btns, text="Cancel Selected Booking", style="Pink.TButton", command=self._cancel_selected).pack(
            side="left", padx=5)

        self._refresh_policy_label()
        self._refresh_resources()
        self._refresh_my_bookings()

    def _logout(self):
        from gui.login import LoginWindow
        for w in self.root.winfo_children(): w.destroy()
        LoginWindow(self.root, self.db)

    def _on_campus_change(self, _event=None):
        self.active_campus_id = self.campus_map[self.campus_var.get()]
        self._refresh_policy_label()
        self._refresh_resources()
        self._refresh_my_bookings()

    def _refresh_policy_label(self):
        rule = self.campus_service.get_rule(self.active_campus_id)
        self.policy_var.set("Active booking policy → " + rule.describe())

    def _refresh_resources(self):
        resources = self.resource_service.list_by_campus(self.active_campus_id)
        self.resource_map = {f"{r['resource_code']} — {r['name']}": r["id"] for r in resources}
        self.resource_combo["values"] = list(self.resource_map.keys())
        self.resource_var.set(next(iter(self.resource_map), ""))
        self._refresh_availability()

    def _refresh_availability(self):
        self.avail_tree.delete(*self.avail_tree.get_children())
        rid = self.resource_map.get(self.resource_var.get())
        if not rid: return
        rows = self.db.conn.execute(
            """SELECT b.booking_date, b.start_time, b.duration_minutes, u.full_name FROM bookings b JOIN users u ON u.id = b.user_id WHERE b.resource_id=? AND b.status='active' ORDER BY b.booking_date, b.start_time""",
            (rid,)).fetchall()
        for r in rows:
            self.avail_tree.insert("", "end",
                                   values=(r["booking_date"], r["start_time"], r["duration_minutes"], r["full_name"]))

    def _parse_input(self):
        d, t = self.date_var.get().strip(), self.time_var.get().strip()
        if not d or not t: raise ValueError("Enter date and start time.")
        try:
            return datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Date must be YYYY-MM-DD; time must be HH:MM.")

    def _check_availability(self):
        rid = self.resource_map.get(self.resource_var.get())
        if not rid: return messagebox.showwarning("Availability", "Select a resource.")
        try:
            start = self._parse_input();
            dur = int(self.duration_var.get())
        except Exception as e:
            return messagebox.showerror("Availability", str(e))

        if self.booking_service.is_available(rid, start, dur):
            messagebox.showinfo("Availability", "Resource is available for that slot.")
        else:
            messagebox.showwarning("Availability", "Resource is NOT available.")

    def _book(self):
        rid = self.resource_map.get(self.resource_var.get())
        if not rid: return messagebox.showwarning("Booking", "Select a resource.")
        try:
            self._parse_input();
            dur = int(self.duration_var.get())
        except Exception as e:
            return messagebox.showerror("Booking", str(e))

        ok, msg = self.booking_service.create_booking(self.user.id, self.active_campus_id, rid,
                                                      self.date_var.get().strip(), self.time_var.get().strip(), dur)
        (messagebox.showinfo if ok else messagebox.showerror)("Booking", msg)
        if ok:
            self._refresh_availability()
            self._refresh_my_bookings()

    def _refresh_my_bookings(self):
        self.my_bookings_tree.delete(*self.my_bookings_tree.get_children())
        for r in self.booking_service.lecturer_bookings(self.user.id):
            self.my_bookings_tree.insert("", "end",
                                         values=(r["id"], r["resource_name"], r["campus_name"], r["booking_date"],
                                                 r["start_time"], r["duration_minutes"], r["status"]))

    def _cancel_selected(self):
        sel = self.my_bookings_tree.selection()
        if not sel: return messagebox.showwarning("Cancel", "Select a booking.")
        bid = int(self.my_bookings_tree.item(sel[0])["values"][0])
        ok, msg = self.booking_service.cancel_booking(bid, user_id=self.user.id)
        (messagebox.showinfo if ok else messagebox.showerror)("Cancel", msg)
        if ok:
            self._refresh_my_bookings();
            self._refresh_availability()