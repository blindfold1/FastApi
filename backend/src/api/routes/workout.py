from fastapi import APIRouter, Depends, HTTPException, status
from ...models.workout import WorkoutCreate, WorkoutResponse
from ...services.workout_service import WorkoutService
from ...core.security import auth_handler

router = APIRouter(prefix="/workouts", tags=["workouts"])

@router.post("/", response_model=WorkoutResponse)
async def create_workout(workout: WorkoutCreate, current_user=Depends(auth_handler.get_current_user)):
    return await WorkoutService.create_workout(workout, user_id=str(current_user["_id"]))

@router.get("/", response_model=list[WorkoutResponse])
async def get_workouts(current_user=Depends(auth_handler.get_current_user)):
    return await WorkoutService.get_workouts(user_id=str(current_user["_id"]))

@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(workout_id: str, current_user=Depends(auth_handler.get_current_user)):
    workout = await WorkoutService.get_workout(workout_id)
    if workout.user_id != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to view this workout")
    return workout

@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(workout_id: str, workout: WorkoutCreate, current_user=Depends(auth_handler.get_current_user)):
    return await WorkoutService.update_workout(workout_id, workout, user_id=str(current_user["_id"]))

@router.delete("/{workout_id}")
async def delete_workout(workout_id: str, current_user=Depends(auth_handler.get_current_user)):
    return await WorkoutService.delete_workout(workout_id, user_id=str(current_user["_id"])) 