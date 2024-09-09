from datetime import date
from fastapi import FastAPI,APIRouter
from pydantic import BaseModel
import sqlite3
from typing import Optional


from .routers import player, match, round


db = sqlite3.connect('baza1.db')
cursor = db.cursor()


app = FastAPI()

app.include_router(player.routers)
app.include_router(match.routers)
app.include_router(round.routers)


#uvicorn app.main:app --reload
