# Gunakan image dasar Python
FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi ke dalam container
COPY . .

# Perintah untuk menjalankan aplikasi menggunakan Gunicorn
CMD ["gunicorn", "-b", ":8896", "app:app"]