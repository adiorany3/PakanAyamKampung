# Optimizer Pakan Ayam Kampung Indonesia

Aplikasi Streamlit untuk membantu peternak ayam kampung/KUB menyusun ransum berbasis bahan lokal, target nutrisi, dan harga pasar setempat.

Versi ini menyempurnakan repo awal `PakanAyamKampung` agar lebih siap digunakan oleh peternak di Indonesia, bukan hanya menghitung komposisi dasar.

## Fitur utama

1. **Optimasi biaya otomatis**
   - Mencari formula pakan dengan biaya terendah.
   - Memakai batas nutrisi: protein, energi metabolis, kalsium, fosfor, serat, dan lemak.
   - Lisin dan metionin dievaluasi, serta dapat dijadikan batas optimasi bila diperlukan.

2. **Harga bahan bisa disesuaikan lokal**
   - Jagung, dedak, bungkil kedelai, tepung ikan, bungkil kelapa, gaplek, minyak, mineral, garam, dan premix.
   - Peternak dapat mengubah harga sesuai pasar desa/kecamatan/kabupaten.

3. **Batas pemakaian bahan bisa diedit**
   - Jika bahan tidak tersedia, hilangkan centang `Pakai` atau ubah `Max %` menjadi 0.
   - Jika bahan melimpah, naikkan batas maksimum secara hati-hati.

4. **Evaluasi nutrisi**
   - Menampilkan status kurang/sesuai/berlebih untuk tiap nutrien utama.
   - Memberikan saran praktis bila protein, energi, mineral, atau serat belum sesuai.

5. **Insight efisiensi harga**
   - Menghitung bahan sumber protein termurah berdasarkan `Rp/kg protein`.
   - Menghitung bahan sumber energi termurah berdasarkan `Rp/1000 kkal EM`.
   - Membantu peternak memilih bahan bukan hanya dari harga per kg, tetapi dari nilai nutrisinya.

6. **Estimasi kebutuhan dan biaya pakan**
   - Input jumlah ayam, hari pemakaian, dan konsumsi rata-rata.
   - Menampilkan estimasi kebutuhan pakan dan biaya pakan periode tersebut.

7. **Panduan pemeliharaan**
   - Starter/DOC, grower, semi-intensif, kesehatan, biosekuriti, dan penyimpanan bahan.
   - Ada checklist harian dan mingguan.

8. **Unduhan CSV**
   - Formula pakan.
   - Checklist belanja bahan.

## Cara menjalankan

Pastikan Python 3.10+ sudah terpasang.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Aplikasi biasanya terbuka di:

```text
http://localhost:8501
```

## Cara pakai untuk peternak

1. Pilih fase ayam: starter, grower, finisher, atau layer/induk.
2. Masukkan jumlah pakan yang ingin dibuat, misalnya 50 kg atau 100 kg.
3. Edit harga bahan sesuai harga setempat.
4. Pilih mode:
   - `Optimasi biaya otomatis`: aplikasi mencari formula efisien.
   - `Pakai formula contoh`: memakai titik awal praktis.
   - `Atur manual`: peternak mengatur persentase sendiri.
5. Lihat status nutrisi.
6. Baca saran perbaikan formula.
7. Unduh CSV untuk dicetak atau disimpan.

## Strategi mendapatkan nutrisi terbaik dengan biaya efisien

- Jangan memilih bahan hanya dari harga per kg. Lihat juga protein, energi, serat, dan mineral.
- Jagung biasanya menjadi sumber energi utama, tetapi perlu sumber protein.
- Dedak murah, tetapi serat dan minyaknya tinggi. Batasi bila pertumbuhan melambat atau dedak mudah tengik.
- Bungkil kedelai mahal, tetapi efektif menaikkan protein dan lisin.
- Tepung ikan bagus untuk protein dan mineral, tetapi harus dicek mutu, bau, kadar garam, dan harganya.
- Kapur pakan penting untuk kalsium, khususnya induk/petelur, tetapi tidak boleh berlebihan.
- Formula yang murah secara angka harus diuji dulu di sebagian kecil ayam selama 7-14 hari.

## Catatan penting

Nilai nutrisi pada aplikasi adalah pendekatan praktis. Kandungan aktual bahan pakan sangat dipengaruhi kadar air, mutu bahan, lama penyimpanan, musim, dan pemasok. Untuk skala usaha besar, gunakan analisis laboratorium atau konsultasi dengan penyuluh/nutrisionis ternak.

## Struktur file

```text
PakanAyamKampung_pro/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── docs/
    └── PANDUAN_PETERNAK.md
```
