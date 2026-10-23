from datetime import timedelta


class BookingRule:
    def __init__(self, campus_id, campus_name, max_duration, open_hour, close_hour):
        self.campus_id = campus_id
        self.campus_name = campus_name
        self.max_duration = max_duration
        self.open_hour = open_hour
        self.close_hour = close_hour

    def describe(self):
        return f"{self.campus_name}: max {self.max_duration} min, open {self.open_hour:02d}:00–{self.close_hour:02d}:00"

    def validate(self, start_dt, duration):
        errors = []
        if duration <= 0:
            errors.append("Duration must be greater than zero.")
        if duration > self.max_duration:
            errors.append(f"Duration exceeds the {self.max_duration}-minute limit.")
        if start_dt.hour < self.open_hour:
            errors.append(f"Bookings cannot start before {self.open_hour:02d}:00.")

        end_dt = start_dt + timedelta(minutes=duration)
        if end_dt.hour > self.close_hour or (end_dt.hour == self.close_hour and end_dt.minute > 0):
            errors.append(f"Booking must finish by {self.close_hour:02d}:00.")
        return (len(errors) == 0, errors)


def rule_from_row(row) -> BookingRule:
    return BookingRule(row["id"], row["name"], row["max_duration"], row["open_hour"], row["close_hour"])