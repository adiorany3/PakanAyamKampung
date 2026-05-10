"""
Kalkulator dan Optimizer Pakan Ayam Kampung Indonesia
======================================================

Aplikasi Streamlit untuk membantu peternak menyusun ransum ayam kampung/KUB
berdasarkan ketersediaan bahan lokal, target nutrisi, dan harga bahan pakan.

Jalankan:
    streamlit run app.py

Catatan:
- Data nutrisi adalah pendekatan praktis. Untuk usaha komersial, sesuaikan dengan
  hasil uji lab bahan pakan, rekomendasi penyuluh/nutrisionis, dan kondisi kandang.
- Optimasi memakai linear programming untuk mencari biaya terendah dengan batasan
  nutrisi dan batas pemakaian bahan yang diedit pengguna.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

try:
    from scipy.optimize import linprog
except Exception:  # pragma: no cover - hanya fallback bila scipy belum terpasang
    linprog = None


# =============================================================================
# Konfigurasi halaman
# =============================================================================
st.set_page_config(
    page_title="Optimizer Pakan Ayam Kampung",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# Data dasar nutrisi dan target
# =============================================================================
@dataclass(frozen=True)
class BahanPakan:
    kategori: str
    protein: float  # % as-fed
    energi: float  # kkal/kg as-fed, pendekatan energi metabolis unggas
    lemak: float  # %
    serat: float  # %
    kalsium: float  # %
    fosfor: float  # %
    lisin: float  # %
    metionin: float  # %
    harga: int  # Rp/kg, contoh awal yang dapat diedit
    min_persen: float  # batas bawah default, %
    max_persen: float  # batas atas default, %
    catatan: str


BAHAN_PAKAN: Dict[str, BahanPakan] = {
    "Jagung giling": BahanPakan(
        "Energi",
        8.8,
        3350,
        3.8,
        2.3,
        0.02,
        0.28,
        0.26,
        0.18,
        6000,
        30.0,
        65.0,
        "Energi utama; pilih jagung kering, tidak berjamur, dan giling halus-sedang.",
    ),
    "Dedak padi/bekatul": BahanPakan(
        "Energi + serat",
        12.0,
        2400,
        12.0,
        11.0,
        0.10,
        1.20,
        0.55,
        0.25,
        3500,
        0.0,
        25.0,
        "Murah dan mudah dicari, tetapi serat/minyak tinggi; hindari yang tengik/berjamur.",
    ),
    "Bungkil kedelai": BahanPakan(
        "Protein",
        44.0,
        2450,
        1.5,
        6.0,
        0.30,
        0.65,
        2.80,
        0.62,
        11000,
        3.0,
        35.0,
        "Sumber protein nabati berkualitas; biasanya menaikkan biaya tetapi memperbaiki pertumbuhan.",
    ),
    "Tepung ikan": BahanPakan(
        "Protein hewani",
        55.0,
        2800,
        8.0,
        1.0,
        5.50,
        3.00,
        4.20,
        1.50,
        14000,
        0.0,
        10.0,
        "Protein dan mineral tinggi; gunakan secukupnya agar biaya dan aroma pakan tidak berlebihan.",
    ),
    "Bungkil kelapa": BahanPakan(
        "Protein lokal",
        20.0,
        2100,
        8.0,
        13.0,
        0.20,
        0.60,
        0.60,
        0.30,
        4500,
        0.0,
        12.0,
        "Alternatif lokal murah, tetapi serat tinggi; batasi bila ayam lambat tumbuh.",
    ),
    "Gaplek/tepung singkong": BahanPakan(
        "Energi lokal",
        2.5,
        3000,
        0.5,
        3.0,
        0.10,
        0.08,
        0.10,
        0.05,
        3000,
        0.0,
        12.0,
        "Sumber energi murah di beberapa daerah; jangan terlalu tinggi karena protein sangat rendah.",
    ),
    "Minyak nabati": BahanPakan(
        "Energi pekat",
        0.0,
        8500,
        100.0,
        0.0,
        0.00,
        0.00,
        0.00,
        0.00,
        14000,
        0.0,
        3.0,
        "Dipakai sedikit untuk menaikkan energi; pencampuran harus merata.",
    ),
    "Kapur pakan": BahanPakan(
        "Mineral",
        0.0,
        0,
        0.0,
        0.0,
        38.0,
        0.00,
        0.00,
        0.00,
        4000,
        0.0,
        8.0,
        "Sumber kalsium murah; penting untuk induk/petelur, tetapi jangan berlebihan.",
    ),
    "Tepung tulang": BahanPakan(
        "Mineral",
        0.0,
        0,
        0.0,
        0.0,
        24.0,
        12.0,
        0.00,
        0.00,
        7000,
        0.0,
        3.0,
        "Sumber Ca dan P; mutu sangat bervariasi, pakai dari pemasok tepercaya.",
    ),
    "Garam": BahanPakan(
        "Aditif",
        0.0,
        0,
        0.0,
        0.0,
        0.00,
        0.00,
        0.00,
        0.00,
        3000,
        0.2,
        0.4,
        "Jangan melebihi batas; kelebihan garam dapat mengganggu konsumsi dan kesehatan.",
    ),
    "Premix vitamin-mineral": BahanPakan(
        "Aditif",
        0.0,
        0,
        0.0,
        0.0,
        0.00,
        0.00,
        0.00,
        0.00,
        25000,
        0.3,
        1.0,
        "Ikuti dosis produsen premix; jangan diganti sembarang bahan.",
    ),
}

# Target praktis. Nilai tengah mengacu pada pedoman KUB, sedangkan rentang dibuat
# agar optimasi tidak terlalu kaku karena nilai bahan lokal bervariasi.
TARGET_NUTRISI = {
    "Starter KUB (0-3 minggu)": {
        "protein_min": 19.5,
        "protein_max": 22.0,
        "energi_min": 2900,
        "energi_max": 3100,
        "kalsium_min": 0.85,
        "kalsium_max": 1.20,
        "fosfor_min": 0.50,
        "fosfor_max": 0.70,
        "lisin_min": 1.10,
        "metionin_min": 0.45,
        "serat_max": 6.5,
        "deskripsi": "Fase paling sensitif; kualitas pakan, suhu brooder, dan air minum sangat menentukan performa.",
        "hari_default": 21,
        "konsumsi_g_default": 18,
    },
    "Grower KUB (4-12 minggu)": {
        "protein_min": 17.0,
        "protein_max": 18.5,
        "energi_min": 2750,
        "energi_max": 2920,
        "kalsium_min": 0.80,
        "kalsium_max": 1.10,
        "fosfor_min": 0.45,
        "fosfor_max": 0.65,
        "lisin_min": 0.90,
        "metionin_min": 0.40,
        "serat_max": 7.0,
        "deskripsi": "Fase pembesaran; fokus pada biaya/kg bobot hidup, keseragaman, dan mortalitas rendah.",
        "hari_default": 63,
        "konsumsi_g_default": 50,
    },
    "Finisher/pembesaran akhir": {
        "protein_min": 15.5,
        "protein_max": 17.5,
        "energi_min": 2680,
        "energi_max": 2900,
        "kalsium_min": 0.70,
        "kalsium_max": 1.05,
        "fosfor_min": 0.40,
        "fosfor_max": 0.60,
        "lisin_min": 0.80,
        "metionin_min": 0.35,
        "serat_max": 7.5,
        "deskripsi": "Fase menekan biaya tanpa menjatuhkan performa; cocok untuk ayam siap potong.",
        "hari_default": 28,
        "konsumsi_g_default": 70,
    },
    "Layer/induk KUB (>12 minggu)": {
        "protein_min": 16.0,
        "protein_max": 17.5,
        "energi_min": 2700,
        "energi_max": 2900,
        "kalsium_min": 3.00,
        "kalsium_max": 3.80,
        "fosfor_min": 0.45,
        "fosfor_max": 0.65,
        "lisin_min": 0.90,
        "metionin_min": 0.40,
        "serat_max": 7.5,
        "deskripsi": "Fase produksi telur; kalsium harus cukup agar kualitas kerabang terjaga.",
        "hari_default": 30,
        "konsumsi_g_default": 80,
    },
}

FORMULA_CONTOH = {
    "Starter KUB (0-3 minggu)": {
        "Jagung giling": 46.0,
        "Dedak padi/bekatul": 12.0,
        "Bungkil kedelai": 24.0,
        "Tepung ikan": 8.0,
        "Bungkil kelapa": 5.0,
        "Gaplek/tepung singkong": 2.0,
        "Minyak nabati": 1.0,
        "Kapur pakan": 1.0,
        "Tepung tulang": 0.0,
        "Garam": 0.3,
        "Premix vitamin-mineral": 0.7,
    },
    "Grower KUB (4-12 minggu)": {
        "Jagung giling": 50.0,
        "Dedak padi/bekatul": 20.0,
        "Bungkil kedelai": 16.0,
        "Tepung ikan": 5.0,
        "Bungkil kelapa": 5.0,
        "Gaplek/tepung singkong": 1.0,
        "Minyak nabati": 0.0,
        "Kapur pakan": 2.0,
        "Tepung tulang": 0.0,
        "Garam": 0.3,
        "Premix vitamin-mineral": 0.7,
    },
    "Finisher/pembesaran akhir": {
        "Jagung giling": 54.0,
        "Dedak padi/bekatul": 24.0,
        "Bungkil kedelai": 12.0,
        "Tepung ikan": 3.0,
        "Bungkil kelapa": 4.0,
        "Gaplek/tepung singkong": 0.0,
        "Minyak nabati": 0.0,
        "Kapur pakan": 2.0,
        "Tepung tulang": 0.0,
        "Garam": 0.3,
        "Premix vitamin-mineral": 0.7,
    },
    "Layer/induk KUB (>12 minggu)": {
        "Jagung giling": 45.0,
        "Dedak padi/bekatul": 20.0,
        "Bungkil kedelai": 14.0,
        "Tepung ikan": 5.0,
        "Bungkil kelapa": 5.0,
        "Gaplek/tepung singkong": 0.0,
        "Minyak nabati": 0.0,
        "Kapur pakan": 9.0,
        "Tepung tulang": 1.0,
        "Garam": 0.3,
        "Premix vitamin-mineral": 0.7,
    },
}

NUTRIENT_COLUMNS = {
    "protein": "Protein (%)",
    "energi": "EM (kkal/kg)",
    "lemak": "Lemak (%)",
    "serat": "Serat (%)",
    "kalsium": "Ca (%)",
    "fosfor": "P (%)",
    "lisin": "Lisin (%)",
    "metionin": "Metionin (%)",
}


# =============================================================================
# Fungsi utilitas
# =============================================================================
def rupiah(nilai: float) -> str:
    return f"Rp{nilai:,.0f}".replace(",", ".")


def persen(nilai: float) -> str:
    return f"{nilai:.2f}%".replace(".", ",")


def bahan_to_dataframe() -> pd.DataFrame:
    rows = []
    for nama, bahan in BAHAN_PAKAN.items():
        rows.append(
            {
                "Pakai": True,
                "Bahan": nama,
                "Kategori": bahan.kategori,
                "Harga Rp/kg": bahan.harga,
                "Min %": bahan.min_persen,
                "Max %": bahan.max_persen,
                "Protein (%)": bahan.protein,
                "EM (kkal/kg)": bahan.energi,
                "Lemak (%)": bahan.lemak,
                "Serat (%)": bahan.serat,
                "Ca (%)": bahan.kalsium,
                "P (%)": bahan.fosfor,
                "Lisin (%)": bahan.lisin,
                "Metionin (%)": bahan.metionin,
                "Catatan": bahan.catatan,
            }
        )
    return pd.DataFrame(rows)


def sanitize_bahan_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    numeric_cols = [
        "Harga Rp/kg",
        "Min %",
        "Max %",
        "Protein (%)",
        "EM (kkal/kg)",
        "Lemak (%)",
        "Serat (%)",
        "Ca (%)",
        "P (%)",
        "Lisin (%)",
        "Metionin (%)",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    df["Pakai"] = df["Pakai"].astype(bool)
    df.loc[~df["Pakai"], ["Min %", "Max %"]] = 0.0
    df["Min %"] = df["Min %"].clip(0, 100)
    df["Max %"] = df["Max %"].clip(0, 100)
    df["Harga Rp/kg"] = df["Harga Rp/kg"].clip(0, 1_000_000)
    df.loc[df["Max %"] < df["Min %"], "Max %"] = df["Min %"]
    return df


def normalisasi_komposisi(komposisi: Dict[str, float]) -> Dict[str, float]:
    total = sum(max(0.0, float(v)) for v in komposisi.values())
    if total <= 0:
        return {nama: 0.0 for nama in komposisi}
    return {nama: max(0.0, float(v)) / total * 100 for nama, v in komposisi.items()}


def nutrient_vector(df: pd.DataFrame, nutrient: str) -> np.ndarray:
    return df[NUTRIENT_COLUMNS[nutrient]].to_numpy(dtype=float)


def hitung_ransum(
    df_bahan: pd.DataFrame,
    komposisi: Dict[str, float],
    jumlah_kg: float,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    rows = []
    ringkasan = {
        "protein": 0.0,
        "energi": 0.0,
        "lemak": 0.0,
        "serat": 0.0,
        "kalsium": 0.0,
        "fosfor": 0.0,
        "lisin": 0.0,
        "metionin": 0.0,
        "biaya_total": 0.0,
    }

    lookup = df_bahan.set_index("Bahan").to_dict("index")
    for nama, pct in komposisi.items():
        if nama not in lookup:
            continue
        row = lookup[nama]
        kg = jumlah_kg * pct / 100.0
        biaya = kg * float(row["Harga Rp/kg"])
        kontribusi = {
            "protein": pct / 100.0 * float(row["Protein (%)"]),
            "energi": pct / 100.0 * float(row["EM (kkal/kg)"]),
            "lemak": pct / 100.0 * float(row["Lemak (%)"]),
            "serat": pct / 100.0 * float(row["Serat (%)"]),
            "kalsium": pct / 100.0 * float(row["Ca (%)"]),
            "fosfor": pct / 100.0 * float(row["P (%)"]),
            "lisin": pct / 100.0 * float(row["Lisin (%)"]),
            "metionin": pct / 100.0 * float(row["Metionin (%)"]),
        }
        for k, v in kontribusi.items():
            ringkasan[k] += v
        ringkasan["biaya_total"] += biaya

        if pct > 0.0001:
            rows.append(
                {
                    "Bahan": nama,
                    "Persen (%)": round(pct, 2),
                    "Jumlah (kg)": round(kg, 3),
                    "Harga/kg": rupiah(row["Harga Rp/kg"]),
                    "Biaya": rupiah(biaya),
                    "Protein kontribusi (%)": round(kontribusi["protein"], 3),
                    "EM kontribusi (kkal/kg)": round(kontribusi["energi"], 0),
                }
            )

    ringkasan["biaya_per_kg"] = ringkasan["biaya_total"] / jumlah_kg if jumlah_kg > 0 else 0.0
    return pd.DataFrame(rows), ringkasan


def status_nutrisi(nilai: float, minimum: Optional[float], maximum: Optional[float]) -> Tuple[str, str]:
    if minimum is not None and nilai < minimum:
        return "Kurang", "🔴"
    if maximum is not None and nilai > maximum:
        return "Berlebih", "🟠"
    return "Sesuai", "🟢"


def tabel_evaluasi(ringkasan: Dict[str, float], target: Dict[str, float]) -> pd.DataFrame:
    specs = [
        ("Protein kasar", "%", ringkasan["protein"], target["protein_min"], target["protein_max"]),
        ("Energi metabolis", "kkal/kg", ringkasan["energi"], target["energi_min"], target["energi_max"]),
        ("Kalsium", "%", ringkasan["kalsium"], target["kalsium_min"], target["kalsium_max"]),
        ("Fosfor", "%", ringkasan["fosfor"], target["fosfor_min"], target["fosfor_max"]),
        ("Lisin", "%", ringkasan["lisin"], target["lisin_min"], None),
        ("Metionin", "%", ringkasan["metionin"], target["metionin_min"], None),
        ("Serat kasar", "%", ringkasan["serat"], None, target["serat_max"]),
        ("Lemak kasar", "%", ringkasan["lemak"], None, 9.0),
    ]
    rows = []
    for nutrien, satuan, nilai, minimum, maximum in specs:
        label, ikon = status_nutrisi(nilai, minimum, maximum)
        if satuan == "kkal/kg":
            hasil = f"{nilai:.0f} {satuan}"
            if minimum is not None and maximum is not None:
                target_text = f"{minimum:.0f} - {maximum:.0f} {satuan}"
            elif minimum is not None:
                target_text = f"min. {minimum:.0f} {satuan}"
            else:
                target_text = f"maks. {maximum:.0f} {satuan}"
        else:
            hasil = f"{nilai:.2f} {satuan}"
            if minimum is not None and maximum is not None:
                target_text = f"{minimum:g} - {maximum:g} {satuan}"
            elif minimum is not None:
                target_text = f"min. {minimum:g} {satuan}"
            else:
                target_text = f"maks. {maximum:g} {satuan}"
        rows.append({"Nutrien": nutrien, "Hasil": hasil, "Target": target_text, "Status": f"{ikon} {label}"})
    return pd.DataFrame(rows)




def sesuaikan_dengan_ketersediaan(
    komposisi: Dict[str, float], df_bahan: pd.DataFrame
) -> Tuple[Dict[str, float], List[str]]:
    """Nolkan bahan yang tidak dicentang Pakai pada mode manual/contoh."""
    df = sanitize_bahan_df(df_bahan)
    available = df.set_index("Bahan")["Pakai"].to_dict()
    adjusted: Dict[str, float] = {}
    warnings: List[str] = []
    for nama in BAHAN_PAKAN:
        nilai = float(komposisi.get(nama, 0.0))
        if not bool(available.get(nama, True)):
            if nilai > 0:
                warnings.append(f"{nama} disetel 0% karena tidak dicentang Pakai.")
            nilai = 0.0
        adjusted[nama] = nilai
    return adjusted, warnings


def cek_pelanggaran_batas_manual(komposisi: Dict[str, float], df_bahan: pd.DataFrame) -> List[str]:
    """Beri peringatan bila formula manual/contoh melewati Max % pengguna."""
    df = sanitize_bahan_df(df_bahan).set_index("Bahan")
    warnings: List[str] = []
    for nama, pct in komposisi.items():
        if nama not in df.index:
            continue
        max_pct = float(df.loc[nama, "Max %"])
        if pct > max_pct + 1e-6:
            warnings.append(f"{nama} {pct:.2f}% melebihi Max % {max_pct:.2f}%. Gunakan mode optimasi atau naikkan Max % bila memang aman/tersedia.")
    return warnings

def solve_least_cost(
    df_bahan: pd.DataFrame,
    target: Dict[str, float],
    pakai_batas_asam_amino: bool,
) -> Tuple[Optional[Dict[str, float]], str]:
    if linprog is None:
        return None, "scipy belum terpasang. Jalankan: pip install scipy"

    df = sanitize_bahan_df(df_bahan)
    if df.empty:
        return None, "Data bahan kosong."

    min_sum = df["Min %"].sum()
    max_sum = df["Max %"].sum()
    if min_sum > 100.0:
        return None, f"Total Min % = {min_sum:.2f}%, melebihi 100%. Turunkan batas minimum bahan."
    if max_sum < 100.0:
        return None, f"Total Max % = {max_sum:.2f}%, kurang dari 100%. Naikkan batas maksimum atau aktifkan bahan lain."

    n = len(df)
    c = df["Harga Rp/kg"].to_numpy(dtype=float)
    bounds = [(lo / 100.0, hi / 100.0) for lo, hi in zip(df["Min %"], df["Max %"])]

    a_ub: List[np.ndarray] = []
    b_ub: List[float] = []

    def add_min(nutrient: str, min_value: float) -> None:
        a_ub.append(-nutrient_vector(df, nutrient))
        b_ub.append(-float(min_value))

    def add_max(nutrient: str, max_value: float) -> None:
        a_ub.append(nutrient_vector(df, nutrient))
        b_ub.append(float(max_value))

    add_min("protein", target["protein_min"])
    add_max("protein", target["protein_max"])
    add_min("energi", target["energi_min"])
    add_max("energi", target["energi_max"])
    add_min("kalsium", target["kalsium_min"])
    add_max("kalsium", target["kalsium_max"])
    add_min("fosfor", target["fosfor_min"])
    add_max("fosfor", target["fosfor_max"])
    add_max("serat", target["serat_max"])
    add_max("lemak", 9.0)

    if pakai_batas_asam_amino:
        add_min("lisin", target["lisin_min"])
        add_min("metionin", target["metionin_min"])

    result = linprog(
        c,
        A_ub=np.array(a_ub),
        b_ub=np.array(b_ub),
        A_eq=np.ones((1, n)),
        b_eq=np.array([1.0]),
        bounds=bounds,
        method="highs",
    )

    if not result.success:
        return None, (
            "Optimasi tidak menemukan kombinasi yang memenuhi semua batas. "
            "Coba longgarkan Max/Min bahan, naikkan batas tepung ikan/bungkil kedelai, "
            "atau matikan batas asam amino bila sedang dipakai."
        )

    komposisi = {nama: float(fraksi * 100.0) for nama, fraksi in zip(df["Bahan"], result.x)}
    return komposisi, "Optimasi berhasil. Formula yang ditampilkan adalah biaya terendah dalam batas yang dipilih."


def buat_saran(ringkasan: Dict[str, float], target: Dict[str, float], df_bahan: pd.DataFrame) -> Iterable[str]:
    if ringkasan["protein"] < target["protein_min"]:
        yield "Protein kurang: naikkan bungkil kedelai/tepung ikan atau turunkan bahan energi rendah protein seperti gaplek/jagung."
    elif ringkasan["protein"] > target["protein_max"]:
        yield "Protein berlebih: kurangi tepung ikan/bungkil kedelai karena biasanya menjadi sumber biaya tinggi."

    if ringkasan["energi"] < target["energi_min"]:
        yield "Energi kurang: tambah jagung giling atau sedikit minyak nabati; jangan hanya menaikkan dedak karena seratnya tinggi."
    elif ringkasan["energi"] > target["energi_max"]:
        yield "Energi berlebih: kurangi jagung/minyak dan cek kembali kebutuhan fase ayam."

    if ringkasan["kalsium"] < target["kalsium_min"]:
        yield "Kalsium kurang: tambah kapur pakan/tepung tulang, terutama untuk induk atau ayam petelur."
    elif ringkasan["kalsium"] > target["kalsium_max"]:
        yield "Kalsium berlebih: kurangi kapur pakan/tepung tulang agar mineral tidak mengganggu konsumsi."

    if ringkasan["fosfor"] < target["fosfor_min"]:
        yield "Fosfor kurang: pertimbangkan tepung tulang/DCP sesuai ketersediaan lokal."
    elif ringkasan["fosfor"] > target["fosfor_max"]:
        yield "Fosfor berlebih: kurangi tepung ikan/tepung tulang/dedak bila jumlahnya tinggi."

    if ringkasan["lisin"] < target["lisin_min"]:
        yield "Lisin di bawah target: untuk pertumbuhan cepat, prioritaskan bungkil kedelai atau tepung ikan yang mutunya baik."
    if ringkasan["metionin"] < target["metionin_min"]:
        yield "Metionin di bawah target: formula bahan lokal sering kurang metionin; untuk usaha besar, konsultasikan penggunaan asam amino sintetis/premix khusus."

    if ringkasan["serat"] > target["serat_max"]:
        yield "Serat terlalu tinggi: batasi dedak dan bungkil kelapa karena bisa menurunkan kecernaan dan pertambahan bobot."

    # Insight berbasis harga bahan
    df_eff = biaya_efektif_bahan(df_bahan)
    if not df_eff.empty:
        protein_termurah = df_eff.dropna(subset=["Rp/kg protein"]).sort_values("Rp/kg protein").head(1)
        energi_termurah = df_eff.dropna(subset=["Rp/1000 kkal EM"]).sort_values("Rp/1000 kkal EM").head(1)
        if not protein_termurah.empty:
            row = protein_termurah.iloc[0]
            yield f"Protein paling murah menurut harga input saat ini: {row['Bahan']} sekitar {rupiah(row['Rp/kg protein'])} per kg protein kasar. Tetap ikuti batas pemakaian agar ransum seimbang."
        if not energi_termurah.empty:
            row = energi_termurah.iloc[0]
            yield f"Energi paling murah menurut harga input saat ini: {row['Bahan']} sekitar {rupiah(row['Rp/1000 kkal EM'])} per 1000 kkal EM."

    yield "Uji formula baru pada sebagian kecil ayam selama 7-14 hari sebelum diterapkan ke seluruh kandang. Amati konsumsi, feses, bobot, dan mortalitas."


def biaya_efektif_bahan(df_bahan: pd.DataFrame) -> pd.DataFrame:
    df = sanitize_bahan_df(df_bahan)
    rows = []
    for _, row in df.iterrows():
        harga = float(row["Harga Rp/kg"])
        protein = float(row["Protein (%)"])
        energi = float(row["EM (kkal/kg)"])
        rows.append(
            {
                "Bahan": row["Bahan"],
                "Kategori": row["Kategori"],
                "Harga Rp/kg": harga,
                "Rp/kg protein": np.nan if protein <= 0 else harga / (protein / 100.0),
                "Rp/1000 kkal EM": np.nan if energi <= 0 else harga / (energi / 1000.0),
                "Catatan batas": f"{row['Min %']:g}-{row['Max %']:g}%",
            }
        )
    return pd.DataFrame(rows)


def csv_download(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def build_shopping_list(tabel_komposisi: pd.DataFrame) -> pd.DataFrame:
    if tabel_komposisi.empty:
        return pd.DataFrame()
    df = tabel_komposisi[["Bahan", "Jumlah (kg)", "Biaya"]].copy()
    df["Checklist beli"] = "☐"
    return df[["Checklist beli", "Bahan", "Jumlah (kg)", "Biaya"]]


def manual_composition_editor(fase: str) -> Dict[str, float]:
    initial = FORMULA_CONTOH[fase]
    df_manual = pd.DataFrame(
        [{"Bahan": nama, "Persen (%)": float(initial.get(nama, 0.0))} for nama in BAHAN_PAKAN]
    )
    edited = st.data_editor(
        df_manual,
        key=f"manual_{fase}",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Persen (%)": st.column_config.NumberColumn("Persen (%)", min_value=0.0, max_value=100.0, step=0.1),
        },
        disabled=["Bahan"],
    )
    return {str(row["Bahan"]): float(row["Persen (%)"]) for _, row in edited.iterrows()}


def html_info_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div style="border:1px solid rgba(49,51,63,.2); border-radius:16px; padding:16px; height:100%;">
            <h4 style="margin-top:0;">{title}</h4>
            <p style="margin-bottom:0;">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Tampilan utama
# =============================================================================
st.title("🐔 Optimizer Pakan Ayam Kampung Indonesia")
st.caption(
    "Hitung formula ransum, cari biaya paling efisien, cek target nutrisi, dan baca panduan pemeliharaan praktis untuk kondisi peternak Indonesia."
)

with st.expander("Cara pakai cepat", expanded=True):
    st.markdown(
        """
        1. Pilih fase ayam dan jumlah pakan yang ingin dibuat.
        2. Edit harga bahan sesuai pasar lokal di daerah Anda.
        3. Pilih **Optimasi biaya otomatis** untuk mencari formula termurah yang masih memenuhi target utama nutrisi.
        4. Bila bahan tertentu tidak tersedia, hilangkan centang **Pakai** atau ubah batas **Max %** menjadi 0.
        5. Baca tab **Insight biaya** dan **Pemeliharaan** sebelum menerapkan formula di kandang.
        """
    )

st.sidebar.header("Pengaturan utama")
fase = st.sidebar.selectbox("Fase ayam", list(TARGET_NUTRISI.keys()))
target = TARGET_NUTRISI[fase]
jumlah_pakan = st.sidebar.number_input("Jumlah pakan yang dibuat (kg)", min_value=1.0, max_value=20_000.0, value=100.0, step=1.0)
mode = st.sidebar.radio(
    "Mode formulasi",
    ["Optimasi biaya otomatis", "Pakai formula contoh", "Atur manual"],
    index=0,
)
pakai_batas_asam_amino = st.sidebar.checkbox(
    "Aktifkan batas lisin & metionin pada optimasi",
    value=False,
    help="Bisa membuat optimasi gagal bila bahan lokal terbatas. Tanpa opsi ini, lisin/metionin tetap dievaluasi sebagai informasi.",
)

st.sidebar.header("Kalkulator kebutuhan pakan")
jumlah_ayam = st.sidebar.number_input("Jumlah ayam (ekor)", min_value=1, max_value=100_000, value=100, step=10)
hari_pakai = st.sidebar.number_input("Periode pakai pakan (hari)", min_value=1, max_value=365, value=int(target["hari_default"]), step=1)
konsumsi_g = st.sidebar.number_input(
    "Konsumsi rata-rata (gram/ekor/hari)",
    min_value=1,
    max_value=250,
    value=int(target["konsumsi_g_default"]),
    step=1,
)
estimasi_kebutuhan = jumlah_ayam * hari_pakai * konsumsi_g / 1000.0
st.sidebar.info(f"Estimasi kebutuhan periode ini: {estimasi_kebutuhan:,.1f} kg".replace(",", "."))

# Editor bahan pakan
st.subheader("1) Harga, ketersediaan, dan batas pemakaian bahan")
st.caption("Edit harga sesuai daerah Anda. Ubah Min/Max % untuk menyesuaikan ketersediaan dan keamanan penggunaan bahan.")
base_df = bahan_to_dataframe()
edited_df = st.data_editor(
    base_df,
    key="bahan_editor",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Pakai": st.column_config.CheckboxColumn("Pakai"),
        "Harga Rp/kg": st.column_config.NumberColumn("Harga Rp/kg", min_value=0, max_value=1_000_000, step=500),
        "Min %": st.column_config.NumberColumn("Min %", min_value=0.0, max_value=100.0, step=0.1),
        "Max %": st.column_config.NumberColumn("Max %", min_value=0.0, max_value=100.0, step=0.1),
    },
    disabled=[
        "Bahan",
        "Kategori",
        "Protein (%)",
        "EM (kkal/kg)",
        "Lemak (%)",
        "Serat (%)",
        "Ca (%)",
        "P (%)",
        "Lisin (%)",
        "Metionin (%)",
        "Catatan",
    ],
)
edited_df = sanitize_bahan_df(edited_df)

# Tentukan komposisi aktif
komposisi: Dict[str, float]
pesan_optimasi = ""
if mode == "Optimasi biaya otomatis":
    komposisi_opt, pesan_optimasi = solve_least_cost(edited_df, target, pakai_batas_asam_amino)
    if komposisi_opt is None:
        st.error(pesan_optimasi)
        st.info("Aplikasi menampilkan formula contoh sementara agar Anda tetap bisa melihat perhitungan.")
        komposisi = FORMULA_CONTOH[fase]
    else:
        st.success(pesan_optimasi)
        komposisi = komposisi_opt
elif mode == "Pakai formula contoh":
    komposisi = FORMULA_CONTOH[fase]
else:
    st.subheader("2) Atur komposisi manual")
    st.caption("Total tidak wajib tepat 100%; aplikasi akan menormalkan perhitungan ke 100%.")
    komposisi = manual_composition_editor(fase)

komposisi, peringatan_ketersediaan = sesuaikan_dengan_ketersediaan(komposisi, edited_df)
komposisi = normalisasi_komposisi(komposisi)
peringatan_batas = cek_pelanggaran_batas_manual(komposisi, edited_df) if mode != "Optimasi biaya otomatis" else []
for warning_text in peringatan_ketersediaan + peringatan_batas:
    st.warning(warning_text)
tabel_komposisi, ringkasan = hitung_ransum(edited_df, komposisi, jumlah_pakan)
evaluasi = tabel_evaluasi(ringkasan, target)

# Untuk pembanding: optimasi selalu dihitung bila mode bukan optimasi
komposisi_pembanding, _ = solve_least_cost(edited_df, target, pakai_batas_asam_amino)
if komposisi_pembanding is not None:
    _, ringkasan_opt = hitung_ransum(edited_df, komposisi_pembanding, jumlah_pakan)
else:
    ringkasan_opt = None

st.subheader("2) Hasil formulasi")
metric_cols = st.columns(5)
metric_cols[0].metric("Biaya total", rupiah(ringkasan["biaya_total"]))
metric_cols[1].metric("Biaya/kg pakan", rupiah(ringkasan["biaya_per_kg"]))
metric_cols[2].metric("Protein", f"{ringkasan['protein']:.2f}%")
metric_cols[3].metric("Energi", f"{ringkasan['energi']:.0f} kkal/kg")
if ringkasan_opt and ringkasan["biaya_total"] > 0:
    selisih = ringkasan["biaya_total"] - ringkasan_opt["biaya_total"]
    metric_cols[4].metric("Potensi hemat vs optimum", rupiah(max(0, selisih)))
else:
    metric_cols[4].metric("Potensi hemat vs optimum", "-")

if estimasi_kebutuhan > 0:
    biaya_estimasi_periode = ringkasan["biaya_per_kg"] * estimasi_kebutuhan
    st.info(
        f"Dengan konsumsi {konsumsi_g} g/ekor/hari untuk {jumlah_ayam} ekor selama {hari_pakai} hari, "
        f"estimasi kebutuhan pakan {estimasi_kebutuhan:,.1f} kg dan biaya pakan sekitar {rupiah(biaya_estimasi_periode)}."
        .replace(",", ".")
    )

main_tab, insight_tab, pemeliharaan_tab, data_tab = st.tabs(
    ["📌 Formula & nutrisi", "💰 Insight biaya", "🏡 Pemeliharaan", "📚 Data & referensi"]
)

with main_tab:
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("#### Komposisi dan kebutuhan bahan")
        st.dataframe(tabel_komposisi, use_container_width=True, hide_index=True)
        st.download_button(
            "Unduh formula CSV",
            data=csv_download(tabel_komposisi),
            file_name=f"formula_pakan_{fase.lower().replace(' ', '_').replace('/', '-')}.csv",
            mime="text/csv",
        )

        shopping = build_shopping_list(tabel_komposisi)
        with st.expander("Checklist belanja bahan"):
            st.dataframe(shopping, use_container_width=True, hide_index=True)
            st.download_button(
                "Unduh checklist belanja CSV",
                data=csv_download(shopping),
                file_name="checklist_belanja_pakan.csv",
                mime="text/csv",
            )

    with right:
        st.markdown("#### Evaluasi nutrisi")
        st.dataframe(evaluasi, use_container_width=True, hide_index=True)
        st.markdown("#### Saran tindakan")
        for item in buat_saran(ringkasan, target, edited_df):
            st.write(f"- {item}")

with insight_tab:
    st.markdown("### Cara mendapatkan nutrisi terbaik dengan biaya efisien")
    c1, c2, c3 = st.columns(3)
    with c1:
        html_info_card(
            "Prioritas 1: target utama",
            "Jangan mengejar harga termurah saja. Pastikan protein, energi, Ca, P, dan serat masuk batas target fase ayam.",
        )
    with c2:
        html_info_card(
            "Prioritas 2: bahan pembatas",
            "Dedak, bungkil kelapa, gaplek, dan tepung ikan berguna, tetapi harus dibatasi agar serat, mineral, dan palatabilitas tidak bermasalah.",
        )
    with c3:
        html_info_card(
            "Prioritas 3: uji kecil",
            "Formula murah wajib diuji bertahap. Catat konsumsi, bobot, kematian, dan biaya/kg bobot hidup.",
        )

    st.markdown("#### Efisiensi harga bahan")
    eff = biaya_efektif_bahan(edited_df)
    display_eff = eff.copy()
    display_eff["Harga Rp/kg"] = display_eff["Harga Rp/kg"].apply(rupiah)
    display_eff["Rp/kg protein"] = display_eff["Rp/kg protein"].apply(lambda x: "-" if pd.isna(x) else rupiah(x))
    display_eff["Rp/1000 kkal EM"] = display_eff["Rp/1000 kkal EM"].apply(lambda x: "-" if pd.isna(x) else rupiah(x))
    st.dataframe(display_eff, use_container_width=True, hide_index=True)

    st.markdown("#### Simulasi komponen biaya usaha")
    st.caption("Gunakan untuk melihat sensitivitas biaya. Pada banyak usaha unggas rakyat, pakan biasanya menjadi komponen biaya terbesar.")
    feed_share = st.slider("Perkiraan porsi biaya pakan dari total biaya usaha (%)", 50, 80, 65)
    biaya_total_usaha = ringkasan["biaya_total"] / (feed_share / 100.0) if feed_share > 0 else 0.0
    non_pakan = biaya_total_usaha - ringkasan["biaya_total"]
    b1, b2, b3 = st.columns(3)
    b1.metric("Biaya pakan", rupiah(ringkasan["biaya_total"]))
    b2.metric("Estimasi biaya non-pakan", rupiah(non_pakan))
    b3.metric("Estimasi total biaya", rupiah(biaya_total_usaha))

    st.markdown("#### Skenario daerah di Indonesia")
    st.write(
        "- **Daerah sentra padi:** dedak biasanya murah, tetapi batasi jika serat naik atau dedak berbau tengik."
    )
    st.write(
        "- **Daerah jagung murah:** jagung bisa menjadi tulang punggung energi; tetap perlu sumber protein agar pertumbuhan tidak turun."
    )
    st.write(
        "- **Daerah pesisir:** tepung ikan bisa ekonomis, tetapi cek bau, kadar garam, dan risiko pemalsuan."
    )
    st.write(
        "- **Daerah lembap:** risiko jamur/aflatoksin lebih tinggi; simpan bahan di tempat kering, gunakan palet, dan hindari stok terlalu lama."
    )

with pemeliharaan_tab:
    st.markdown("### Panduan pemeliharaan ayam kampung yang baik")
    st.markdown(
        """
        #### 1. Starter/DOC umur 1-30 hari
        - Siapkan brooder bersih, kering, hangat, dan bebas angin langsung.
        - Pakai alas koran/sekam kering; ganti bila basah atau kotor.
        - Lampu pemanas menyala penuh pada awal pemeliharaan, lalu dikurangi bertahap sesuai respons anak ayam.
        - Beri pakan 4-5 kali per hari agar pakan segar dan mudah diakses.
        - Air minum harus bersih. Pada tempat minum anak ayam, gunakan batu kecil/kerikil agar DOC tidak masuk ke air.

        #### 2. Grower/pembesaran
        - Pindahkan ke kandang grower setelah brooding selesai dan bulu mulai lengkap.
        - Gunakan kandang postal/litter atau boks bambu/kayu dengan ventilasi baik.
        - Kepadatan praktis: sekitar 10 ekor/m² untuk grower, disesuaikan suhu, ventilasi, dan bobot ayam.
        - Sediakan tenggeran, tempat pakan, tempat minum, dan litter kering.

        #### 3. Semi-intensif untuk menekan biaya
        - Jika lahan memungkinkan, gunakan pekarangan berpagar agar ayam mendapat hijauan, serangga, dan aktivitas alami.
        - Pakan buatan tetap diberikan 2-3 kali sehari; jangan hanya mengandalkan umbaran bila target panen ingin seragam.
        - Pantau predator, hujan, genangan, dan kontak dengan unggas liar.

        #### 4. Kesehatan dan biosekuriti
        - Pisahkan ayam sakit, bersihkan kandang rutin, dan batasi tamu/peralatan dari kandang lain.
        - Buat jadwal vaksinasi sesuai arahan penyuluh/dokter hewan setempat.
        - Catat kematian, konsumsi pakan, bobot mingguan, obat/vitamin, dan asal DOC.

        #### 5. Penyimpanan bahan pakan
        - Simpan di tempat kering, berventilasi, tidak menempel langsung ke lantai, dan jauh dari tikus.
        - Gunakan prinsip stok lama dipakai lebih dulu.
        - Tolak bahan yang berjamur, berbau apek/tengik, menggumpal, atau bercampur benda asing.
        """
    )

    st.markdown("#### Checklist harian kandang")
    checklist = pd.DataFrame(
        [
            {"Waktu": "Pagi", "Pekerjaan": "Cek ayam lemah/sakit, air minum, sisa pakan, suhu kandang, dan litter basah."},
            {"Waktu": "Siang", "Pekerjaan": "Tambah air, cek ventilasi/panas, buang pakan basah atau tercemar."},
            {"Waktu": "Sore", "Pekerjaan": "Pemberian pakan, cek kepadatan, amankan kandang dari predator."},
            {"Waktu": "Mingguan", "Pekerjaan": "Timbang sampel ayam, hitung FCR sederhana, bersihkan peralatan, dan evaluasi biaya."},
        ]
    )
    st.dataframe(checklist, use_container_width=True, hide_index=True)

with data_tab:
    st.markdown("### Target nutrisi fase terpilih")
    target_df = pd.DataFrame(
        [
            {"Parameter": "Protein kasar", "Batas": f"{target['protein_min']} - {target['protein_max']} %"},
            {"Parameter": "Energi metabolis", "Batas": f"{target['energi_min']} - {target['energi_max']} kkal/kg"},
            {"Parameter": "Kalsium", "Batas": f"{target['kalsium_min']} - {target['kalsium_max']} %"},
            {"Parameter": "Fosfor", "Batas": f"{target['fosfor_min']} - {target['fosfor_max']} %"},
            {"Parameter": "Lisin", "Batas": f"min. {target['lisin_min']} %"},
            {"Parameter": "Metionin", "Batas": f"min. {target['metionin_min']} %"},
            {"Parameter": "Serat kasar", "Batas": f"maks. {target['serat_max']} %"},
        ]
    )
    st.dataframe(target_df, use_container_width=True, hide_index=True)

    st.markdown("### Data nutrisi bahan")
    data_show = edited_df[
        [
            "Bahan",
            "Kategori",
            "Protein (%)",
            "EM (kkal/kg)",
            "Lemak (%)",
            "Serat (%)",
            "Ca (%)",
            "P (%)",
            "Lisin (%)",
            "Metionin (%)",
            "Catatan",
        ]
    ]
    st.dataframe(data_show, use_container_width=True, hide_index=True)

    with st.expander("Catatan sumber dan kehati-hatian"):
        st.markdown(
            """
            - Target fase KUB disederhanakan dari pedoman nutrisi ayam KUB: starter sekitar 20% protein dan 3000 kkal/kg EM, grower sekitar 17,5% protein dan 2800 kkal/kg EM, layer sekitar 16,5% protein dan 2800 kkal/kg EM.
            - Nilai nutrisi bahan pakan adalah pendekatan as-fed dari literatur bahan pakan umum. Kandungan aktual dapat berbeda antar daerah, musim, kadar air, dan pemasok.
            - Untuk skala komersial, gunakan uji laboratorium bahan, konsultasi penyuluh/nutrisionis, dan uji performa kandang.
            - Aplikasi ini membantu pengambilan keputusan, bukan pengganti diagnosis dokter hewan atau formulasi profesional untuk pabrik pakan.
            """
        )

st.divider()
st.caption(
    "Versi disempurnakan: optimasi biaya, insight harga bahan, evaluasi lisin-metionin, estimasi kebutuhan pakan, panduan pemeliharaan, dan checklist belanja."
)
