"""Auth routes — scaffolding for future JWT / OAuth."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.user import TokenResponse, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    include_in_schema=True,
)
async def register(payload: UserCreate) -> UserRead:
    """Placeholder — user registration will land with full auth."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication is not enabled yet. Coming soon.",
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def login() -> TokenResponse:
    """Placeholder — JWT login will land with full auth."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication is not enabled yet. Coming soon.",
    )
