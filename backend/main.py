from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import Dict, List
import openpyxl
import io
from datetime import datetime
import pandas as pd
import pyexcel as pe
from collections import defaultdict

app = FastAPI()

def parse_excel_to_dict(file_content: bytes) -> List[List]:
    try:
        df = pd.read_excel(io.BytesIO(file_content))

        column_headers = df.columns.tolist()

        dates = [column_headers[i] for i in range(3, len(column_headers), 4)]

        # print(dates)

        readings_dict = defaultdict(list)
        
        data_list = df.values.tolist()

        for i in range(2, len(data_list)):
            for j in range(len(dates)):
                readings_dict[int(data_list[i][1])].append(
                        {
                        'date': dates[j],
                        'A_plus': data_list[i][j],
                        'A_minus': data_list[i][j + 3],
                        'B_plus': data_list[i][j + 4],
                        'B_minus': data_list[i][j + 5],
                        }
                )
            print(readings_dict)
        
    except Exception as e:
        raise HTTPException(500, detail=f"Ошибка обработки файла: {str(e)}")

@app.post("/upload/")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(400, detail="Только Excel файлы (.xls, .xlsx)")
    
    try:
        contents = await file.read()
        excel_data = parse_excel_to_dict(contents)
        return excel_data
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(500, detail=f"Ошибка: {str(e)}")