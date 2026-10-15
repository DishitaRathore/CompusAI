import csv
from pathlib import Path

from sqlalchemy import select

from database import SessionLocal
from models import Attendance, Fee, Student


DATA_DIR = Path("data/raw")


def read_csv_file(
    filename,
    required_columns
):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open(
        "r",
        newline="",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                f"{filename} does not contain headers."
            )

        missing_columns = set(required_columns) - set(
            reader.fieldnames
        )

        if missing_columns:
            raise ValueError(
                f"{filename} is missing columns: "
                f"{missing_columns}"
            )

        return list(reader)


def import_students(db):
    rows = read_csv_file(
        "students.csv",
        ["id", "name", "course"]
    )

    inserted_count = 0

    for row in rows:
        student_id = int(row["id"])

        existing_student = db.get(
            Student,
            student_id
        )

        if existing_student is None:
            db.add(
                Student(
                    id=student_id,
                    name=row["name"].strip(),
                    course=row["course"].strip()
                )
            )

            inserted_count += 1

    db.commit()

    return inserted_count


def import_attendance(db):
    rows = read_csv_file(
        "attendance.csv",
        [
            "student_id",
            "subject",
            "attended",
            "total"
        ]
    )

    inserted_count = 0

    for row in rows:
        student_id = int(row["student_id"])
        subject = row["subject"].strip()
        attended = int(row["attended"])
        total = int(row["total"])

        if attended < 0 or total <= 0:
            raise ValueError(
                "Attendance values must be valid."
            )

        if attended > total:
            raise ValueError(
                "Attended classes cannot exceed total classes."
            )

        if db.get(Student, student_id) is None:
            raise ValueError(
                f"Student {student_id} does not exist."
            )

        existing_record = db.scalar(
            select(Attendance).where(
                Attendance.student_id == student_id,
                Attendance.subject == subject
            )
        )

        if existing_record is None:
            db.add(
                Attendance(
                    student_id=student_id,
                    subject=subject,
                    attended=attended,
                    total=total
                )
            )

            inserted_count += 1

    db.commit()

    return inserted_count


def import_fees(db):
    rows = read_csv_file(
        "fees.csv",
        [
            "student_id",
            "total_fee",
            "paid",
            "remaining"
        ]
    )

    inserted_count = 0

    for row in rows:
        student_id = int(row["student_id"])
        total_fee = float(row["total_fee"])
        paid = float(row["paid"])
        remaining = float(row["remaining"])

        if total_fee < 0 or paid < 0 or remaining < 0:
            raise ValueError(
                "Fee values cannot be negative."
            )

        if round(paid + remaining, 2) != round(
            total_fee,
            2
        ):
            raise ValueError(
                f"Fee values do not balance for "
                f"student {student_id}."
            )

        if db.get(Student, student_id) is None:
            raise ValueError(
                f"Student {student_id} does not exist."
            )

        existing_record = db.scalar(
            select(Fee).where(
                Fee.student_id == student_id
            )
        )

        if existing_record is None:
            db.add(
                Fee(
                    student_id=student_id,
                    total_fee=total_fee,
                    paid=paid,
                    remaining=remaining
                )
            )

            inserted_count += 1

    db.commit()

    return inserted_count


def main():
    db = SessionLocal()

    try:
        students_count = import_students(db)
        attendance_count = import_attendance(db)
        fees_count = import_fees(db)

        print("CSV data imported successfully.")
        print(f"Students inserted: {students_count}")
        print(f"Attendance records inserted: {attendance_count}")
        print(f"Fee records inserted: {fees_count}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()