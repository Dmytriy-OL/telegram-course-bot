import itsdangerous
import os
from dotenv import load_dotenv

load_dotenv()

serializer = itsdangerous.URLSafeTimedSerializer(os.getenv("SECRET_KEY"))


def generate_token(email: str) -> str:
    return serializer.dumps(email, salt="email-confirm")


def verify_token(token: str, max_age: int = 3600) -> str | None:
    try:
        return serializer.loads(token, salt="email-confirm", max_age=max_age)
    except itsdangerous.BadSignature:
        return None
