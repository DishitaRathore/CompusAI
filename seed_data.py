from sqlalchemy import select

from database import SessionLocal
from models import Attendance, Fee, Student


def seed_database():
    db = SessionLocal()

    try:
        existing_student = db.scalar(
            select(Student.id).limit(1)
        )

        if existing_student is not None:
            print("Sample data already exists.")
            return

        students = [
            Student(
                id=1,
                name="Aarav Sharma",
                course="Computer Science"
            ),
            Student(
                id=2,
                name="Meera Patel",
                course="Information Technology"
            )
        ]

        db.add_all(students)

        # Commit students first because attendance and fees
        # depend on student IDs.
        db.commit()

        attendance_records = [
            Attendance(
                student_id=1,
                subject="Machine Learning",
                attended=18,
                total=20
            ),
            Attendance(
                student_id=1,
                subject="Database Systems",
                attended=15,
                total=20
            ),
            Attendance(
                student_id=2,
                subject="Machine Learning",
                attended=16,
                total=20
            )
        ]

        fee_records = [
            Fee(
                student_id=1,
                total_fee=100000,
                paid=75000,
                remaining=25000
            ),
            Fee(
                student_id=2,
                total_fee=100000,
                paid=100000,
                remaining=0
            )
        ]

        db.add_all(attendance_records)
        db.add_all(fee_records)
        db.commit()

        print("Sample data inserted successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()