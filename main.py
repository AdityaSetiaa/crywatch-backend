from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base
from models import User
from schemas import UserCreate, UserLogin, UserResponse
from auth import hash_password, verify_password, create_token, get_db, get_current_user
from watchlist import router as watchlist_router

from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/signup")
def signup(data: UserCreate, db: Session = Depends(get_db)):
    print("SIGNUP RECEIVED:", data.email)

    existing = db.query(User).filter(User.email == data.email).first()
    print("EXISTING USER:", existing)

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(data.password)
    
    user = User(
        name=data.name,
        email=data.email,
        password=hashed_pw
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token({"user_id": user.id, "email": user.email})
    return {"message": "User created successfully", "token": token}


@app.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    print("LOGIN ATTEMPT:", data.email, data.password)

    user = db.query(User).filter(User.email == data.email).first()
    print("DB USER:", user)

    if not user:
        print("USER NOT FOUND")
    else:
        print("HASHED PW:", user.password)

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token({"user_id": user.id, "email": user.email})
    return {"token": token}

@app.get("/profile", response_model=UserResponse)
def get_profile(user=Depends(get_current_user)):
    return user


@app.put("/profile", response_model=UserResponse)
def update_profile(update: UserCreate, db: Session = Depends(get_db),
                   user=Depends(get_current_user)):
    user.name = update.name
    user.email = update.email
    user.password = hash_password(update.password)
    db.commit()
    db.refresh(user)
    return user



app.include_router(watchlist_router, prefix="/watchlist", tags=["Watchlist"])
