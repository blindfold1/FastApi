from fastapi import APIRouter, Depends, HTTPException, status, Query
from ...models.exercise import ExerciseCreate, ExerciseResponse
from ...services.exercise_service import ExerciseService
from ...core.security import auth_handler

router = APIRouter(prefix="/exercises", tags=["exercises"])

@router.post("/", response_model=ExerciseResponse)
async def create_exercise(exercise: ExerciseCreate, current_user=Depends(auth_handler.get_current_user)):
    if current_user["role"] not in ("trainer", "admin"):
        raise HTTPException(status_code=403, detail="Only trainers or admins can add exercises")
    return await ExerciseService.create_exercise(exercise, created_by=current_user["username"])

@router.get("/", response_model=list[ExerciseResponse])
async def get_exercises(skip: int = 0, limit: int = 100, search: str = Query(None)):
    return await ExerciseService.get_exercises(skip=skip, limit=limit, search=search)

@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(exercise_id: str):
    return await ExerciseService.get_exercise(exercise_id)

@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(exercise_id: str, exercise: ExerciseCreate, current_user=Depends(auth_handler.get_current_user)):
    if current_user["role"] not in ("trainer", "admin"):
        raise HTTPException(status_code=403, detail="Only trainers or admins can update exercises")
    return await ExerciseService.update_exercise(exercise_id, exercise)

@router.delete("/{exercise_id}")
async def delete_exercise(exercise_id: str, current_user=Depends(auth_handler.get_current_user)):
    if current_user["role"] not in ("trainer", "admin"):
        raise HTTPException(status_code=403, detail="Only trainers or admins can delete exercises")
    return await ExerciseService.delete_exercise(exercise_id) 