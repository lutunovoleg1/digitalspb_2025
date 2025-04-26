from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict, List
import io
from datetime import datetime
from collections import defaultdict

from api.database import AsyncSessionLocal
from api.models import Reading

from sqlalchemy import insert, text

from api.schemas import Report

from api.excel_parser import parse_excel_to_list
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

@app.get("/report/")
async def return_report_info():
    try:
        response_dict = makeup_report()
        response = Report(response_dict)

        return response
    
    except Exception as e:
        raise HTTPException(500, detail=f'Failed processing report:{e}')
