from pydantic import BaseModel

class HospitalQuery(BaseModel):
    text : str