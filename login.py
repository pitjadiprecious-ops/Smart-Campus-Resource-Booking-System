import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthService
from services import CampusService
from models import Lecturer, CampusAdmin, SystemOperator

class LoginWindow:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.auth = AuthService(db)
        self._clear_root()
        self._build()

    def _clear_root(self):
        for w in self.root.winfo_children(): w.destroy()

    def _build(self):
        # Added Header.TLabel style
        ttk.Label(self.root, text="Smart Campus Resource Booking System", style="Header.TLabel").pack(pady=(60, 20))
        form = ttk.Frame(self.root, padding=15);
        form.pack()

        ttk.Label(form, text="Username").grid(row=0, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.username_var, width=28).grid(row=0, column=1)

        ttk.Label(form, text="Password").grid(row=1, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.password_var, show="*", width=28).grid(row=1, column=1)

        btns = ttk.Frame(self.root);
        btns.pack(pady=15)
        # Added Blue and Pink styles to buttons
        ttk.Button(btns, text="Login", style="Blue.TButton", command=self.login).pack(side="left", padx=5)
        ttk.Button(btns, text="Register (Lecturer)", style="Blue.TButton", command=self.open_register).pack(side="left",
                                                                                                            padx=5)

    def login(self):
        u, p = self.username_var.get().strip(), self.password_var.get()
        if not u or not p: return messagebox.showwarning("Login", "Enter username and password.")
        user = self.auth.login(u, p)
        if not user: return messagebox.showerror("Login", "Invalid credentials.")

        self._clear_root()
        if isinstance(user, Lecturer):
            from gui.lecturer import LecturerWindow
            LecturerWindow(self.root, self.db, user)
        elif isinstance(user, CampusAdmin):
            from gui.admin_window import AdminWindow
            AdminWindow(self.root, self.db, user)
        elif isinstance(user, SystemOperator):
            from gui.operator_window import OperatorWindow
            OperatorWindow(self.root, self.db, user)

    def open_register(self):
        RegisterDialog(self.root, self.db)


class RegisterDialog(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.auth = AuthService(db)
        self.campus_service = CampusService(db)
        self.title("Register Lecturer")
        self.geometry("400x280")
        self.transient(parent);
        self.grab_set()
        self.configure(bg="#E3F2FD")  # Light blue background

        f = ttk.Frame(self, padding=20);
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="Full Name").grid(row=0, column=0, sticky="w", pady=5)
        self.full_name = tk.StringVar()
        ttk.Entry(f, textvariable=self.full_name, width=25).grid(row=0, column=1)

        ttk.Label(f, text="Username").grid(row=1, column=0, sticky="w", pady=5)
        self.username = tk.StringVar()
        ttk.Entry(f, textvariable=self.username, width=25).grid(row=1, column=1)

        ttk.Label(f, text="Password").grid(row=2, column=0, sticky="w", pady=5)
        self.password = tk.StringVar()
        ttk.Entry(f, textvariable=self.password, show="*", width=25).grid(row=2, column=1)

        ttk.Label(f, text="Campus").grid(row=3, column=0, sticky="w", pady=5)
        self.campus_map = {r["name"]: r["id"] for r in self.campus_service.list_campuses()}
        self.campus_var = tk.StringVar(value=list(self.campus_map.keys())[0])
        ttk.Combobox(f, textvariable=self.campus_var, state="readonly", values=list(self.campus_map.keys()),
                     width=22).grid(row=3, column=1)

        ttk.Button(f, text="Create Account", style="Blue.TButton", command=self.submit).grid(row=4, column=0,
                                                                                             columnspan=2, pady=15)

    def submit(self):
        ok, msg = self.auth.register_lecturer(
            self.username.get().strip(), self.password.get(),
            self.full_name.get().strip(), self.campus_map.get(self.campus_var.get()))
        (messagebox.showinfo if ok else messagebox.showerror)("Register", msg)
        if ok: self.destroy()