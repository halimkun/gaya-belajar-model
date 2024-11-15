# Gunakan image dasar Python
FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt ./

# upgarde pip
# RUN pip install --upgrade pip

# Install dependencies
RUN pip install -r requirements.txt

# Salin seluruh kode aplikasi ke dalam container
COPY . .

# Perintah untuk menjalankan aplikasi menggunakan Gunicorn
CMD ["python", "app.py"]