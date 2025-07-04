from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder


from server.database import student_collection
from server.models.student import (
    ErrorResponseModel,
    ResponseModel,
    StudentSchema,
    UpdateStudentModel,
)

router = APIRouter()

@router.post("/", response_description="Student data added into the database")
async def add_student_data(student: StudentSchema = Body(...)):
    student = jsonable_encoder(student)
    new_student = await student_collection.add_student(student)
    return ResponseModel(new_student, "Student added successfully.")

@router.get("/", response_description="Students retrieved")
async def get_students():
    students = await student_collection.retrieve_all()
    if students:
        return ResponseModel(students, "Students data retrieved successfully")
    return ResponseModel(students, "Empty list returned")

@router.get("/{id}", response_description="Student data retrieved")
async def get_student_data(id: str):
    student = await student_collection.retrieve_by_id(id)
    if student:
        return ResponseModel(student, "Student data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "Student doesn't exist.")

@router.put("/{id}")
async def update_student_data(id: str, req: UpdateStudentModel = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_student = await student_collection.update_student(id, req)
    if updated_student:
        return ResponseModel(
            f"Student with ID: {id} name update is successful",
            "Student name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the student data.",
    )

@router.delete("/{id}", response_description="Student data deleted from the database")
async def delete_student_data(id: str):
    deleted_student = await student_collection.delete_student(id)
    if deleted_student:
        return ResponseModel(
            f"Student with ID: {id} removed", "Student deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "Student with id {0} doesn't exist".format(id)
    )
