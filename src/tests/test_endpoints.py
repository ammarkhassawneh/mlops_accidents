import unittest 
from fastapi.testclient import TestClient 
from src.api.main import app 
 
client = TestClient(app) 
 
class TestAPIEndpoints(unittest.TestCase): 
    def test_predict_endpoint(self): 
        response = client.post('/predict', json={ 
            'place': 10, 
            'catu': 3, 
            'sexe': 1, 
            'secu1': 0.0, 
            'year_acc': 2021, 
            'victim_age': 60, 
            'catv': 2, 
            'obsm': 1, 
            'motor': 1, 
            'catr': 3, 
            'circ': 2, 
            'surf': 1, 
            'situ': 1, 
            'vma': 50, 
            'jour': 7, 
            'mois': 12, 
            'lum': 5, 
            'dep': 77, 
            'com': 77317, 
            'agg_': 2, 
            'int': 1, 
            'atm': 0, 
            'col': 6, 
            'lat': 48.60, 
            'long': 2.89, 
            'hour': 17, 
            'nb_victim': 2, 
            'nb_vehicules': 1 
        }) 
        assert response.status_code == 200 
        assert 'prediction' in response.json() 
 
if __name__ == '__main__': 
    unittest.main() 
