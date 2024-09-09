from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from datetime import date
 
routers = APIRouter()
 
class Match(BaseModel):
    id: Optional[int] = None
    round_id: int
    player_id: int
    order_no: int
 
def get_db_connection():
    return sqlite3.connect('baza1.db')
 
@routers.put("/match/", response_model=Match)
async def create_match(match: Match):
    conn = get_db_connection()
    cursor = conn.cursor()
 
    try:
        cursor.execute("""
            INSERT INTO match (id,round_id, player_id, order_no)
            VALUES (?, ?, ?,?)
            RETURNING *;
        """, (match.id,match.round_id, match.player_id, match.order_no))
       
        inserted_row = cursor.fetchone()  
 
        conn.commit()
 
        if inserted_row is None:
            raise HTTPException(status_code=500, detail="Problem creating new recorD")
         
        
        created_match = Match(
            id=inserted_row[0],
            round_id=inserted_row[1],
            player_id=inserted_row[2],
            order_no=inserted_row[3]
        )
 
    except sqlite3.Error as e:
        conn.rollback()  
        raise HTTPException(status_code=500, detail=str(e))
   
    return created_match
 
 
@routers.post("/match/", response_model=Match)
async def replace_match(match: Match):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM match WHERE id = ?", (match.id,))
        existing_match = cursor.fetchone()
        
        if existing_match:
            cursor.execute("""
                UPDATE match
                SET round_id = ?, player_id = ?, order_no = ?
                WHERE id = ?
                RETURNING id,round_id, player_id, order_no;
            """, (match.id, match.round_id, match.player_id, match.order_no))
            
            updated_row = cursor.fetchone()
            conn.commit()
            
            
            created_match = Match(
                id=updated_row[0],
                round_id=int(updated_row[1]),
                player_id=int(updated_row[2]),  
                order_no=int(updated_row[3])     
            )
    
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    
    return created_match
 
 
@routers.get("/match/", response_model=List[Match])
async def get_match():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """ 
            SELECT id, round_id, player_id, order_no
            FROM match
            """ )
        rows = cursor.fetchall()
        conn.commit()
 
        
        matches = [Match(id=row[0], round_id=row[1], player_id=row[2], order_no=row[3]) for row in rows]
 
    except sqlite3.Error as e:
        conn.rollback()  
        raise HTTPException(status_code=500, detail=str(e))
 
    return matches
