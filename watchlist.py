from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user, get_db
from models import WatchlistItem
from schemas import WatchlistCreate, WatchlistUpdate, WatchlistResponse

router = APIRouter()

@router.get("/", response_model=list[WatchlistResponse])
def get_items(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id).all()

@router.post("/", response_model=WatchlistResponse)
def create_item(data: WatchlistCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    item = WatchlistItem(**data.dict(), user_id=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/{item_id}", response_model=WatchlistResponse)
def update_item(item_id: int, data: WatchlistUpdate, 
                db: Session = Depends(get_db), user=Depends(get_current_user)):
    
    item = db.query(WatchlistItem).filter(
        WatchlistItem.id == item_id, WatchlistItem.user_id == user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in data.dict().items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):

    item = db.query(WatchlistItem).filter(
        WatchlistItem.id == item_id, WatchlistItem.user_id == user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
