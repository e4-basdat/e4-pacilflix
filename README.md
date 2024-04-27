# PacilFlix

Repositori _front-end_ untuk Tugas Kelompok Basis Data Semester Genap 2023/2024. Menggunakan Django dengan `psycopg2` untuk integrasi ke basis data PostgreSQL eksternal.

Oleh kelompok E4:
- Muhammad Nabil Mu'afa (2206024972)
- Dimas Herjunodarpito N. (2206081282)
- Thaariq Kurnia Spama (2206082801)

## Deployment (dev)

Clone repositori ini.

```
git clone https://github.com/e4-basdat/e4-pacilflix.git
```

Buat virtual environment, activate, kemudian install dependencies.

Linux:

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Windows:

```
python -m venv env
env/Scripts/activate
pip install -r requirements.txt
```

Jika ingin menyambungkan dev. environment dengan PostgreSQL eksternal, inisialisasi _environment variables_ berikut:
```
DB_USERNAME=<username_database>
DB_PASSWORD=<password_database>
DB_HOST=<host_database>
DB_PORT=<port_database>
DB_NAME=<nama_database>
```

Jika environment variables tidak diinisialisasi, proyek pada local akan tersambung ke PostgreSQL lokal, dengan asumsi username `postgres`, password `postgres`, dan nama database `defaultdb`. Lebih lengkapnya dapat dilihat pada `utils/query.py`.

Untuk menjalankan di local, jalankan:

```
python manage.py runserver
// or
python3 manage.py runserver
```
