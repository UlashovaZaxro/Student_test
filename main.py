from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import statistics
import uvicorn

app = FastAPI(title="Student Application Testing System")


class Student(BaseModel):
    id: int = Field(..., description="Unique identifier for the student")
    name: str = Field(..., min_length=2, max_length=50, description="Student's full name")
    email: str = Field(..., description="Student's email address")
    tests_taken: List[int] = []

class Test(BaseModel):
    id: int = Field(..., description="Unique identifier for the test")
    name: str = Field(..., min_length=2, max_length=100, description="Name of the test")
    max_score: int = Field(..., description="Maximum possible score")

class TestResult(BaseModel):
    student_id: int = Field(..., description="ID of the student taking the test")
    test_id: int = Field(..., description="ID of the test taken")
    score: int = Field(..., description="Score obtained in the test")

class ResponseMessage(BaseModel):
    message: str
    
students: Dict[int, Student] = {}
tests: Dict[int, Test] = {}
test_results: List[TestResult] = []

@app.post("/students/", response_model=Student)
async def create_student(student: Student):
    if student.id in students:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    students[student.id] = student
    return student

@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return students[student_id]

@app.get("/students/", response_model=List[Student])
async def get_all_students():
    return list(students.values())

@app.delete("/students/{student_id}", response_model=ResponseMessage)
async def delete_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    del students[student_id]
    return ResponseMessage(message="Student deleted successfully")

# Test Endpoints
@app.post("/tests/", response_model=Test)
async def create_test(test: Test):
    if test.id in tests:
        raise HTTPException(status_code=400, detail="Test ID already exists")
    tests[test.id] = test
    return test

@app.get("/tests/{test_id}", response_model=Test)
async def get_test(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    return tests[test_id]

@app.get("/tests/", response_model=List[Test])
async def get_all_tests():
    return list(tests.values())

@app.post("/results/", response_model=TestResult)
async def submit_test_result(result: TestResult):
    if result.student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    if result.test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    if result.score > tests[result.test_id].max_score:
        raise HTTPException(status_code=400, detail="Score exceeds maximum possible score")
    
    test_results.append(result)
    students[result.student_id].tests_taken.append(result.test_id)
    return result

@app.get("/results/student/{student_id}", response_model=List[TestResult])
async def get_student_results(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return [result for result in test_results if result.student_id == student_id]

@app.get("/results/test/{test_id}", response_model=List[TestResult])
async def get_test_results(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    return [result for result in test_results if result.test_id == test_id]

@app.get("/results/test/{test_id}/o'rtacha", response_model=float)
async def get_test_average(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    test_scores = [result.score for result in test_results if result.test_id == test_id]
    if not test_scores:
        raise HTTPException(status_code=404, detail="No results found for this test")
    return statistics.mean(test_scores)

@app.get("/results/test/{test_id}/eng_yuqori", response_model=int)
async def get_test_highest(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    test_scores = [result.score for result in test_results if result.test_id == test_id]
    if not test_scores:
        raise HTTPException(status_code=404, detail="No results found for this test")
    return max(test_scores)

@app.get("/results/test/{test_id}/eng_pasti", response_model=int)
async def get_test_lowest(test_id: int):
    if test_id not in tests:
        raise HTTPException(status_code=404, detail="Test not found")
    test_scores = [result.score for result in test_results if result.test_id == test_id]
    if not test_scores:
        raise HTTPException(status_code=404, detail="No results found for this test")
    return min(test_scores)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)