from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict, List
import io
from datetime import datetime
import pandas as pd
from collections import defaultdict

from .database import AsyncSessionLocal
from .models import Reading

app = FastAPI()

def parse_excel_to_dict(file_content: bytes) -> List[List]:
    try:
        df = pd.read_excel(io.BytesIO(file_content))

        column_headers = df.columns.tolist()

        dates = [column_headers[i] for i in range(3, len(column_headers), 4)]

        # print(dates)

        readings_list = list()
        
        data_list = df.values.tolist()

        for i in range(2, len(data_list)):
            device_id = int(data_list[i][1])
            for j in range(len(dates)):
                readings_list.append(
                    {
                        'device_id': device_id,
                        'time': dates[j],
                        'A_plus': data_list[i][j],
                        'A_minus': data_list[i][j + 3],
                        'B_plus': data_list[i][j + 4],
                        'B_minus': data_list[i][j + 5],
                    }
                )
        print(readings_list)
        return readings_list
        
    except Exception as e:
        raise HTTPException(500, detail=f"File processing error: {str(e)}")

@app.post("/upload/")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(400, detail="Wrong file type")
    
    try:
        contents = await file.read()
        excel_data = parse_excel_to_dict(contents)
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    async with AsyncSessionLocal() as session:
        try:

            await session.execute(
                insert(Reading),
                excel_data,
            )
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            raise HTTPException(400, detail=str(e))