from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd

# Membuat instance Flask
app = Flask(__name__)

# Memuat model dan scaler
scaler = joblib.load('scaler.pkl')
knn_model = joblib.load('knn_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

# add new route index to test the server
@app.route('/')
def index():
    return 'Server is running'

# Endpoint untuk prediksi
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Mendapatkan data dari permintaan JSON
        data = request.get_json(force=True)
        
        # Validasi data
        required_fields = ['mtk', 'pjok', 'visual', 'auditori', 'kinestetik']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': {
                        'message': 'Field ' + field + ' is required',
                        'code': 400
                    }
                }), 500
            
        data.setdefault('skor', (data['mtk'] + data['pjok']) / 2)

        # Menyusun data input
        input_data = pd.DataFrame([data])

        # Normalisasi data
        input_data = scaler.transform(input_data)

        # Melakukan prediksi
        prediction = knn_model.predict(input_data)

        # Mengembalikan hasil prediksi sebagai JSON
        return jsonify({
            'prediction': label_encoder.inverse_transform(prediction)[0],
            'input': data
        }), 200
    except Exception as e:
        return jsonify({
            'error': {
                'message': str(e),
                'code': 500
            }    
        }), 500

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(debug=False, port=8896)
