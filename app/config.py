from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")
SERECT_KEY=os.getenv("SERECT_KEY")

if  not DATABASE_URL:
    raise ValueError("Database url is not configured")
if not SERECT_KEY:
    raise ValueError("Serect key is not configured")