
import getpass

from sqlalchemy import select

from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_admin():
    print("=== Create Initial Admin Account ===")

    name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip().lower()
    password = getpass.getpass("Enter admin password: ")

    if not name or not email or len(password) < 8:
        print("Invalid input. Password must contain at least 8 characters.")
        return

    with SessionLocal() as db:
        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            print("An account with this email already exists.")
            return

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="admin"
        )

        db.add(admin)
        db.commit()

        print("Admin account created successfully!")


if __name__ == "__main__":
    create_admin()
