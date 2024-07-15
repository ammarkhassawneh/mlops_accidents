from fastapi import APIRouter
from pydantic import BaseModel 
import joblib 
import pandas as pd 
 
router = APIRouter() 
 
class PredictionRequest(BaseModel): 
    place: int 
    catu: int 
    sexe: int 
    secu1: float 
    year_acc: int 
    victim_age: int 
    catv: int 
    obsm: int 
    motor: int 
    catr: int 
    circ: int 
    surf: int 
    situ: int 
    vma: int 
    jour: int 
    mois: int 
    lum: int 
    dep: int 
    com: int 
    agg_: int 
    int: int 
    atm: int 
    col: int 
    lat: float 
    long: float 
    hour: int 
    nb_victim: int 
    nb_vehicules: int 
 
# Load your saved model 
model = joblib.load('./src/models/trained_model.joblib') 
 
@router.post('/predict') 
def predict(request: PredictionRequest): 
    input_data = pd.DataFrame([request.dict()]) 
    prediction = model.predict(input_data) 
    return {'prediction': prediction[0]} 
