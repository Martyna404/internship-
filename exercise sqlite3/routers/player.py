from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from datetime import date
 
app = FastAPI()
routers = APIRouter()
 
class Player(BaseModel):
    id: Optional[int] = None
    name: str
    surname: str
 
def get_db_connection():
    return sqlite3.connect('baza1.db')
 
@routers.put("/player/", response_model=Player)
async def create_player(player: Player):
    conn = get_db_connection()
    cursor = conn.cursor()
 
    try:
        cursor.execute("""
            INSERT INTO player (id,name,surname)
            VALUES (?, ?, ?)
            RETURNING *;
        """, (player.id,player.name, player.surname))
       
        inserted_row = cursor.fetchone()  
 
        conn.commit()
 
        if inserted_row is None:
            raise HTTPException(status_code=500, detail="Problem creating new recorD")
         
        
        created_player = Player(
            id=inserted_row[0],
            name=inserted_row[1],
            surname=inserted_row[2]
        )
 
    except sqlite3.Error as e:
        conn.rollback()  
        raise HTTPException(status_code=500, detail=str(e))
   
    return created_player
 
 
@routers.post("/player/", response_model=Player)
async def replace_player(player: Player):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM player WHERE id = ?", (player.id,))
        existing_match = cursor.fetchone()

        if existing_match:
            cursor.execute("""
                UPDATE player
                SET id=?, name=?, surname=?
                WHERE id = ?
                RETURNING id, name, surname;
            """, (player.id, player.name, player.surname, player.id)) 

            updated_row = cursor.fetchone()
            conn.commit()

            created_player = Player(
                id=updated_row[0],
                name=str(updated_row[1]),
                surname=str(updated_row[2])
            )

    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return created_player

 
 
@routers.get("/player/", response_model=List[Player])
async def get_player():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """ 
            SELECT id, name, surname
            FROM player
            """ )
        rows = cursor.fetchall()
        conn.commit()
 
        
        matches = [Player(id=row[0], name=row[1],surname=row[2]) for row in rows]
 
    except sqlite3.Error as e:
        conn.rollback()  
        raise HTTPException(status_code=500, detail=str(e))
 
    return matches
