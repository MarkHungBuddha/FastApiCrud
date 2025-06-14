from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import database

# 1. 初始化 FastAPI 應用程式
app = FastAPI(
    title="基本 CRUD API",
    description="一個使用 FastAPI 建立的簡單 CRUD 操作範例。",
    version="1.0.0",
)


# 2. 定義資料模型 (Pydantic Model)
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None  # 可選欄位


class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None


# 3. 建立一個簡單的記憶體資料庫
db: List[Item] = [
    Item(id=1, name="範例項目 1", description="這是第一個項目"),
    Item(id=2, name="範例項目 2", description="這是第二個項目"),
]

@app.get("/db-test")
def test_database_connection(db: Session = Depends(database.get_db)):
    """
    一個簡單的端點，用來測試資料庫連線。
    """
    try:
        # 執行一個簡單的查詢來驗證連線
        db.execute('SELECT 1')
        return {"status": "success", "message": "資料庫連線成功！"}
    except Exception as e:
        # 如果有任何錯誤，拋出 HTTP 異常
        raise HTTPException(status_code=500, detail=f"資料庫連線失敗: {e}")

# Create (建立)
@app.post("/items/", response_model=Item, status_code=201)
def create_item(item: ItemCreate):
    """
    建立一個新項目。
    - **name**: 項目名稱 (必填)。
    - **description**: 項目描述 (可選)。
    """
    new_id = max(i.id for i in db) + 1 if db else 1
    new_item = Item(id=new_id, name=item.name, description=item.description)
    db.append(new_item)
    return new_item


# Read (讀取所有項目)
@app.get("/items/", response_model=List[Item])
def read_items():
    """
    獲取所有項目列表。
    """
    return db


# Read (讀取單一項目)
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    """
    根據 ID 獲取單一項目。
    """
    item = next((item for item in db if item.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="找不到該項目")
    return item


# Update (更新)
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item_update: ItemCreate):
    """
    根據 ID 更新一個既有項目。
    """
    item_index = next((index for index, i in enumerate(db) if i.id == item_id), None)

    if item_index is None:
        raise HTTPException(status_code=404, detail="找不到該項目")

    updated_item = Item(id=item_id, **item_update.model_dump())
    db[item_index] = updated_item
    return updated_item


# Delete (刪除)
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    """
    根據 ID 刪除一個項目。
    """
    item = next((item for item in db if item.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="找不到該項目")
    db.remove(item)
    return  # 成功時不返回任何內容，狀態碼為 204
