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
    X_train = data['X_train']
    X_test = data['X_test']

# Menambahkan route index untuk menguji server
@app.route('/')
def index():
    # return message server running and show the last update today in json format, last update is date format day date, month, year
    return jsonify({
        'message': 'Server is running',
        'update': "Jum'at, 15 November 2024 09:05"
    })

@app.route('/importance', methods=['GET'])
def importance():
    try:
        # Data uji (ambil sampel dari dataset atau gunakan data lain)
        sample_data = X_test[:10]  # Contoh sampel 10 data
        feature_importance = []

        # Iterasi untuk setiap fitur
        for i in range(X_train.shape[1]):
            perturbed_data = sample_data.copy()

            # Manipulasi nilai fitur ini (+10% dari nilai asli)
            perturbed_data[:, i] *= 1.10

            # Hitung perubahan jarak rata-rata ke tetangga terdekat
            original_distances, _ = knn_model.kneighbors(sample_data)
            perturbed_distances, _ = knn_model.kneighbors(perturbed_data)

            # Rata-rata perubahan jarak
            mean_change = np.mean(np.abs(perturbed_distances - original_distances))
            feature_importance.append(mean_change)

        # Buat hasil dalam bentuk JSON
        importance_result = {
            'features': {
                'mtk': feature_importance[0],
                'pjok': feature_importance[1],
                'visual': feature_importance[2],
                'auditori': feature_importance[3],
                'kinestetik': feature_importance[4],
                'skor': feature_importance[5]
            }
        }

        return jsonify(importance_result), 200

    except Exception as e:
        return jsonify({
            'error': {
                'message': str(e),
                'code': 500
            }
        }), 500

# Endpoint untuk prediksi
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Receive data from JSON request
        input_data = request.get_json(force=True)
        
        # Validate input
        required_fields = ['mtk', 'pjok', 'visual', 'auditori', 'kinestetik', 'skor']
        for field in required_fields:
            if field not in input_data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Prepare and scale input
        input_df = pd.DataFrame([input_data], columns=['mtk', 'pjok', 'visual', 'auditori', 'kinestetik', 'skor'])
        input_scaled = scaler.transform(input_df)

        # Get distances and indices for neighbors
        distances, indices = knn_model.kneighbors(input_scaled, n_neighbors=3)

        # Retrieve labels and distances of neighbors
        neighbors = []
        for i, distance in enumerate(distances[0]):
            neighbor_index = indices[0][i]
            neighbor_label_encoded = y_train.iloc[neighbor_index]
            neighbor_label = label_encoder.inverse_transform([neighbor_label_encoded])[0]
            neighbors.append({
                'label': neighbor_label,
                'distance': float(distance)
            })

        # Predicted label is still based on the closest neighbor
        predicted_label = neighbors[0]['label']

        # Build response
        response = {
            'predicted_label': predicted_label,
            'nearest_neighbors': neighbors
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(debug=True, port=8896, host='0.0.0.0', threaded=True)
