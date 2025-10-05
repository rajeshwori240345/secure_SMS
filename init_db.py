from app import create_app, db
from app.models import User, Student, Teacher
from app.encryption import encrypt_text

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    # Users
    admin = User(username="admin", email="admin@example.com", role="admin")
    admin.set_password("Admin@123")
    teacher = User(username="teacher1", email="teacher1@example.com", role="teacher")
    teacher.set_password("Teacher@123")
    student_user = User(username="student1", email="student1@example.com", role="student")
    student_user.set_password("Student@123")
    db.session.add_all([admin, teacher, student_user])
    # Teachers
    t1 = Teacher(name="Alice Johnson", email="alice.j@example.com", department="Mathematics")
    t2 = Teacher(name="Bob Smith", email="bob.s@example.com", department="Science")
    db.session.add_all([t1, t2])
    # Students
    s1 = Student(name="John Doe", email="john.doe@example.com", grade="A", address_encrypted=encrypt_text("123 Main St"))
    s2 = Student(name="Jane Roe", email="jane.roe@example.com", grade="B", address_encrypted=encrypt_text("456 Pine Ave"))
    s3 = Student(name="Sam Park", email="sam.park@example.com", grade="C", address_encrypted=encrypt_text("789 Oak Rd"))
    s4 = Student(name="Nina Patel", email="nina.patel@example.com", grade="B", address_encrypted=encrypt_text("1010 Maple Blvd"))
    db.session.add_all([s1, s2, s3, s4])
    db.session.commit()
    print("Database initialized with sample data.")
