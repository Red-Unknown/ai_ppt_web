from fastapi import APIRouter, Depends, HTTPException
from backend.app.schemas.student import StudentProfile, CreateProfileRequest, UpdateProfileRequest
from backend.app.services.student.state_manager import StudentStateManager

router = APIRouter()

# Mock dependency
def get_current_user_id():
    # In real app, extract from JWT token
    return "student_001"

@router.post("/profile", response_model=StudentProfile)
async def create_or_update_profile(
    profile_data: UpdateProfileRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create or update the student's learning profile.
    """
    profile = StudentStateManager.create_or_update_profile(
        user_id=user_id,
        profile_data=profile_data.dict(exclude_unset=True)
    )
    return profile

@router.get("/profile", response_model=StudentProfile)
async def get_profile(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get the current student's profile.
    """
    profile = StudentStateManager.get_profile(user_id)
    if not profile:
        # Return default profile if not exists
        return StudentStateManager.create_or_update_profile(user_id, {})
    return profile
