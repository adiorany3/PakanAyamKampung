"""
Aplikasi Formulasi Ransum Ayam Kampung
Dibuat agar lebih mudah dipakai oleh peternak di Indonesia.

Cara menjalankan:
    streamlit run app.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import pandas as pd
import streamlit as st


# -----------------------------------------------------------------------------
# Konfigurasi halaman
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Kalkulator Pakan Ayam Kampung",
    page_icon="🐔",
    layout="wide",
)


# -----------------------------------------------------------------------------
# Data dasar
# Nilai nutrisi merupakan nilai pendekatan umum. Untuk penggunaan komersial,
# pengguna tetap perlu menyesuaikan dengan hasil analisis lab/kualitas bahan lokal.
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class NutrisiBahan:
    protein: float  # %
    energi: float  # kkal/kg
    lemak: float  # %
    serat: float  # %
    kalsium: float  # %
    fosfor: float  # %
    harga: int  # Rupiah/kg, harga contoh yang dapat diedit pengguna
    catatan: str


BAHAN_PAKAN: Dict[str, NutrisiBahan] = {
    "Jagung giling": NutrisiBahan(8.5, 3350, 3.8, 2.5, 0.02, 0.30, 6000, "Sumber energi utama."),
    "Dedak padi/bekatul": NutrisiBahan(12.0, 2200, 13.0, 8.0, 0.10, 1.20, 3500, "Mudah didapat, serat cukup tinggi."),
    "Bungkil kedelai": NutrisiBahan(45.0, 2400, 5.0, 6.0, 0.30, 0.65, 11000, "Sumber protein nabati."),
    "Tepung ikan": NutrisiBahan(55.0, 2800, 8.0, 1.0, 6.00, 3.00, 14000, "Protein tinggi, pakai secukupnya."),
    "Bungkil kelapa": NutrisiBahan(20.0, 2000, 8.0, 12.0, 0.20, 0.60, 4500, "Alternatif protein lokal, serat tinggi."),
    "Tepung tulang/kapur pakan": NutrisiBahan(0.0, 0, 0.0, 0.0, 30.00, 15.00, 5000, "Sumber kalsium dan fosfor."),
    "Garam": NutrisiBahan(0.0, 0, 0.0, 0.0, 0.00, 0.00, 3000, "Jangan berlebihan."),
    "Premix vitamin-mineral": NutrisiBahan(0.0, 0, 0.0, 0.0, 0.00, 0.00, 25000, "Ikuti dosis merek premix."),
}

# Rentang target praktis. Bukan standar tunggal; disediakan sebagai panduan lapangan.
TARGET_NUTRISI = {
    "Starter (0-4 minggu)": {
        "protein_min": 18.0,
        "protein_max": 21.0,
        "energi_min": 2800,
        "energi_max": 3000,
        "kalsium_min": 0.8,
        "kalsium_max": 1.2,
        "fosfor_min": 0.35,
        "fosfor_max": 0.60,
    },
    "Grower (5-10 minggu)": {
        "protein_min": 16.0,
        "protein_max": 18.0,
        "energi_min": 2700,
        "energi_max": 2900,
        "kalsium_min": 0.75,
        "kalsium_max": 1.1,
        "fosfor_min": 0.35,
        "fosfor_max": 0.55,
    },
    "Finisher/Pembesaran akhir": {
        "protein_min": 15.0,
        "protein_max": 17.0,
        "energi_min": 2650,
        "energi_max": 2850,
        "kalsium_min": 0.70,
        "kalsium_max": 1.0,
        "fosfor_min": 0.30,
        "fosfor_max": 0.50,
    },
    "Induk/Petelur kampung": {
        "protein_min": 16.0,
        "protein_max": 18.0,
        "energi_min": 2600,
        "energi_max": 2800,
        "kalsium_min": 3.0,
        "kalsium_max": 4.2,
        "fosfor_min": 0.30,
        "fosfor_max": 0.55,
    },
}

# Formula contoh dibuat total 100% supaya peternak punya titik awal.
FORMULA_CONTOH = {
    "Starter (0-4 minggu)": {
        "Jagung giling": 48.0,
        "Dedak padi/bekatul": 16.0,
        "Bungkil kedelai": 24.0,
        "Tepung ikan": 8.0,
        "Bungkil kelapa": 1.5,
        "Tepung tulang/kapur pakan": 1.5,
        "Garam": 0.3,
        "Premix vitamin-mineral": 0.7,
    },
    "Grower (5-10 minggu)": {
        "Jagung giling": 50.0,
        "Dedak padi/bekatul": 24.0,
        "Bungkil kedelai": 15.0,
        "Tepung ikan": 5.0,
        "Bungkil kelapa": 3.0,
        "Tepung tulang/kapur pakan": 2.0,
        "Garam": 0.3,
        "Premix vitamin-mineral": 0.7,
    },
    "Finisher/Pembesaran akhir": {
        "Jagung giling": 53.0,
        "Dedak padi/bekatul": 28.0,
        "Bungkil kedelai": 10.0,
        "Tepung ikan": 3.5,
        "Bungkil kelapa": 3.0,
        "Tepung tulang/kapur pakan": 1.5,
        "Garam": 0.3,
        "Premix vitamin-mineral": 0.7,
    },
    "Induk/Petelur kampung": {
        "Jagung giling": 45.0,
        "Dedak padi/bekatul": 25.0,
        "Bungkil kedelai": 14.0,
        "Tepung ikan": 5.0,
        "Bungkil kelapa": 4.0,
        "Tepung tulang/kapur pakan": 6.0,
        "Garam": 0.3,
        "Premix vitamin-mineral": 0.7,
    },
}


# -----------------------------------------------------------------------------
# Fungsi utilitas
# -----------------------------------------------------------------------------
def rupiah(nilai: float) -> str:
    """Format angka menjadi Rupiah sederhana."""
    return f"Rp{nilai:,.0f}".replace(",", ".")


def normalisasi_komposisi(komposisi: Dict[str, float]) -> Dict[str, float]:
    """Menormalkan komposisi agar total menjadi 100%."""
    total = sum(max(v, 0) for v in komposisi.values())
    if total <= 0:
        return {nama: 0.0 for nama in komposisi}
    return {nama: (max(nilai, 0) / total) * 100 for nama, nilai in komposisi.items()}


def hitung_ransum(
    komposisi: Dict[str, float],
    harga_per_kg: Dict[str, float],
    jumlah_kg: float,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Menghitung kontribusi nutrisi, bobot, dan biaya tiap bahan."""
    baris = []
    ringkasan = {
        "protein": 0.0,
        "energi": 0.0,
        "lemak": 0.0,
        "serat": 0.0,
        "kalsium": 0.0,
        "fosfor": 0.0,
        "biaya_total": 0.0,
    }

    for nama, persen in komposisi.items():
        bahan = BAHAN_PAKAN[nama]
        kg = jumlah_kg * persen / 100
        biaya = kg * harga_per_kg[nama]

        kontribusi = {
            "protein": persen / 100 * bahan.protein,
            "energi": persen / 100 * bahan.energi,
            "lemak": persen / 100 * bahan.lemak,
            "serat": persen / 100 * bahan.serat,
            "kalsium": persen / 100 * bahan.kalsium,
            "fosfor": persen / 100 * bahan.fosfor,
        }

        for kunci, nilai in kontribusi.items():
            ringkasan[kunci] += nilai
        ringkasan["biaya_total"] += biaya

        if persen > 0:
            baris.append(
                {
                    "Bahan": nama,
                    "Persen (%)": round(persen, 2),
                    "Jumlah (kg)": round(kg, 2),
                    "Harga/kg": rupiah(harga_per_kg[nama]),
                    "Biaya": rupiah(biaya),
                    "Protein kontribusi (%)": round(kontribusi["protein"], 2),
                    "EM kontribusi (kkal/kg)": round(kontribusi["energi"], 0),
                }
            )

    ringkasan["biaya_per_kg"] = ringkasan["biaya_total"] / jumlah_kg if jumlah_kg else 0
    return pd.DataFrame(baris), ringkasan


def status_target(nilai: float, minimum: float, maximum: float) -> Tuple[str, str]:
    """Memberikan status kesesuaian nutrisi terhadap target."""
    if nilai < minimum:
        return "Kurang", "🔴"
    if nilai > maximum:
        return "Berlebih", "🟠"
    return "Sesuai", "🟢"


def tabel_evaluasi(ringkasan: Dict[str, float], target: Dict[str, float]) -> pd.DataFrame:
    rows = []
    spesifikasi = [
        ("Protein kasar", "%", ringkasan["protein"], target["protein_min"], target["protein_max"]),
        ("Energi metabolis", "kkal/kg", ringkasan["energi"], target["energi_min"], target["energi_max"]),
        ("Kalsium", "%", ringkasan["kalsium"], target["kalsium_min"], target["kalsium_max"]),
        ("Fosfor", "%", ringkasan["fosfor"], target["fosfor_min"], target["fosfor_max"]),
        ("Lemak kasar", "%", ringkasan["lemak"], 0, 999),
        ("Serat kasar", "%", ringkasan["serat"], 0, 999),
    ]

    for nutrien, satuan, nilai, minimum, maximum in spesifikasi:
        if nutrien in {"Lemak kasar", "Serat kasar"}:
            rows.append(
                {
                    "Nutrien": nutrien,
                    "Hasil": f"{nilai:.2f} {satuan}",
                    "Target": "Pantau sesuai kondisi bahan",
                    "Status": "ℹ️ Informasi",
                }
            )
            continue
        label, ikon = status_target(nilai, minimum, maximum)
        hasil = f"{nilai:.0f} {satuan}" if satuan == "kkal/kg" else f"{nilai:.2f} {satuan}"
        rows.append(
            {
                "Nutrien": nutrien,
                "Hasil": hasil,
                "Target": f"{minimum:g} - {maximum:g} {satuan}",
                "Status": f"{ikon} {label}",
            }
        )
    return pd.DataFrame(rows)


def buat_saran(ringkasan: Dict[str, float], target: Dict[str, float]) -> Iterable[str]:
    """Saran praktis agar formulasi lebih mudah diperbaiki."""
    if ringkasan["protein"] < target["protein_min"]:
        yield "Protein kurang: naikkan bungkil kedelai atau tepung ikan sedikit demi sedikit, lalu kurangi jagung/dedak agar total tetap 100%."
    elif ringkasan["protein"] > target["protein_max"]:
        yield "Protein berlebih: kurangi bahan protein tinggi seperti tepung ikan/bungkil kedelai untuk menekan biaya."

    if ringkasan["energi"] < target["energi_min"]:
        yield "Energi kurang: tambah jagung giling atau bahan energi lain yang tersedia di daerah Anda."
    elif ringkasan["energi"] > target["energi_max"]:
        yield "Energi berlebih: kurangi jagung dan seimbangkan dengan dedak atau bahan berserat secukupnya."

    if ringkasan["kalsium"] < target["kalsium_min"]:
        yield "Kalsium kurang: tambah kapur pakan/tepung tulang, terutama untuk induk atau ayam petelur."
    elif ringkasan["kalsium"] > target["kalsium_max"]:
        yield "Kalsium berlebih: kurangi tepung tulang/kapur pakan agar tidak mengganggu konsumsi dan keseimbangan mineral."

    if ringkasan["fosfor"] < target["fosfor_min"]:
        yield "Fosfor kurang: pertimbangkan tepung tulang atau sumber mineral lain sesuai rekomendasi teknis."
    elif ringkasan["fosfor"] > target["fosfor_max"]:
        yield "Fosfor berlebih: kurangi bahan mineral/fosfor tinggi dan evaluasi kembali kebutuhan fase ayam."

    if ringkasan["serat"] > 7:
        yield "Serat cukup tinggi: batasi dedak atau bungkil kelapa bila pertumbuhan ayam melambat atau konsumsi menurun."

    yield "Uji perubahan formula dalam skala kecil dahulu sebelum dipakai untuk seluruh kandang."


def csv_download(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


# -----------------------------------------------------------------------------
# Tampilan aplikasi
# -----------------------------------------------------------------------------
st.title("🐔 Kalkulator Pakan Ayam Kampung")
st.caption("Aplikasi sederhana untuk membantu peternak menghitung komposisi, nutrisi, jumlah bahan, dan estimasi biaya ransum.")

with st.expander("Petunjuk singkat", expanded=True):
    st.markdown(
        """
        1. Pilih **fase ayam** sesuai umur atau tujuan pemeliharaan.
        2. Masukkan **jumlah pakan** yang ingin dibuat, misalnya 50 kg atau 100 kg.
        3. Gunakan **formula contoh** sebagai titik awal, lalu ubah persentase bahan sesuai ketersediaan bahan di daerah Anda.
        4. Ubah **harga bahan/kg** agar estimasi biaya sesuai harga pasar lokal.
        5. Lihat tabel evaluasi. Status hijau berarti sudah masuk rentang target praktis.
        """
    )

st.sidebar.header("1. Pengaturan utama")
fase = st.sidebar.selectbox("Fase ayam", list(TARGET_NUTRISI.keys()))
jumlah_pakan = st.sidebar.number_input("Jumlah pakan yang dibuat (kg)", min_value=1.0, max_value=5000.0, value=100.0, step=1.0)
mode = st.sidebar.radio("Mode komposisi", ["Pakai formula contoh", "Atur manual"], horizontal=False)

st.sidebar.header("2. Harga bahan lokal")
harga_input: Dict[str, float] = {}
for nama, bahan in BAHAN_PAKAN.items():
    harga_input[nama] = st.sidebar.number_input(
        f"{nama} (Rp/kg)",
        min_value=0,
        max_value=100000,
        value=bahan.harga,
        step=500,
        key=f"harga_{nama}",
    )

st.sidebar.header("3. Komposisi bahan")
komposisi_awal = FORMULA_CONTOH[fase]
komposisi_input: Dict[str, float] = {}

if mode == "Pakai formula contoh":
    st.sidebar.info("Formula contoh bisa langsung dipakai sebagai simulasi awal.")
    komposisi_input = dict(komposisi_awal)
else:
    st.sidebar.caption("Isi angka persen. Aplikasi akan menormalkan total menjadi 100% bila total belum tepat.")
    for nama in BAHAN_PAKAN:
        komposisi_input[nama] = st.sidebar.number_input(
            nama,
            min_value=0.0,
            max_value=100.0,
            value=float(komposisi_awal.get(nama, 0.0)),
            step=0.1,
            key=f"komposisi_{fase}_{nama}",
        )

komposisi_normal = normalisasi_komposisi(komposisi_input)
total_input = sum(komposisi_input.values())

tabel_komposisi, ringkasan = hitung_ransum(komposisi_normal, harga_input, jumlah_pakan)
evaluasi = tabel_evaluasi(ringkasan, TARGET_NUTRISI[fase])

kartu1, kartu2, kartu3, kartu4 = st.columns(4)
kartu1.metric("Total input", f"{total_input:.1f}%")
kartu2.metric("Setelah normalisasi", f"{sum(komposisi_normal.values()):.1f}%")
kartu3.metric("Biaya total", rupiah(ringkasan["biaya_total"]))
kartu4.metric("Biaya per kg", rupiah(ringkasan["biaya_per_kg"]))

if abs(total_input - 100) > 0.01:
    st.warning(
        "Total komposisi awal belum 100%. Aplikasi sudah menormalkan perhitungan menjadi 100%, "
        "tetapi sebaiknya Anda menyesuaikan angka manual agar totalnya tepat."
    )

kolom_kiri, kolom_kanan = st.columns([1.25, 1])

with kolom_kiri:
    st.subheader("Komposisi dan kebutuhan bahan")
    st.dataframe(tabel_komposisi, use_container_width=True, hide_index=True)

    st.download_button(
        "Unduh komposisi sebagai CSV",
        data=csv_download(tabel_komposisi),
        file_name=f"komposisi_pakan_{fase.lower().replace(' ', '_').replace('/', '-')}.csv",
        mime="text/csv",
    )

with kolom_kanan:
    st.subheader("Evaluasi nutrisi")
    st.dataframe(evaluasi, use_container_width=True, hide_index=True)

    st.subheader("Saran perbaikan")
    for saran in buat_saran(ringkasan, TARGET_NUTRISI[fase]):
        st.write(f"- {saran}")

st.divider()

kolom_info1, kolom_info2 = st.columns(2)
with kolom_info1:
    st.subheader("Data nutrisi bahan")
    df_bahan = pd.DataFrame(
        [
            {
                "Bahan": nama,
                "Protein (%)": bahan.protein,
                "EM (kkal/kg)": bahan.energi,
                "Lemak (%)": bahan.lemak,
                "Serat (%)": bahan.serat,
                "Ca (%)": bahan.kalsium,
                "P (%)": bahan.fosfor,
                "Catatan": bahan.catatan,
            }
            for nama, bahan in BAHAN_PAKAN.items()
        ]
    )
    st.dataframe(df_bahan, use_container_width=True, hide_index=True)

with kolom_info2:
    st.subheader("Catatan penggunaan")
    st.markdown(
        """
        - Angka nutrisi adalah **perkiraan**. Nilai aktual dapat berubah karena varietas bahan, kadar air, penyimpanan, dan pemasok.
        - Untuk pakan skala usaha, mintalah pendampingan penyuluh, nutrisionis ternak, atau laboratorium pakan.
        - Pastikan bahan tidak berjamur, tidak berbau tengik, dan disimpan di tempat kering.
        - Jangan menaikkan garam/premix sembarangan. Ikuti batas penggunaan pada label produk.
        """
    )

st.caption("Versi perbaikan: kode dirapikan, formula dapat dinormalisasi, biaya dapat dihitung, dan hasil bisa diunduh.")
