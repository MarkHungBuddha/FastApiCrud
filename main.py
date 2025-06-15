# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text  # <--- 確保這行存在，為 db-test 端點所需
from typing import List

import auth
import crud
import models
import schemas
import security
from database import SessionLocal, engine, get_db

# 建立資料庫資料表 (如果不存在)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PostgreSQL CRUD API",
    description="一個使用 FastAPI 與 PostgreSQL 進行 CRUD 操作的範例。",
    version="1.0.0",
)


# ===============================================================
#  使用者認證 (Authentication)
# ===============================================================

@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)  # 表單的 username 欄位對應我們的 email
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="不正確的 email 或密碼",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User, tags=["Authentication"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email 已被註冊")
    return crud.create_user(db=db, user=user)


# ===============================================================
#  健康檢查 / 資料庫連線測試端點 (Health Check / DB Test Endpoint)
# ===============================================================
@app.get("/db-test", tags=["Health Check"])
def test_database_connection(db: Session = Depends(get_db)):
    """
    一個簡單的端點，用來測試資料庫連線。
    """
    try:
        # 使用 text() 將 SQL 字串包裝起來
        db.execute(text('SELECT 1'))
        return {"status": "success", "message": "資料庫連線成功！"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料庫連線失敗: {e}")


# ===============================================================
#  CRUD 端點 (CRUD Endpoints for Items)
# ===============================================================

# Create
@app.post("/items/", response_model=schemas.Item, status_code=201, tags=["Items"])
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)


# Read (All)
@app.get("/items/", response_model=List[schemas.Item], tags=["Items"])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


# Read (Single)
@app.get("/items/{item_id}", response_model=schemas.Item, tags=["Items"])
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="找不到該項目")
    return db_item


# Update
@app.put("/items/{item_id}", response_model=schemas.Item, tags=["Items"])
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = crud.update_item(db, item_id, item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="找不到該項目")
    return db_item


# Delete
@app.delete("/items/{item_id}", status_code=204, tags=["Items"])
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.delete_item(db, item_id=item_id)
    if db_item is None:
        pass
    return
