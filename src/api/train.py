from src.models.train_model import train_model 
 
router = APIRouter() 
 
@router.post('/train') 
def train(): 
    train_model() 
    return {'message': 'Model trained successfully'} 
