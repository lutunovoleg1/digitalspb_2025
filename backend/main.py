from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict, List
import io
from datetime import datetime
import pandas as pd
from collections import defaultdict

from api.database import AsyncSessionLocal
from api.models import Reading

from sqlalchemy import insert

from math import ceil


app = FastAPI()

CHUNK_SIZE = 500

async def insert_in_chunks(session, data):
    total = len(data)
    chunks = ceil(total / CHUNK_SIZE)
    
    for i in range(chunks):
        chunk = data[i*CHUNK_SIZE : (i+1)*CHUNK_SIZE]
        await session.execute(insert(Reading), chunk)
        await session.commit()

def parse_excel_to_list(file_content: bytes) -> List[List]:
    try:
        df = pd.read_excel(io.BytesIO(file_content))
        df = df.where(pd.notna(df), None)

        column_headers = df.columns.tolist()

        dates = [column_headers[i] for i in range(3, len(column_headers), 4)]

        # print(dates)

        readings_list = list()
        
        data_list = df.values.tolist()

        for i in range(2, len(data_list)):
            device_id = str(int(data_list[i][1]))
            for j in range(len(dates)):
                readings_list.append(
                    {
                        'time': dates[j],
                        'device_id': device_id,
                        'a_plus': data_list[i][j + 3],
                        'a_minus': data_list[i][j + 4],
                        'r_plus': data_list[i][j + 5],
                        'r_minus': data_list[i][j + 6],
                    }
                )
        readings_devices_id = [elem['device_id'] for elem in readings_list]
        print(readings_devices_id)
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