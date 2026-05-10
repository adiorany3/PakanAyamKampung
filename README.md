# Kalkulator Pakan Ayam Kampung

Aplikasi Streamlit untuk membantu peternak ayam kampung di Indonesia menyusun ransum secara praktis. Aplikasi ini menghitung:

- komposisi bahan pakan dalam persen,
- kebutuhan bahan dalam kilogram,
- estimasi biaya total dan biaya per kg,
- kandungan protein, energi metabolis, kalsium, fosfor, lemak, dan serat,
- evaluasi apakah hasil sudah mendekati target fase ayam,
- saran perbaikan formula.

## Perbaikan dari versi awal

Versi awal `app.py` tersimpan dalam satu baris sehingga sulit dijalankan dan sulit diedit. Versi ini dibuat ulang agar:

1. struktur kode lebih rapi dan mudah dipelihara,
2. antarmuka memakai bahasa Indonesia yang sederhana,
3. tersedia formula contoh untuk fase starter, grower, finisher, dan induk/petelur,
4. pengguna dapat memasukkan harga bahan sesuai pasar lokal,
5. hasil langsung menampilkan jumlah bahan dalam kg dan estimasi biaya,
6. komposisi otomatis dinormalisasi ke 100%,
7. hasil komposisi bisa diunduh sebagai CSV.

## Cara menjalankan di laptop/PC

Pastikan Python sudah terpasang. Disarankan memakai Python 3.10 atau versi lebih baru.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Setelah perintah dijalankan, browser akan membuka aplikasi secara otomatis. Jika tidak terbuka, salin alamat lokal yang muncul di terminal, biasanya:

```text
http://localhost:8501
```

## Cara pakai singkat

1. Pilih fase ayam di sidebar.
2. Masukkan jumlah pakan yang ingin dibuat, misalnya 50 kg atau 100 kg.
3. Pilih `Pakai formula contoh` untuk simulasi cepat, atau `Atur manual` untuk mengubah persentase bahan.
4. Ubah harga bahan per kg sesuai harga di daerah Anda.
5. Lihat tabel evaluasi nutrisi dan saran perbaikan.
6. Unduh komposisi sebagai CSV bila ingin dicetak atau disimpan.

## Catatan penting

Nilai nutrisi pada aplikasi adalah pendekatan. Kandungan bahan pakan dapat berubah karena mutu bahan, kadar air, penyimpanan, musim, dan pemasok. Untuk usaha komersial, gunakan analisis laboratorium atau konsultasi dengan penyuluh/nutrisionis ternak.
