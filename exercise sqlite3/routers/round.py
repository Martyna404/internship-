from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from datetime import date
 
app = FastAPI()
routers = APIRouter()
 
class Round(BaseModel):
    id: Optional[int] = None  
    date: date
    name: str
    no: int
 
def get_db_connection():
    return sqlite3.connect('baza1.db')
 
@routers.put("/round/", response_model=Round)
async def create_round(round: Round):
    conn = get_db_connection()
    cursor = conn.cursor()
 
    try:
        cursor.execute("""
            INSERT INTO round (id, date, name, no)
            VALUES (?, ?, ?, ?)
            RETURNING id, date, name, no;
        """, (round.id, round.date, round.name, round.no))
       
        inserted_row = cursor.fetchone()  
 
        conn.commit()
 
        if inserted_row is None:
            raise HTTPException(status_code=500, detail="Problem creating new recorD")
         
        
        created_round = Round(
            id=inserted_row[0],
            date=inserted_row[1],
            name=inserted_row[2],
            no=inserted_row[3]
        )
 
    except sqlite3.Error as e:
        conn.rollback()  
        raise HTTPException(status_code=500, detail=str(e))
   
    return created_round
 
 
@routers.post("/round/", response_model=List[Round])
async def replace_round(round: Round):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM round WHERE id = ?", (round.id,))
        existing_match = cursor.fetchone()
        
        if existing_match:
            cursor.execute("""
                UPDATE round
                SET date = ?, name = ?, no = ?
                WHERE id = ?
                RETURNING id, date, name, no;
            """, (round.date, round.name, round.no, round.id))
            
            updated_row = cursor.fetchone()
            conn.commit()
            
            
            created_round = Round(
                id=updated_row[0],
                date=updated_row[1],
                name=str(updated_row[2]),  
                no=int(updated_row[3])     
            )
    
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    
    return created_round
 
 
@routers.get("/round/",response_model=List[Round])
async def get_rounds():
    conn=get_db_connection()
    cursor=conn.cursor()

    try:
        cursor.execute(
                """ SELECT id, date, name, no
                FROM round
    """
            )
        rows=cursor.fetchall()
        conn.commit()
 
        matches = [Round(id=row[0], date=row[1], name=row[2], no=row[3]) for row in rows]
 
    except sqlite3.Error as e:
        conn.rollback()  
        raise HTTPException(status_code=500, detail=str(e))
 
   
    return matches
