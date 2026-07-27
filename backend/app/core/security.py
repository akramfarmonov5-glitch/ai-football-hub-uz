import secrets
from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import settings


def verify_admin(x_admin_token: Optional[str] = Header(default=None)) -> bool:
    """FastAPI dependency: ma'lumot o'zgartiradigan endpointlarni himoyalaydi.

    Ikki muhim jihat:
      * ADMIN_TOKEN sozlanmagan bo'lsa hamma so'rov rad etiladi (fail-closed) —
        standart parol bilan ochiq qolib ketish holati bo'lmaydi.
      * Solishtirish `secrets.compare_digest` orqali, ya'ni vaqt bo'yicha
        (timing) hujumga chidamli.
    """
    expected = settings.ADMIN_TOKEN
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "ADMIN_TOKEN sozlanmagan. backend/.env faylida uni belgilang "
                "(namuna uchun backend/.env.example ga qarang)."
            ),
        )

    if not x_admin_token or not secrets.compare_digest(x_admin_token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri yoki yo'q admin token (X-Admin-Token).",
        )
    return True
