from typing import Union
from fastapi import FastAPI
import uvicorn
from typing import Union

from fastapi.middleware.cors import CORSMiddleware
from server.routes.student import router as StudentRouter
from server.routes.teacher import router as TeacherRouter
from server.routes.smtp import router as SMTPRouter
from server.routes.file import router as FileRouter

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(StudentRouter, tags=["Student"], prefix="/students")
app.include_router(TeacherRouter, tags=["Teacher"], prefix="/teacher")
app.include_router(SMTPRouter, tags=["SMTP"], prefix="/smtp")
app.include_router(FileRouter, tags=["File"], prefix="/files")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)