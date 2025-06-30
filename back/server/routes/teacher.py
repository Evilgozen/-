from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from server.database import teacher_collection
from server.models.teacher import (
    ErrorResponseModel,
    ResponseModel,
    TeacherSchema,
    UpdateTeacherModel,
)

router = APIRouter()

@router.post("/", response_description="Teacher data added into the database")
async def add_teacher_data(teacher: TeacherSchema = Body(...)):
    teacher = jsonable_encoder(teacher)
    new_teacher = await teacher_collection.add_teacher(teacher)
    return ResponseModel(new_teacher, "Teacher added successfully.")

@router.get("/", response_description="Teachers retrieved")
async def get_teachers():
    teachers = await teacher_collection.retrieve_all()
    if teachers:
        return ResponseModel(teachers, "Teachers data retrieved successfully")
    return ResponseModel(teachers, "Empty list returned")

@router.get("/{id}", response_description="Teacher data retrieved")
async def get_teacher_data(id: str):
    teacher = await teacher_collection.retrieve_by_id(id)
    if teacher:
        return ResponseModel(teacher, "Teacher data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "Teacher doesn't exist.")

@router.put("/{id}")
async def update_teacher_data(id: str, req: UpdateTeacherModel = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_teacher = await teacher_collection.update_teacher(id, req)
    if updated_teacher:
        return ResponseModel(
            f"Teacher with ID: {id} update is successful",
            "Teacher updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the teacher data.",
    )

@router.delete("/{id}", response_description="Teacher data deleted from the database")
async def delete_teacher_data(id: str):
    deleted_teacher = await teacher_collection.delete_teacher(id)
    if deleted_teacher:
        return ResponseModel(
            f"Teacher with ID: {id} removed", "Teacher deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "Teacher with id {0} doesn't exist".format(id)
    )

@router.post("/search/school_level", response_description="Teachers retrieved by school level")
async def get_teachers_by_school_level(school_level: str = Body(..., embed=True)):
    teachers = await teacher_collection.find_by_school_level(school_level)
    if teachers:
        return ResponseModel(teachers, f"Teachers with school level '{school_level}' retrieved successfully")
    return ResponseModel([], "No teachers found with the specified school level")

@router.post("/search/school", response_description="Teachers retrieved by school")
async def get_teachers_by_school(school: str = Body(..., embed=True)):
    teachers = await teacher_collection.find_by_school(school)
    if teachers:
        return ResponseModel(teachers, f"Teachers from school '{school}' retrieved successfully")
    return ResponseModel([], "No teachers found from the specified school")
