# crud.py
from sqlalchemy.orm import Session
import models
from sqlalchemy import text
import schemas
import security


# def get_item(db: Session, item_id: int):
#     return db.query(models.Item).filter(models.Item.id == item_id).first()
#
#
# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()
#
#
# def create_item(db: Session, item: schemas.ItemCreate):
#     db_item = models.Item(name=item.name, description=item.description)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
#
#
# def update_item(db: Session, item_id: int, item: schemas.ItemUpdate):
#     db_item = get_item(db, item_id)
#     if db_item:
#         db_item.name = item.name
#         db_item.description = item.description
#         db.commit()
#         db.refresh(db_item)
#     return db_item
#
#
# def delete_item(db: Session, item_id: int):
#     db_item = get_item(db, item_id)
#     if db_item:
#         db.delete(db_item)
#         db.commit()
#     return db_item


def get_item(db: Session, item_id: int):
    # --- 使用原始 SQL 的 Read ---
    query = text("SELECT * FROM items WHERE id = :item_id")
    result = db.execute(query, {"item_id": item_id}).first()
    return result


def get_items(db: Session, skip: int = 0, limit: int = 100):
    # --- 使用原始 SQL 的 Read (All with pagination) ---
    query = text("SELECT * FROM items ORDER BY id LIMIT :limit OFFSET :skip")
    result = db.execute(query, {"limit": limit, "skip": skip}).all()
    return result


def create_item(db: Session, item: schemas.ItemCreate):
    # --- 使用原始 SQL 的 Create ---
    # RETURNING * 是 PostgreSQL 的一個好用功能，它會在 INSERT 後立即回傳剛建立的整筆資料
    query = text("INSERT INTO items (name, description) VALUES (:name, :description) RETURNING *")

    params = {
        "name": item.name,
        "description": item.description
    }

    result = db.execute(query, params).first()
    db.commit()  # 執行 INSERT/UPDATE/DELETE 後需要 commit
    return result


def update_item(db: Session, item_id: int, item: schemas.ItemUpdate):
    # --- 使用原始 SQL 的 Update ---
    query = text("""
                 UPDATE items
                 SET name        = :name,
                     description = :description
                 WHERE id = :item_id RETURNING *
                 """)

    params = {
        "item_id": item_id,
        "name": item.name,
        "description": item.description
    }

    result = db.execute(query, params).first()
    db.commit()
    return result


def delete_item(db: Session, item_id: int):
    # --- 使用原始 SQL 的 Delete ---
    query = text("DELETE FROM items WHERE id = :item_id RETURNING *")
    result = db.execute(query, {"item_id": item_id}).first()
    db.commit()
    return result

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
