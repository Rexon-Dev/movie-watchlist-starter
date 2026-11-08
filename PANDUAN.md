# Panduan Pengujian, Integrasi Frontend, dan GitHub

## A. Persiapan cepat

Lihat `README.md` bagian Cara Memasang dan Mengatur `.env`. Setelah itu:

```bash
uvicorn app.main:app --reload
```

Terminal harus menampilkan `Uvicorn running on http://127.0.0.1:8000` dan log seeding (`20 film baru ditambahkan` pada start pertama, `0` pada start berikutnya).

## B. Pengujian lewat Swagger UI (`/docs`)

Buka http://127.0.0.1:8000/docs. Klik endpoint, lalu **Try it out**, isi body, **Execute**.

Setelah login, klik tombol **Authorize** di kanan atas, tempel token (tanpa kata `Bearer`), klik Authorize. Endpoint dengan ikon gembok kini membawa token.

Gunakan email dengan domain biasa (`example.com`, `gmail.com`). Domain khusus seperti `.test` atau `.local` ditolak validator email.

### 1. Register: `POST /api/auth/register`
```json
{"username": "hebron", "email": "hebron@example.com", "password": "rahasia123"}
```
Harus: **201**
```json
{"message": "Registrasi berhasil. Silakan login.", "user": {"id": 1, "username": "hebron", "email": "hebron@example.com"}}
```
Ulangi request yang sama: **409** `{"message": "Email sudah terdaftar"}`.
Password 5 karakter: **400** (`password: String should have at least 8 characters`).

### 2. Login: `POST /api/auth/login`
```json
{"email": "hebron@example.com", "password": "rahasia123"}
```
Harus: **200** `{"token": "eyJ...", "user": {"id": 1, "username": "hebron", "email": "hebron@example.com"}}`.
Password salah: **401** `{"message": "Email atau password salah"}`.

### 3. Password tersimpan sebagai hash
```bash
python -c "import sqlite3; print(sqlite3.connect('filmlog.db').execute('select email, password_hash from users').fetchall())"
```
Kolom kedua harus berawalan `$2b$`, bukan `rahasia123`.

### 4. Movies
- `GET /api/movies`: 200, 20 film.
- `GET /api/movies?genre=Sci-Fi`: hanya film Sci-Fi (Inception, Interstellar, The Matrix, Alien, WALL-E, Blade Runner 2049, Dune).
- `GET /api/movies?genre=Sci-Fi&search=Inception`: hanya Inception.
- `GET /api/movies/1`: detail Inception (field `genres` dan `cast` berupa array).
- `GET /api/movies/999`: **404** `{"message": "Film tidak ditemukan"}`.

### 5. Proteksi endpoint
Tanpa Authorize (atau `curl` tanpa header), `GET /api/watchlist` dan `GET /api/watched` harus **401**.
Token ngawur (`Authorization: Bearer abc`): **401**.

### 6. Watchlist (sudah Authorize)
- `POST /api/watchlist` body `{"movieId": 1}`: **201** `{"message": "Film ditambahkan ke watchlist", "movieId": 1}`.
- Kirim lagi: **409**. Body `{"movieId": 999}`: **404**.
- `GET /api/watchlist`: 200, array berisi objek film Inception.
- `DELETE /api/watchlist/1`: 200 `{"message": "Film dihapus dari watchlist"}`. Ulangi: 404.

### 7. Watched dan review
- `POST /api/watched` body `{"movieId": 1, "rating": 5, "review": "Filmnya luar biasa"}`: **201**, berisi `id, movie_id, rating, review, created_at, movie`.
- `rating: 6` atau `0`: **400**. Film sama dua kali: **409**.
- `GET /api/watched`: 200, daftar review milik user ini.

### 8. Data antar user terpisah
Register + login user kedua (`user2@example.com`), Authorize dengan token user kedua:
- `GET /api/watchlist` dan `GET /api/watched` harus `[]`.
- `DELETE /api/watchlist/1` harus **404** (watchlist user pertama tidak tersentuh).

### 9. Gemini: `POST /api/movies/recommend`
```json
{"prompt": "Saya ingin menonton film fiksi ilmiah yang memiliki cerita menarik."}
```
Harus: **200** `{"movie_id": <id film sci-fi>, "reasoning": "..."}`. `movie_id` selalu ada di 1-20.
Coba prompt di luar daftar, mis. "Saya mau nonton Avatar": hasilnya tetap salah satu dari 20 film.

## C. Integrasi frontend

1. Backend jalan di port 8000.
2. Terminal kedua: `cd frontend` lalu `python -m http.server 3000`.
3. Buka http://localhost:3000. Titik hijau di pojok = backend terhubung.
4. Uji alur: Register, Login, buka poster, Add Watchlist, Mark Watched (beri rating + review), tab Watchlist dan Watched, tab AI Recommendation.
5. Buka drawer **Show Logs** di bawah untuk melihat status tiap request.

Frontend tidak diubah. Penyesuaian dilakukan di backend (format error `message`, objek film langsung di watchlist, response register tanpa token, CORS).

## D. Panduan GitHub

Prasyarat: Git terpasang (`git --version`) dan akun GitHub. Sekali saja di komputer ini:
```bash
git config --global user.name "Nama Kamu"
git config --global user.email "email@kamu.com"
```

1. Buat repository di https://github.com/new. Nama contoh: `movie-watchlist-api`. Pilih **Public**. Jangan centang README/.gitignore/license (sudah ada di proyek).
2. Di folder root proyek:
   ```bash
   git init
   git add .
   git status
   ```
   Pastikan `.env`, `.venv/`, dan `filmlog.db` **tidak** muncul di daftar. `.env.example` boleh muncul.
3. Commit:
   ```bash
   git commit -m "Movie Watchlist API: FastAPI, SQLite, JWT, Gemini"
   ```
4. Hubungkan ke GitHub (ganti `USERNAME`):
   ```bash
   git branch -M main
   git remote add origin https://github.com/USERNAME/movie-watchlist-api.git
   git push -u origin main
   ```
   Saat diminta login, ikuti jendela browser atau pakai Personal Access Token sebagai password.
5. Buka halaman repo di browser. Cek: ada `app/`, `data/`, `frontend/`, `README.md`, `requirements.txt`, `.env.example`; **tidak ada** `.env`.

Jika API key Gemini pernah ter-commit, hapus key itu di Google AI Studio dan buat yang baru. Menghapus file dari commit baru tidak menghapus riwayat lama.

Sebelum submit, pin versi dependency agar hasil sama di komputer lain (venv aktif):
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Pin versi dependency"
git push
```

## E. Masalah umum

| Gejala | Penyebab / solusi |
|---|---|
| `RuntimeError: SECRET_KEY belum diisi` | Buat `.env` dari `.env.example`, isi `SECRET_KEY`. |
| `ModuleNotFoundError` | venv belum aktif, atau `pip install -r requirements.txt` belum dijalankan. |
| `pip install` gagal di Python 3.14 | Kirim pesan error lengkap; biasanya paket perlu versi lebih baru (`pip install -U pip`). |
| Frontend: "Backend belum aktif" / CORS | Backend belum jalan, atau API Base URL di Settings frontend bukan `http://localhost:8000/api`. |
| Gemini 502 "kode 404" | Nama model di `GEMINI_MODEL` tidak tersedia. Ganti (mis. `gemini-3.8-flash`), restart server. |
| Gemini 502 "kode 400/403" | `GEMINI_API_KEY` salah atau belum aktif. |
| Gemini 502 "kode 429" | Kuota gratis habis. Tunggu beberapa saat. |
| Gemini 503 | `GEMINI_API_KEY` kosong di `.env`. |
| Ingin reset data | Hentikan server, hapus `filmlog.db`, jalankan server lagi. |
