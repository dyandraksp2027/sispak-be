import fastapi
import json

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class Symptom(BaseModel):
    symptom: dict

diseases_map = {}
symptoms_map = {}
diseases_symptoms_matrix = pd.DataFrame()

def load():
    with open("resource/diseases_map.json", "r") as f:
        global diseases_map
        diseases_map = json.load(f)

    with open('resource/symptoms_map.json', 'r') as f:
        global symptoms_map
        symptoms_map = json.load(f)

    global diseases_symptoms_matrix
    diseases_symptoms_matrix = pd.read_json('resource/diseases_symptoms_matrix.json')

def get_diseases(symtoms_matrix : dict):
    temp_matrix = {int(k):int(v) for k,v in symtoms_matrix.items()}

    filtered_data = diseases_symptoms_matrix.loc[(diseases_symptoms_matrix[list(temp_matrix)] == pd.Series(temp_matrix)).all(axis=1)]

    if(filtered_data.shape[0] > 1):
        temp_id = -2
        next_question_id = filtered_data.sum().to_numpy().argsort(axis=0)[temp_id]

        while int(next_question_id) in temp_matrix.keys():
            temp_id = temp_id - 1
            next_question_id = filtered_data.sum().to_numpy().argsort(axis=0)[temp_id]

        return {
            "ResourceType":"Question",
            'Id':str(next_question_id),
            'CurrentMatrix':temp_matrix,
            "Value":symptoms_map[str(next_question_id)]
        }

    diseases_id = filtered_data.index.to_list()[0]
    return {
        "ResourceType":"Answer",
        'Id':str(diseases_id),
        'Value':diseases_map[str(diseases_id)]
    }

app = FastAPI()
load()

origins = [
    "http://localhost",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get_disease")
async def api_get_disease(symptom: Symptom):
    return get_diseases(symptom.symptom)