from flask import Flask, request, jsonify
from collections import Counter

import pandas as pd
import numpy as np
import datetime
import pickle
# import locale

# Membuat instance Flask
app = Flask(__name__)

# set locale to Indonesia
# locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

# Load the model, scaler, label encoder, and y_train
with open('knn_model.pkl', 'rb') as file:
    data = pickle.load(file)
    knn_model = data['model']
    scaler = data['scaler']
    label_encoder = data['label_encoder']
    y_train = data['y_train'] 

# Menambahkan route index untuk menguji server
@app.route('/')
def index():
    # return message server running and show the last update today in json format, last update is date format day date, month, year
    return jsonify({
        'message': 'Server is running',
        'update': datetime.datetime(2024, 11, 10).strftime('%A, %d %B %Y')
    })

# Endpoint untuk prediksi
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Receive data from JSON request
        data = request.get_json(force=True)
        
        # Data validation and handling missing fields
        required_fields = ['mtk', 'pjok', 'visual', 'auditori', 'kinestetik']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': {
                        'message': f'Field {field} is required',
                        'code': 400
                    }
                }), 400
        
        # Calculate `skor` if not provided
        data.setdefault('skor', (data['mtk'] + data['pjok']) / 2)
        
        # Prepare and scale input data
        input_data = pd.DataFrame([data], columns=['mtk', 'pjok', 'visual', 'auditori', 'kinestetik', 'skor'])
        input_data_scaled = scaler.transform(input_data)
        
        # Retrieve neighbors and distances
        distances, indices = knn_model.kneighbors(input_data_scaled, n_neighbors=3)
        
        # Predict main label
        predicted_label_encoded = knn_model.predict(input_data_scaled)
        predicted_label = label_encoder.inverse_transform(predicted_label_encoded)[0]
        
        # Retrieve labels and distances of neighbors
        neighbor_labels = label_encoder.inverse_transform(y_train.iloc[indices.flatten()])
        neighbor_info = [
            {"label": label, "distance": distance}
            for label, distance in sorted(zip(neighbor_labels, distances.flatten()), key=lambda x: x[1])
        ]
        
        # Calculate prediction percentages
        label_counts = Counter(neighbor_labels)
        total_neighbors = len(neighbor_labels)
        percentage_predictions = {label: (count / total_neighbors) * 100 for label, count in label_counts.items()}
        
        # Prepare final output
        prediction_result = {
            'predicted_label': predicted_label,
            'percentage_predictions': percentage_predictions,
            'neighbors': neighbor_info
        }
        
        return jsonify(prediction_result), 200
    
    except Exception as e:
        return jsonify({
            'error': {
                'message': str(e),
                'code': 500
            }    
        }), 500

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(debug=True, port=8896, host='0.0.0.0', threaded=True)
