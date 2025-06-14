# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text  # <--- 確保這行存在，為 db-test 端點所需
from typing import List

import crud
import models
import schemas
from database import SessionLocal, engine, get_db

# 建立資料庫資料表 (如果不存在)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PostgreSQL CRUD API",
    description="一個使用 FastAPI 與 PostgreSQL 進行 CRUD 操作的範例。",
    version="1.0.0",
)

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