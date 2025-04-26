from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict, List
import io
from datetime import datetime
import pandas as pd
from collections import defaultdict

from api.database import AsyncSessionLocal
from api.models import Reading

from sqlalchemy import insert, text

from math import ceil


app = FastAPI()

CHUNK_SIZE = 500

async def insert_in_chunks(session, data):
    total = len(data)
    chunks = ceil(total / CHUNK_SIZE)
    
    for i in range(chunks):
        chunk = data[i*CHUNK_SIZE : (i+1)*CHUNK_SIZE]
        try:
            await session.execute(insert(Reading), chunk)
            await session.commit()  # Явный коммит после каждой порции
        except Exception as chunk_error:
            await session.rollback()
            print(f"Chunk {i} error: {chunk_error}")
            raise

def parse_excel_to_list(file_content: bytes) -> List[List]:
    try:
        df = pd.read_excel(io.BytesIO(file_content))
        df = df.where(pd.notna(df), None)

        column_headers = df.columns.tolist()

        dates = [column_headers[i] for i in range(3, len(column_headers), 4)]

        print(len(dates))

        readings_list = list()
        
        data_list = df.values.tolist()

        for i in range(1, len(data_list)):
            device_id = str(int(data_list[i][1]))
            for j in range(len(dates)):
                readings_list.append(
                    {
                        'time': dates[j],
                        'device_id': device_id,
                        'a_plus': data_list[i][j * 4 + 3],
                        'a_minus': data_list[i][j * 4 + 4],
                        'r_plus': data_list[i][j * 4 + 5],
                        'r_minus': data_list[i][j * 4 + 6],
                    }
                )
        readings_devices_id = [elem['device_id'] for elem in readings_list]
        print(len(readings_list))
        return readings_list
        
    except Exception as e:
        raise HTTPException(500, detail=f"File processing error: {str(e)}")

@app.post("/upload/")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(400, detail="Wrong file type")
    
    try:
        contents = await file.read()
        excel_data = parse_excel_to_list(contents)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    async with AsyncSessionLocal() as session:
        try:
            await insert_in_chunks(session, excel_data)
            return {"status": f"Inserted {len(excel_data)} records"}
            
        except Exception as e:
            await session.rollback()
            raise HTTPException(500, detail=f"Database error: {str(e)}")


@app.get("/test-db")
async def test_db():
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text("SELECT 1"))
            return {"status": "OK", "result": result.scalar()}
        except Exception as e:
            raise HTTPException(500, detail=str(e))