import json
from datetime import datetime


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class Quiz:
    def __init__(self, subject, questions):
        self.subject = subject
        self.questions = questions


class QuizApp:
    def __init__(self, user_file="users.json", score_file="scores.json"):
        self.user_file = user_file
        self.score_file = score_file
        self.users = self.load_users()
        self.subjects = {}

    # ---------------- USER FILE HANDLING ----------------
    def load_users(self):
        try:
            with open(self.user_file, "r") as f:
                data = json.load(f)
                return [User(u["username"], u["password"]) for u in data]
        except:
            return []

    def save_users(self):
        with open(self.user_file, "w") as f:
            json.dump(
                [{"username": u.username, "password": u.password} for u in self.users],
                f,
                indent=4
            )

    # ---------------- AUTH ----------------
    def register(self, username, password):
        if any(u.username == username for u in self.users):
            return False
        self.users.append(User(username, password))
        self.save_users()
        return True

    def login(self, username, password):
        return any(
            u.username == username and u.password == password
            for u in self.users
        )

    # ---------------- QUIZ ----------------
    def add_subject(self, subject, questions):
        self.subjects[subject] = Quiz(subject, questions)

    # ---------------- SCORE STORAGE ----------------
    def save_score(self, username, subject, score, total):
        data = []

        try:
            with open(self.score_file, "r") as f:
                data = json.load(f)
        except:
            pass  # file not found or empty

        data.append({
            "username": username,
            "subject": subject,
            "score": score,
            "total": total,
            "percentage": round((score / total) * 100, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        with open(self.score_file, "w") as f:
            json.dump(data, f, indent=4)
