import sqlite3
from app.schemas.schemas import ShipmentCreate, ShipmentUpdate
from typing import Any
from contextlib import contextmanager
class Database:
    def connect_to_db(self):
        self.conn = sqlite3.connect("sqlite.db",check_same_thread=False)
        self.cur = self.conn.cursor()
        print("Connected to the database")
    def create_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS shipment (
            id INTEGER PRIMARY KEY,
            content TEXT,
            weight REAL,
            status TEXT,
            destination INTEGER,
            estimated_delivery_date TEXT  -- <- This was missing in the actual table
        )
    """)


    def create(self, shipment: ShipmentCreate):
        self.cur.execute("SELECT MAX(id) FROM shipment")
        result = self.cur.fetchone()
        new_id = (result[0] or 12700) + 1  # Fallback if DB is empty
        self.cur.execute("""
            INSERT INTO shipment (id, content, weight, status, destination)
            VALUES (:id, :content, :weight, :status, :destination)
        """, {
         "id": new_id,
            **shipment.model_dump(),
            "status": "placed"
     })
        self.conn.commit()
        return new_id 

    def get(self, id: int):
        self.cur.execute("SELECT * FROM shipment WHERE id = ?", (id,))
        row = self.cur.fetchone()
        print(type(row))
        print(row)
        return {
            "id": row[0],
            "content": row[1],
            "weight": row[2],
            "status": row[3]
        } if row else None

    def update(self, id: int, shipment: ShipmentUpdate) -> dict[str, Any]:
        self.cur.execute("""
            UPDATE shipment
            SET status = :status
            WHERE id = :id
        """, {
            "id": id,
            **shipment.model_dump()
        })
        self.conn.commit()
        return self.get(id)

    def delete(self, id: int):
        self.cur.execute("DELETE FROM shipment WHERE id = ?", (id,))
        self.conn.commit()

    def close(self):
        print("Closing the database connection")
        self.conn.close()
    # def __enter__(self):
     #   print("Entering the database context")
      #  self.connect_to_db()
       # self.create_table()
        #return self
    # def __exit__(self, *arg):
     #   print("Exiting the database context")
      #  self.close()
#Usage
@contextmanager
def managed_db():
    db=Database()
    #Setup 
    print("Entering the database context")
    db.connect_to_db()
    db.create_table()
    yield db
    #dispose
    print("Exiting the database context")
    db.close()
with managed_db() as db:
    db.get(12701)
