from flask import Flask, request, jsonify
import pickle
import numpy as np
import pandas as pd
from collections import Counter

# Membuat instance Flask
app = Flask(__name__)

# Memuat model, scaler, dan label encoder yang sudah diekspor menggunakan pickle
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('knn_model.pkl', 'rb') as f:
    knn_model = pickle.load(f)

with open('label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)
    
# Memuat X_train dan y_train
with open('X_train.pkl', 'rb') as f:
    X_train = pickle.load(f)

with open('y_train.pkl', 'rb') as f:
    y_train = pickle.load(f)


# Menambahkan route index untuk menguji server
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
                        'message': f'Field {field} is required',
                        'code': 400
                    }
                }), 400  # Ganti kode status menjadi 400 (Bad Request)
            
        # Jika skor tidak ada, hitung skor sebagai rata-rata MTK dan PJOK
        data.setdefault('skor', (data['mtk'] + data['pjok']) / 2)
        
        # Mengurutkan data agar sesuai dengan urutan yang diharapkan
        ordered_data = {
            'mtk': data['mtk'],
            'pjok': data['pjok'],
            'visual': data['visual'],
            'auditori': data['auditori'],
            'kinestetik': data['kinestetik'],
            'skor': data['skor']
        }
        data = ordered_data
        

        # Menyusun data input untuk model
        input_data = pd.DataFrame([data])

        # Normalisasi data
        input_data_scaled = scaler.transform(input_data)

        # Mendapatkan tetangga terdekat untuk data input
        neighbors = knn_model.kneighbors(input_data_scaled, n_neighbors=3)  # Mendapatkan indeks tetangga terdekat
        indices = neighbors[1]  # Indeks tetangga terdekat
        
        # Mengambil label dari data latih berdasarkan indeks tetangga terdekat
        neighbor_labels = label_encoder.inverse_transform(y_train.iloc[indices.flatten()])

        # Menghitung jumlah setiap label gaya belajar (termasuk campuran)
        label_counts = Counter(neighbor_labels)
        
        # Menghitung total jumlah tetangga
        total_neighbors = len(neighbor_labels)
        
        # Persentase prediksi
        percentage_predictions = []
        for neighbors in indices:
            # Ambil label dari tetangga terdekat
            neighbor_labels = y_train.iloc[neighbors]
            label_counts = Counter(neighbor_labels)

            percentage = {label_encoder.inverse_transform([label])[0]: (count / total_neighbors) * 100 for label, count in label_counts.items()}
            percentage_predictions.append(percentage)

        # Melakukan prediksi untuk data input
        prediction = knn_model.predict(input_data_scaled)

        # Mengembalikan hasil prediksi dan persentase sebagai JSON
        return jsonify({
            'results': percentage_predictions,
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
    app.run(debug=True, port=8896, host='0.0.0.0', threaded=True)
