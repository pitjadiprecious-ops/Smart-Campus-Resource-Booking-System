class User:
    ROLE = "user"
    def __init__(self, id, username, full_name, role, campus_id):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.role = role
        self.campus_id = campus_id

    def display_name(self):
        return f"{self.full_name} ({self.role})"

    @staticmethod
    def from_row(row):
        cls = {"lecturer": Lecturer, "admin": CampusAdmin, "operator": SystemOperator}.get(row["role"], User)
        return cls(row["id"], row["username"], row["full_name"], row["role"], row["campus_id"])

class Lecturer(User):
    ROLE = "lecturer"

class CampusAdmin(User):
    ROLE = "admin"

class SystemOperator(User):
    ROLE = "operator"