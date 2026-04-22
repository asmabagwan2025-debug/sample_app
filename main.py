from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height**2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        
        if self.bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= self.bmi < 25:
            return 'Normal weight'
        elif 25 <= self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

def load_data():
    with open('patient.json', 'r') as f:
        data = json.load(f)
    return data 

def save_data(data):
    with open('patient.json', 'w') as f:
        json.dump(data, f)

@app.get("/")
def hello_world():
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "A fully functional Patient data to manage System API"}

@app.get("/view")
def view_patient_data():
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve", example="P001")):
    data = load_data()
    if isinstance(data, dict):
        if patient_id in data:
            return data[patient_id]
        raise HTTPException(status_code=404, detail="Patient not found")

    for patient in data:
        if patient.get("patient_id") == patient_id:
            return patient
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description='Sort by one of: patient_id, age, city, gender, height, weight, bmi'),
    order: str = Query('asc', description='sort in ascending or descending order')
):

    valid_fields = ['patient_id', 'age', 'city', 'gender', 'height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field selected. Choose from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order selected. Use asc or desc')
    
    data = load_data()
    if isinstance(data, dict):
        items = []
        for pid, info in data.items():
            item = info.copy() if isinstance(info, dict) else {'value': info}
            item['patient_id'] = pid
            items.append(item)
    else:
        items = data

    reverse = order == 'desc'
    sorted_data = sorted(items, key=lambda x: x.get(sort_by, ''), reverse=reverse)

    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):

    # load existing data
    data = load_data()

    # check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # new patient add to the database
    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient created successfully'})

# id is path parameter so not req in request body, we will get it from the path and then update the patient data
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    existing_patient_info = data[patient_id]

    patient_update.model_dump(exclude_unset=True)

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

# save to json file -> we need to create new pydantic obj to calculate bmi & verdict & then convert it to dict to save in json file & return response to user
# existing_patient_info -> pydantic object -> updated bmi + verdict

    existing_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)

# -> pydantic object -> dict 

    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')
# add this dict to data
    data[patient_id] = existing_patient_info
 
# save to json file
    save_data(data)


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200, content={'message':'patient deleted'})
