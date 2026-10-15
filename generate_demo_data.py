import csv
import random
from pathlib import Path

from faker import Faker


random.seed(42)
Faker.seed(42)

fake = Faker("en_IN")

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

STUDENT_COUNT = 100
START_STUDENT_ID = 1001

COURSES = [
    "Computer Science",
    "Information Technology",
    "Artificial Intelligence",
    "Data Science",
    "Cybersecurity"
]

SUBJECTS = [
    "Machine Learning",
    "Database Systems",
    "Computer Networks",
    "Operating Systems"
]


def generate_students():
    students = []

    for student_id in range(
        START_STUDENT_ID,
        START_STUDENT_ID + STUDENT_COUNT
    ):
        students.append(
            {
                "id": student_id,
                "name": fake.name(),
                "course": random.choice(COURSES)
            }
        )

    file_path = DATA_DIR / "students.csv"

    with file_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "name",
                "course"
            ]
        )

        writer.writeheader()
        writer.writerows(students)

    return students


def generate_attendance(students):
    attendance_records = []

    for student in students:
        for subject in SUBJECTS:
            total_classes = random.randint(20, 30)
            attendance_rate = random.uniform(0.60, 0.98)
            attended_classes = int(
                total_classes * attendance_rate
            )

            attendance_records.append(
                {
                    "student_id": student["id"],
                    "subject": subject,
                    "attended": attended_classes,
                    "total": total_classes
                }
            )

    file_path = DATA_DIR / "attendance.csv"

    with file_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "student_id",
                "subject",
                "attended",
                "total"
            ]
        )

        writer.writeheader()
        writer.writerows(attendance_records)


def generate_fees(students):
    fee_records = []

    for student in students:
        total_fee = 100000
        paid_amount = random.choice(
            range(0, total_fee + 1, 5000)
        )

        fee_records.append(
            {
                "student_id": student["id"],
                "total_fee": total_fee,
                "paid": paid_amount,
                "remaining": total_fee - paid_amount
            }
        )

    file_path = DATA_DIR / "fees.csv"

    with file_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "student_id",
                "total_fee",
                "paid",
                "remaining"
            ]
        )

        writer.writeheader()
        writer.writerows(fee_records)


def main():
    students = generate_students()
    generate_attendance(students)
    generate_fees(students)

    print("Synthetic ERP data generated successfully.")
    print(f"Students created: {len(students)}")
    print("Files created inside data/raw/")


if __name__ == "__main__":
    main()