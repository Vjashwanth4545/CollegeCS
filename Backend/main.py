from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uuid
from logic import process_complaint

app = FastAPI()

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dummy Student DB ---
students_db = [
    {
        "id": "S001",
        "name": "Jashwanth",
        "password": "1234",
        "complaints": []
    },
    {
        "id": "S002",
        "name": "Rahul",
        "password": "abcd",
        "complaints": []
    }
]

# --- Management DB ---
management_db = [
    {"role": "dean", "password": "1111"},
    {"role": "warden", "password": "2222"},
    {"role": "it_head", "password": "3333"},
    {"role": "security", "password": "4444"}
]

# --- Models ---
class LoginRequest(BaseModel):
    password: str

class AdminLogin(BaseModel):
    role: str
    password: str

class Complaint(BaseModel):
    student_id: str
    text: str


# --- Student Login ---
@app.post("/login")
def login(req: LoginRequest):
    student = next((s for s in students_db if s["password"] == req.password), None)

    if not student:
        return {"success": False, "message": "Invalid password"}

    return {
        "success": True,
        "student_id": student["id"],
        "name": student["name"]
    }


# --- Management Login ---
@app.post("/admin-login")
def admin_login(req: AdminLogin):
    admin = next(
        (a for a in management_db if a["role"] == req.role and a["password"] == req.password),
        None
    )

    if not admin:
        return {"success": False, "message": "Invalid credentials"}

    return {"success": True, "role": req.role}


# --- Simple Category Logic (AI Placeholder) ---
def detect_category(text: str):
    text = text.lower()

    if "fan" in text or "room" in text:
        return "Hostel Issues"
    elif "wifi" in text or "internet" in text:
        return "Infrastructure"
    elif "marks" in text or "exam" in text:
        return "Academic Issues"
    else:
        return "Discipline"


# --- Add Complaint ---
@app.post("/complaint")
def add_complaint(c: Complaint):
    student = next((s for s in students_db if s["id"] == c.student_id), None)

    if not student:
        return {"error": "Student not found"}

    # ✅ GET NAME
    student_name = student["name"]

    # ✅ CALL AI WITH NAME
    ai_result = process_complaint(c.text, student_name)

    new_complaint = {
        "id": str(uuid.uuid4()),
        "complaint": c.text,
        "category": ai_result["category"],
        "status": ai_result["status"],
        "assigned_to": ai_result["assigned_to"],
        "letter": ai_result["letter"]
    }

    student["complaints"].append(new_complaint)

    return {
        "message": "Complaint added",
        "data": new_complaint
    }


# --- Get Student Complaints ---
@app.get("/complaints/{student_id}")
def get_complaints(student_id: str):
    student = next((s for s in students_db if s["id"] == student_id), None)

    if not student:
        return {"error": "Student not found"}

    return student["complaints"]


# --- Get Complaints by Role (🔥 IMPORTANT FEATURE) ---
@app.get("/admin-complaints/{role}")
def get_admin_complaints(role: str):
    role_map = {
        "dean": "Academic Issues",
        "warden": "Hostel Issues",
        "it_head": "Infrastructure",
        "security": "Discipline"
    }

    category = role_map.get(role)

    if not category:
        return {"error": "Invalid role"}

    result = []

    for student in students_db:
        for complaint in student["complaints"]:
            if complaint["category"] == category:
                result.append({
                    "student": student["name"],
                    **complaint
                })

    return result

@app.get("/student/{student_id}")
def get_student(student_id: str):
    student = next((s for s in students_db if s["id"] == student_id), None)

    if not student:
        return {"error": "Student not found"}

    return {
        "id": student["id"],
        "name": student["name"]
    }
@app.put("/update-status/{complaint_id}")
def update_status(complaint_id: str):
    for student in students_db:
        for complaint in student["complaints"]:
            if complaint["id"] == complaint_id:
                complaint["status"] = "Resolved"
                return {"message": "Updated"}

    return {"error": "Not found"}