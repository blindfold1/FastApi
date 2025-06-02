import pytest
from datetime import datetime
from bson import ObjectId
from backend.src.models.trainer import (
    TrainerCreate, WorkoutCreate, ProgressPostCreate
)
from backend.src.services.trainer_service import TrainerService
from backend.src.services.workout_service import WorkoutService
from backend.src.services.progress_service import ProgressService

@pytest.fixture
async def test_trainer():
    trainer_data = TrainerCreate(
        username="test_trainer",
        email="test@example.com",
        password="testpass123",
        specialization="CrossFit",
        experience_years=5,
        bio="Test bio"
    )
    return await TrainerService.create_trainer(trainer_data)

@pytest.fixture
async def test_workout(test_trainer):
    workout_data = WorkoutCreate(
        title="Test Workout",
        description="Test description",
        duration_minutes=60,
        difficulty="Intermediate",
        equipment_needed=["dumbbells", "bench"],
        target_muscle_groups=["chest", "triceps"]
    )
    return await WorkoutService.create_workout(str(test_trainer.id), workout_data)

@pytest.fixture
async def test_progress_post(test_trainer):
    post_data = ProgressPostCreate(
        title="Test Progress",
        content="Test content",
        before_image_url="before.jpg",
        after_image_url="after.jpg",
        metrics={"weight": 80, "body_fat": 15}
    )
    return await ProgressService.create_progress_post(str(test_trainer.id), post_data)

@pytest.mark.asyncio
async def test_create_trainer():
    trainer_data = TrainerCreate(
        username="new_trainer",
        email="new@example.com",
        password="newpass123",
        specialization="Yoga",
        experience_years=3,
        bio="New trainer bio"
    )
    trainer = await TrainerService.create_trainer(trainer_data)
    
    assert trainer.username == "new_trainer"
    assert trainer.email == "new@example.com"
    assert trainer.specialization == "Yoga"
    assert trainer.experience_years == 3
    assert trainer.bio == "New trainer bio"
    assert trainer.followers_count == 0
    assert trainer.following_count == 0
    assert not trainer.is_verified

@pytest.mark.asyncio
async def test_get_trainer(test_trainer):
    trainer = await TrainerService.get_trainer(str(test_trainer.id))
    
    assert trainer.id == str(test_trainer.id)
    assert trainer.username == "test_trainer"
    assert trainer.email == "test@example.com"

@pytest.mark.asyncio
async def test_create_workout(test_trainer):
    workout_data = WorkoutCreate(
        title="New Workout",
        description="New description",
        duration_minutes=45,
        difficulty="Beginner",
        equipment_needed=["mat"],
        target_muscle_groups=["core"]
    )
    workout = await WorkoutService.create_workout(str(test_trainer.id), workout_data)
    
    assert workout.title == "New Workout"
    assert workout.description == "New description"
    assert workout.duration_minutes == 45
    assert workout.difficulty == "Beginner"
    assert workout.equipment_needed == ["mat"]
    assert workout.target_muscle_groups == ["core"]
    assert workout.likes == 0
    assert workout.saves == 0

@pytest.mark.asyncio
async def test_get_workout(test_workout):
    workout = await WorkoutService.get_workout(str(test_workout.id))
    
    assert workout.id == str(test_workout.id)
    assert workout.title == "Test Workout"
    assert workout.description == "Test description"

@pytest.mark.asyncio
async def test_create_progress_post(test_trainer):
    post_data = ProgressPostCreate(
        title="New Progress",
        content="New content",
        before_image_url="new_before.jpg",
        after_image_url="new_after.jpg",
        metrics={"weight": 75, "body_fat": 12}
    )
    post = await ProgressService.create_progress_post(str(test_trainer.id), post_data)
    
    assert post.title == "New Progress"
    assert post.content == "New content"
    assert post.before_image_url == "new_before.jpg"
    assert post.after_image_url == "new_after.jpg"
    assert post.metrics == {"weight": 75, "body_fat": 12}
    assert post.likes == 0
    assert post.comments == 0

@pytest.mark.asyncio
async def test_get_progress_post(test_progress_post):
    post = await ProgressService.get_progress_post(str(test_progress_post.id))
    
    assert post.id == str(test_progress_post.id)
    assert post.title == "Test Progress"
    assert post.content == "Test content"

@pytest.mark.asyncio
async def test_follow_trainer(test_trainer):
    # Create another trainer to follow
    follower_data = TrainerCreate(
        username="follower",
        email="follower@example.com",
        password="follower123",
        specialization="Pilates",
        experience_years=2,
        bio="Follower bio"
    )
    follower = await TrainerService.create_trainer(follower_data)
    
    # Follow the test trainer
    result = await TrainerService.follow_trainer(str(follower.id), str(test_trainer.id))
    assert result["message"] == "Successfully followed trainer"
    
    # Check followers
    followers = await TrainerService.get_followers(str(test_trainer.id))
    assert len(followers) == 1
    assert followers[0].username == "follower"

@pytest.mark.asyncio
async def test_like_workout(test_workout):
    result = await WorkoutService.like_workout(str(test_workout.id))
    assert result["message"] == "Workout liked successfully"
    
    workout = await WorkoutService.get_workout(str(test_workout.id))
    assert workout.likes == 1

@pytest.mark.asyncio
async def test_like_progress_post(test_progress_post):
    result = await ProgressService.like_progress_post(str(test_progress_post.id))
    assert result["message"] == "Progress post liked successfully"
    
    post = await ProgressService.get_progress_post(str(test_progress_post.id))
    assert post.likes == 1 