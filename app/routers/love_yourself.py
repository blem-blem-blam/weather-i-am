from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/kiss", response_model=str)
async def kiss_for_you():
    return "Secret kisses for you <3"


@router.get("/", response_model=str)
async def thank_you():
    return "Double secret kisses for you <3"
