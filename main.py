import tkinter as tk
from database import Database
from gui.styles import apply_theme  # <--- UPDATED IMPORT HERE
from gui.login import LoginWindow

def main():
    db = Database()
    root = tk.Tk()
    root.geometry("1000x650")
    root.title("Smart Campus Resource Booking System")

    apply_theme(root)

    LoginWindow(root, db)
    root.mainloop()


if __name__ == "__main__":
    main()