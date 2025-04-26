from pydantic import BaseModel
import datetime
from typing import Optional


class Reading(BaseModel):
    time: datetime
    device_id: int
    A_plus: Optional(float)
    A_minus: Optional(float)
    R_plus: Optional(float)
    R_minus: Optional(float)
