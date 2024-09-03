from flask import Flask, request, jsonify
from predict_model import predict_severity, loaded_model
from build_features import preprocess_features

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    
    # Prétraiter les données
    preprocessed_data = preprocess_features(data)
    
    # Faire la prédiction
    prediction = predict_severity(loaded_model, preprocessed_data)
    
    return jsonify({'prediction': float(prediction)})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'OK', 'message': 'Server is running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
