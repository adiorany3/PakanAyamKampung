# Panduan Praktis Peternak Ayam Kampung/KUB

**Developed by: Galuh Adi Insani**

Dokumen ini menjadi pendamping aplikasi `Optimizer Pakan Ayam Kampung Indonesia`.

## 1. Tujuan formulasi pakan

Tujuan utama bukan membuat pakan paling murah, tetapi membuat pakan dengan **biaya paling efisien untuk target pertumbuhan atau produksi**. Pakan yang terlalu murah tetapi protein, energi, atau mineralnya kurang bisa membuat ayam lambat besar, umur panen mundur, dan biaya total justru naik.

## 2. Prinsip nutrisi

### Protein
Protein dibutuhkan untuk pertumbuhan otot, bulu, produksi telur, dan daya tahan tubuh. Kekurangan protein membuat ayam lambat besar dan bobot tidak seragam. Sumber protein yang umum:

- bungkil kedelai,
- tepung ikan,
- bungkil kelapa,
- sebagian dari dedak dan jagung.

### Energi
Energi berasal dari jagung, gaplek, dedak, dan minyak. Energi yang kurang membuat ayam banyak makan tetapi pertumbuhan tidak optimal. Energi berlebih tanpa protein cukup dapat menyebabkan pemborosan.

### Mineral
Kalsium dan fosfor penting untuk tulang dan kerabang telur. Induk/petelur membutuhkan kalsium jauh lebih tinggi dibanding ayam pembesaran.

### Serat
Serat terlalu tinggi dapat menurunkan kecernaan. Dedak dan bungkil kelapa perlu dibatasi, terutama untuk ayam muda.

## 3. Bahan lokal dan strategi penggunaannya

### Jagung giling
Cocok sebagai sumber energi utama. Pastikan kering, tidak berjamur, dan tidak terlalu kasar.

### Dedak padi/bekatul
Murah dan mudah didapat. Masalah utama adalah mutu tidak stabil, mudah tengik, dan bisa tinggi serat. Gunakan dari pemasok tepercaya.

### Bungkil kedelai
Sumber protein berkualitas. Jika harganya tinggi, gunakan seperlunya dan kombinasikan dengan bahan protein lain.

### Tepung ikan
Sangat baik bila mutunya bagus. Cek bau, kadar air, cemaran garam, dan risiko pemalsuan. Penggunaan berlebihan menaikkan biaya dan bisa membuat pakan terlalu amis.

### Bungkil kelapa
Bahan lokal yang membantu menekan biaya, tetapi seratnya tinggi. Batasi terutama untuk starter.

### Gaplek/tepung singkong
Sumber energi murah di beberapa daerah. Karena proteinnya rendah, harus diimbangi dengan bahan protein.

### Kapur pakan/tepung tulang
Dipakai untuk mineral. Sangat penting untuk petelur, tetapi jangan berlebihan.

## 4. Cara membaca hasil aplikasi

- **Biaya/kg pakan**: biaya produksi 1 kg pakan.
- **Potensi hemat vs optimum**: selisih biaya dibanding formula optimum dari harga dan batas bahan saat ini.
- **Status nutrisi hijau**: masih dalam rentang target.
- **Status merah**: kurang; perlu perbaikan.
- **Status oranye**: berlebih; biasanya bisa dikurangi agar biaya lebih efisien.

## 5. Pemeliharaan fase starter

- Kandang brooder harus hangat, kering, dan tidak terkena angin langsung.
- Alas kandang harus diganti bila basah.
- Pakan diberikan beberapa kali sehari agar segar.
- Air minum harus selalu tersedia dan bersih.
- Amati sebaran anak ayam: bila bergerombol di bawah lampu berarti dingin, bila menjauh dari lampu berarti terlalu panas.

## 6. Pemeliharaan grower dan pembesaran

- Kepadatan perlu disesuaikan dengan ventilasi dan suhu.
- Litter harus dijaga kering.
- Tempat pakan dan minum harus cukup agar ayam tidak berebut.
- Timbang sampel ayam tiap minggu untuk melihat pertumbuhan.

## 7. Sistem semi-intensif

Sistem semi-intensif cocok untuk sebagian peternak Indonesia karena bisa memanfaatkan pekarangan berpagar. Hijauan, serangga, dan aktivitas alami dapat membantu, tetapi pakan buatan tetap diperlukan supaya pertumbuhan seragam.

## 8. Pencatatan minimal

Catat setiap minggu:

- jumlah ayam awal dan akhir,
- kematian,
- jumlah pakan habis,
- bobot sampel,
- obat/vitamin/vaksin,
- biaya pakan dan bahan,
- harga jual.

Dari catatan tersebut peternak bisa menghitung efisiensi dan membandingkan formula antar periode.

## 9. Rumus sederhana evaluasi

### FCR sederhana

```text
FCR = total pakan habis / total kenaikan bobot hidup
```

Semakin rendah FCR, semakin efisien penggunaan pakan. Namun ayam kampung umumnya memiliki pertumbuhan lebih lambat dibanding broiler, sehingga evaluasi harus sesuai jenis ayam dan sistem pemeliharaan.

### Biaya pakan per kg bobot hidup

```text
Biaya pakan per kg bobot hidup = biaya pakan total / total kenaikan bobot hidup
```

Rumus ini sering lebih berguna daripada hanya melihat harga pakan per kg.


## 10. Ekspor ransum ke Excel dan PDF

Aplikasi menyediakan tiga jenis unduhan:

### Excel `.xlsx`

Gunakan Excel untuk arsip usaha dan perhitungan lanjutan. File Excel berisi beberapa sheet:

- **Ringkasan**: fase ayam, mode formulasi, jumlah pakan, biaya total, biaya/kg, estimasi kebutuhan, dan hasil nutrisi utama.
- **Formula Ransum**: persentase bahan, jumlah kg, harga/kg, biaya, serta kontribusi protein dan energi.
- **Evaluasi Nutrisi**: status nutrisi terhadap target fase.
- **Checklist Belanja**: daftar bahan yang perlu dibeli beserta jumlah dan biaya.
- **Insight Bahan**: efisiensi harga bahan berdasarkan protein dan energi.
- **Saran**: rekomendasi perbaikan formula.
- **Data Bahan**: data harga, nutrisi, dan batas pemakaian yang digunakan dalam perhitungan.
- **Pemeliharaan**: checklist harian dan mingguan.

### PDF

Gunakan PDF untuk laporan siap cetak atau dibagikan ke peternak, kelompok ternak, penyuluh, atau mitra usaha. PDF berisi ringkasan ransum, formula, evaluasi nutrisi, saran tindakan, checklist belanja, dan checklist pemeliharaan.

### CSV

CSV tetap disediakan untuk kebutuhan sederhana, misalnya membuka formula di spreadsheet ringan atau sistem pencatatan lain.

## 11. Cara menyesuaikan biaya dengan kondisi Indonesia

Harga bahan pakan sangat berbeda antar daerah. Untuk mendapatkan hasil paling efisien:

- Masukkan harga bahan sesuai kondisi lokal, bukan harga perkiraan umum.
- Jika jagung mahal tetapi dedak murah, naikkan batas dedak secara hati-hati dan tetap perhatikan serat.
- Jika tepung ikan lokal murah di daerah pesisir, tetap batasi penggunaannya dan cek bau, garam, kadar air, dan kemungkinan pemalsuan.
- Jika bungkil kedelai mahal, kombinasikan dengan bahan protein lokal, tetapi jangan sampai protein, lisin, dan metionin terlalu rendah.
- Jika bahan mudah berjamur karena daerah lembap, jangan membeli stok terlalu banyak; bahan murah yang rusak dapat membuat kerugian lebih besar.
- Evaluasi efisiensi dari biaya per kg bobot hidup, bukan hanya harga pakan per kg.
