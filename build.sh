#!/bin/bash

# Mendapatkan tanggal hari ini dalam format YYYY-MM-DD
today=$(date +%Y-%m-%d)

# Nama image
image_name="gaya-belajar-model:$today"

# Membangun image Docker
docker build --no-cache -t $image_name .

# Konfirmasi sebelum menjalankan container
read -p "Apakah Anda ingin menjalankan container dengan nama 'gaya-belajar-container'? (yes/no): " confirm

if [[ $confirm == "yes" ]]; then
    # Menjalankan container dengan restart policy
    docker run -d --restart always -p 8896:8896 --name gaya-belajar-container $image_name
    echo "Container 'gaya-belajar-container' telah dijalankan dengan restart policy 'always'."
else
    echo "Container tidak dijalankan."
fi
