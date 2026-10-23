import tkinter as tk
from tkinter import ttk, messagebox
from services import CampusService, ResourceService, BookingService
from reports import ReportService

class AdminWindow:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user
        self.campus_service = CampusService(db)
        self.resource_service = ResourceService(db)l
        self.booking_service = BookingService(db, self.campus_service)
        self.report_service = ReportService(db)
        self._build()

    def _build(self):
        bar = ttk.Frame(self.root, padding=8);
        bar.pack(fill="x")
        ttk.Label(bar, text=f"Admin: {self.user.full_name}", font=("Segoe UI", 10, "bold")).pack(side="left")

        campus = self.campus_service.get_campus(self.user.campus_id)
        rule = self.campus_service.get_rule(self.user.campus_id)
        ttk.Label(bar, text=f"  Active Campus: {campus['name']}").pack(side="left", padx=20)
        ttk.Label(bar, text=f"  Policy: {rule.describe()}", foreground="#1976D2", font=("Segoe UI", 10, "bold")).pack(
            side="left")

        ttk.Button(bar, text="Logout", style="Pink.TButton", command=self._logout).pack(side="right", padx=5)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Manage Resources
        mr = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(mr, text="Manage Resources")

        cols = ("id", "code", "name", "type")
        self.admin_res_tree = ttk.Treeview(mr, columns=cols, show="headings")
        for c in cols:
            self.admin_res_tree.heading(c, text=c.title())
            self.admin_res_tree.column(c, width=150, anchor="w")
        self.admin_res_tree.pack(fill="both", expand=True)
        self.admin_res_tree.bind("<<TreeviewSelect>>", self._on_admin_select)

        form = ttk.LabelFrame(mr, text="Resource Details")
        form.pack(fill="x", pady=10)
        ttk.Label(form, text="Code").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.res_code_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.res_code_var, width=15).grid(row=0, column=1)

        ttk.Label(form, text="Name").grid(row=0, column=2, padx=5, sticky="w")
        self.res_name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.res_name_var, width=20).grid(row=0, column=3)

        ttk.Label(form, text="Type").grid(row=0, column=4, padx=5, sticky="w")
        self.res_type_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.res_type_var, width=18,
                     values=["Computer Lab", "Projector", "Seminar Room"]).grid(row=0, column=5)

        btns = ttk.Frame(mr);
        btns.pack(fill="x")
        ttk.Button(btns, text="Add", style="Blue.TButton", command=self._add_resource).pack(side="left")
        ttk.Button(btns, text="Update Selected", style="Blue.TButton", command=self._update_resource).pack(side="left",
                                                                                                           padx=5)
        ttk.Button(btns, text="Delete Selected", style="Pink.TButton", command=self._delete_resource).pack(side="left",
                                                                                                           padx=5)

        # Tab 2: Campus Bookings
        cb = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(cb, text="Campus Bookings")
        cols2 = ("id", "resource", "user", "date", "start", "duration", "status")
        self.campus_bookings_tree = ttk.Treeview(cb, columns=cols2, show="headings")
        for c in cols2:
            self.campus_bookings_tree.heading(c, text=c.title())
            self.campus_bookings_tree.column(c, width=110, anchor="w")
        self.campus_bookings_tree.pack(fill="both", expand=True)
        ttk.Button(cb, text="Refresh", style="Blue.TButton", command=self._refresh_campus_bookings).pack(anchor="w",
                                                                                                         pady=5)

        # Tab 3: Campus Report
        rp = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(rp, text="Campus Report")
        self.report_summary = tk.StringVar()
        ttk.Label(rp, textvariable=self.report_summary, font=("Segoe UI", 11, "bold"), foreground="#1976D2").pack(
            anchor="w", pady=5)

        self.top_res_tree = ttk.Treeview(rp, columns=("resource", "uses"), show="headings", height=8)
        self.top_res_tree.heading("resource", text="Resource Name")
        self.top_res_tree.column("resource", width=250)
        self.top_res_tree.heading("uses", text="Total Bookings")
        self.top_res_tree.pack(fill="both", expand=True, pady=5)
        ttk.Button(rp, text="Refresh Report", style="Blue.TButton", command=self._refresh_report).pack(anchor="w")

        self._refresh_admin_resources()
        self._refresh_campus_bookings()
        self._refresh_report()

    def _logout(self):
        from gui.login import LoginWindow
        for w in self.root.winfo_children(): w.destroy()
        LoginWindow(self.root, self.db)

    def _refresh_admin_resources(self):
        self.admin_res_tree.delete(*self.admin_res_tree.get_children())
        for r in self.resource_service.list_by_campus(self.user.campus_id):
            self.admin_res_tree.insert("", "end", values=(r["id"], r["resource_code"], r["name"], r["resource_type"]))

    def _on_admin_select(self, _event=None):
        sel = self.admin_res_tree.selection()
        if sel:
            v = self.admin_res_tree.item(sel[0])["values"]
            self.res_code_var.set(v[1]);
            self.res_name_var.set(v[2]);
            self.res_type_var.set(v[3])

    def _add_resource(self):
        ok, msg = self.resource_service.add_resource(self.res_code_var.get(), self.res_name_var.get(),
                                                     self.res_type_var.get(), self.user.campus_id)
        (messagebox.showinfo if ok else messagebox.showerror)("Add", msg)
        self._refresh_admin_resources()

    def _update_resource(self):
        sel = self.admin_res_tree.selection()
        if not sel: return messagebox.showwarning("Update", "Select a resource.")
        rid = int(self.admin_res_tree.item(sel[0])["values"][0])
        ok, msg = self.resource_service.update_resource(rid, self.res_name_var.get(), self.res_type_var.get())
        (messagebox.showinfo if ok else messagebox.showerror)("Update", msg)
        self._refresh_admin_resources()

    def _delete_resource(self):
        sel = self.admin_res_tree.selection()
        if not sel: return messagebox.showwarning("Delete", "Select a resource.")
        rid = int(self.admin_res_tree.item(sel[0])["values"][0])
        ok, msg = self.resource_service.delete_resource(rid)
        (messagebox.showinfo if ok else messagebox.showerror)("Delete", msg)
        self._refresh_admin_resources()

    def _refresh_campus_bookings(self):
        self.campus_bookings_tree.delete(*self.campus_bookings_tree.get_children())
        for r in self.booking_service.campus_bookings(self.user.campus_id):
            self.campus_bookings_tree.insert("", "end",
                                             values=(r["id"], r["resource_name"], r["user_name"], r["booking_date"],
                                                     r["start_time"], r["duration_minutes"], r["status"]))

    def _refresh_report(self):
        rep = self.report_service.campus_report(self.user.campus_id)
        self.report_summary.set(f"Total bookings: {rep['total']}    |    Average duration: {rep['avg']} min")
        self.top_res_tree.delete(*self.top_res_tree.get_children())
        for r in rep["top"]:
            self.top_res_tree.insert("", "end", values=(r["name"], r["uses"]))