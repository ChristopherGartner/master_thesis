

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


def validate_username(username):
    # optional user validation
    if 3 > len(username) > 50:
        return f"Username zu kurz oder zu lang ({len(username)} Zeichen), muss 3-50 Zeichen lang sein!\n"
    else: return ""

def validate_email(email):
    #TODO email regex bei gpt erfragen
    if '@' in email and '.' in email:
        return ""
    else: return "Email ungültig!\n"

def validate_password(password):
    #TODO pw verification
    return ""

def validate_role(role):
    if role in ["User", "Campsite", "Admin"]:
        return ""
    else:
        return "Invalid role!\n"


class UserToDelete(UserMixin):
    id = 0
    username = ""
    email = ""
    password_hash = ""
    role = "User" #user / campsite / Admin

    def __init__(self, username=None, email=None, role="User", rs=None):
        if rs is not None:
            # Initialize from database result set
            self.id = rs[0]
            self.username = rs[1]
            self.email = rs[2]
            self.password_hash = rs[3]
            self.role = rs[4]
        else:
            # Initialize with individual parameters
            self.id = 0
            self.username = username
            self.email = email
            self.password_hash = ""
            self.role = role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        return self.password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



