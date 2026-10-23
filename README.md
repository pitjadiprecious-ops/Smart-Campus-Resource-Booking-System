# Smart-Campus-Resource-Booking-System
In this project I built a Smart Campus Resource Booking System using Python, Tkinter, and SQLite for Richfield Graduate Institution. 
Project link: https://github.com/pitjadiprecious-ops/Smart-Campus-Resource-Booking-System.git

I created a desktop application that allows users to book and manage academic resources across three or more campuses.

Three user roles
Lecturer: Register, log in, view resources, make bookings, view booking history, and cancel future bookings.
Campus Administrator: Add, edit, and remove resources, view campus bookings, and monitor resource usage.
System Operator: View information across all campuses and generate comparative reports.

 Main features
Login and lecturer registration.
Campus selection and campus-specific booking policies.
Resource management and availability checking.
Booking creation, cancellation, and history.
Prevention of overlapping bookings.
Reports showing total bookings, popular resources, and average booking duration.
Persistent data storage using SQLite.

 Programming concepts required
OOP: Classes, inheritance, and encapsulation.
Data structures: Lists, dictionaries, and sets.
GUI: Tkinter windows, buttons, forms, and tables.
Database: SQLite tables for users, campuses, resources, and bookings.
Validation: Check booking times, durations, permissions, and duplicate resources.

 Recommended project files
main.py — starts the application.
database.py — creates and manages the database.
models.py — defines classes and user roles.
booking_service.py — handles booking rules and availability.
gui.py — builds the Tkinter interface.
reports.py — generates statistics.
