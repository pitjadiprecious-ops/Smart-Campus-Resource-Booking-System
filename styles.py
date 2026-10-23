# gui/styles.py
from tkinter import ttk


def apply_theme(root):
    style = ttk.Style()
    style.theme_use('clam')

    # --- COLOR PALETTE ---
    PINK = "#E91E63"  # Main pink
    LIGHT_PINK = "#FCE4EC"  # Very soft pink
    BLUE = "#1976D2"  # Main blue
    DARK_BLUE = "#0D47A1"  # Deep blue for text
    LIGHT_BLUE = "#E3F2FD"  # Soft blue for backgrounds
    WHITE = "#FFFFFF"

    root.configure(bg=LIGHT_BLUE)
    style.configure("TFrame", background=LIGHT_BLUE)
    style.configure("TLabel", background=LIGHT_BLUE, foreground=DARK_BLUE, font=("Segoe UI", 10))

    # Header Label (Title)
    style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground=BLUE, background=LIGHT_BLUE)

    # --- NOTEBOOK (Tabs) ---
    style.configure("TNotebook", background=WHITE, borderwidth=0)
    style.configure("TNotebook.Tab", background=LIGHT_BLUE, foreground=DARK_BLUE, padding=[15, 5],
                    font=("Segoe UI", 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", BLUE)], foreground=[("selected", WHITE)])

    # --- BUTTONS ---
    style.configure("Blue.TButton", background=BLUE, foreground=WHITE, font=("Segoe UI", 10, "bold"), borderwidth=0,
                    padding=5)
    style.map("Blue.TButton", background=[("active", DARK_BLUE), ("disabled", "#90CAF9")])

    style.configure("BLUE", background=PINK, foreground=WHITE, font=("Segoe UI", 10, "bold"), borderwidth=0,
                    padding=5)
    style.map("BLUE", background=[("active", "#C2185B"), ("disabled", "#F48FB1")])

    # --- TREEVIEW (Tables) ---
    style.configure("Treeview", background=WHITE, foreground=DARK_BLUE, rowheight=25, fieldbackground=WHITE)
    style.configure("Treeview.Heading", background=BLUE, foreground=WHITE, font=("Segoe UI", 10, "bold"), relief="flat")
    style.map("Treeview", background=[("selected", LIGHT_PINK)], foreground=[("selected", DARK_BLUE)])
    style.map("Treeview.Heading", background=[("active", DARK_BLUE)])