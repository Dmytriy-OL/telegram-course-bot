import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_URL = os.getenv("SQLALCHEMY_URL")
