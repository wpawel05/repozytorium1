from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from shapely import wkb, wkt 
from fastapi.encoders import jsonable_encoder
from models import Room, RoomCreate, RoomUpdate
from db_config import ORMBaseModel, db_engine, get_db_session
from encoders import to_dict
import os

DATABASE_URL = os.getenv("DATABASE_URL")
app = FastAPI()

ORMBaseModel.metadata.create_all(bind=db_engine)
@app.get("/")
def test():
    return {"message": "Elo Elo 320!"}

@app.post("/rooms")
def create_room(room_create: RoomCreate, db_session: Session = Depends(get_db_session)):
    new_room = Room(
        number = room_create.number,
        room_category_id = room_create.room_category_id,
        floor_id = room_create.floor_id
    )
    db_session.add(new_room)
    db_session.commit()
    db_session.refresh(new_room)
    return jsonable_encoder ({
        "id": new_room.id,
        "number": new_room.number,
        "room_category_id":new_room.room_category_id,
        "floor_id": new_room.floor_id
    })

@app.get("/rooms")
def get_all_rooms(db_session: Session = Depends(get_db_session)):
    rooms = db_session.query(Room).all()
    result = []
    for room in rooms:
        room_dict = to_dict(room)
        result.append(room_dict)
    return jsonable_encoder(result)

@app.get("/rooms/{room_id}")
def get_room(room_id: int, db_session: Session = Depends(get_db_session)):
    room = db_session.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return to_dict(room)

@app.put("/rooms/{room_id}")
def update_room(room_id: int, room_update: RoomUpdate, db_session: Session = Depends(get_db_session)):
    room = db_session.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    room.number = room_update.number
    room.room_category_id = room_update.room_category_id
    room.floor_id = room_update.floor_id
    db_session.commit()
    db_session.refresh(room)
    return to_dict(room)



@app.delete("/rooms/{room_id}")
def delete_room(room_id: int, db_session: Session = Depends(get_db_session)):
    room = db_session.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    db_session.delete(room)
    db_session.commit()
    return jsonable_encoder({"message": "Room deleted"})
