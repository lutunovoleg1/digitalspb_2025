from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict, List
import io
from datetime import datetime
from collections import defaultdict
import pandas as pd

from api.database import AsyncSessionLocal
from api.models import Reading

from sqlalchemy import insert, text, select

from api.schemas import Report

from api.excel_parser import parse_excel_to_list
from math import ceil

from api.model.prediction import prediction
from api.model.report_maker import make_report

from fastapi.encoders import jsonable_encoder
import json
import os


app = FastAPI()

CHUNK_SIZE = 500

REPORT_DICT = {}

REPORT_PATH = 'report.json'

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
        except Exception as e:
            await session.rollback()
            raise HTTPException(500, detail=f"Database error: {str(e)}")

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Reading))
            rows = result.scalars().all()
        except Exception as e:
            raise HTTPException(500, detail=f"Database error: {str(e)}")

    data = [row.__dict__ for row in rows]
    for d in data:
        d.pop('_sa_instance_state', None)

    df = pd.DataFrame(data)

    predicted_criminals = prediction(df)
    print(f"Suspicious devices count: {len(predicted_criminals)}")

    report_dict = make_report(df, predicted_criminals)
    print(report_dict)

    json_compatible_report = jsonable_encoder(report_dict)

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(json_compatible_report, f, ensure_ascii=False, indent=4)

    return {"status": f"Inserted {len(excel_data)} records, report saved"}

@app.get("/report/", response_model=Report)
async def return_report_info():
    if not os.path.exists(REPORT_PATH):
        raise HTTPException(status_code=404, detail="Report not available yet")
    try:
        with open(REPORT_PATH, 'r', encoding='utf-8') as f:
            report_dict = json.load(f)
        return report_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed processing report: {e}')