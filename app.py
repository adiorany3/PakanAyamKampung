import streamlit as st
import pandas as pd

st.set_page_config(page_title="Formulasi Ransum Ayam Kampung", layout="wide")
st.title("🛠️ Formulasi Ransum Ayam Kampung")
st.markdown("**Aplikasi penghitung komposisi nutrisi ransum ayam kampung**")

# Data Bahan Pakan
ingredients_data = {
    "Jagung": {"protein": 8.5, "em": 3350, "lemak": 3.8, "serat": 2.5, "ca": 0.02, "p": 0.3},
    "Dedak Padi / Bekatul": {"protein": 12.0, "em": 2200, "lemak": 13.0, "serat": 8.0, "ca": 0.1, "p": 1.2},
    "Bungkil Kedelai": {"protein": 45.0, "em": 2400, "lemak": 5.0, "serat": 6.0, "ca": 0.3, "p": 0.65},
    "Tepung Ikan": {"protein": 55.0, "em": 2800, "lemak": 8.0, "serat": 1.0, "ca": 6.0, "p": 3.0},
    "Bungkil Kelapa": {"protein": 20.0, "em": 2000, "lemak": 8.0, "serat": 12.0, "ca": 0.2, "p": 0.6},
    "Tepung Tulang": {"protein": 25.0, "em": 1500, "lemak": 10.0, "serat": 2.0, "ca": 30.0, "p": 15.0},
    "Garam": {"protein": 0.0, "em": 0, "lemak": 0.0, "serat": 0.0, "ca": 0.0, "p": 0.0},
    "Premix Vitamin-Mineral": {"protein": 0.0, "em": 0, "lemak": 0.0, "serat": 0.0, "ca": 0.0, "p": 0.0},
}

df_ingredients = pd.DataFrame.from_dict(ingredients_data, orient='index')

# Kebutuhan Nutrisi
requirements = {
    "Starter (0-4 minggu)": {"protein": 19.0, "em": 2850, "ca": 1.0, "p": 0.45},
    "Grower (5-10 minggu)": {"protein": 17.0, "em": 2750, "ca": 0.9, "p": 0.45},
    "Finisher / Layer": {"protein": 16.0, "em": 2700, "ca": 3.5, "p": 0.35},
}

# Sidebar
st.sidebar.header("Pengaturan Ransum")
phase = st.sidebar.selectbox("Fase Ayam", list(requirements.keys()))
target = requirements[phase]
total_percentage = st.sidebar.slider("Total Persentase Bahan (%)", 95, 100, 100)

st.sidebar.markdown("### Komposisi Bahan (%)")
selected_ingredients = {}
for ing in ingredients_data.keys():
    pct = st.sidebar.slider(f"{ing}", 0, 50, 0, step=1)
    if pct > 0:
        selected_ingredients[ing] = pct

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Komposisi Ransum")
    if selected_ingredients:
        total_selected = sum(selected_ingredients.values())
        st.info(f"Total persentase: **{total_selected}%**")
        
        if abs(total_selected - total_percentage) > 5:
            st.warning("Total persentase sebaiknya mendekati 100%.")
        
        if total_selected > 0:
            data = []
            for ing, pct in selected_ingredients.items():
                norm_pct = (pct / total_selected) * total_percentage if total_selected != total_percentage else pct
                data.append({"Bahan": ing, "Persentase (%)": round(norm_pct, 2)})
            
            df_comp = pd.DataFrame(data)
            st.dataframe(df_comp, use_container_width=True)

with col2:
    st.subheader("Kebutuhan Nutrisi")
    st.table(pd.DataFrame([target], index=["Target"]))

# Perhitungan
if selected_ingredients:
    st.subheader("Hasil Analisis Nutrisi")
    total_protein = total_em = total_lemak = total_serat = total_ca = total_p = 0
    results = []
    
    for ing, pct in selected_ingredients.items():
        norm_pct = (pct / total_selected) * total_percentage if total_selected != total_percentage else pct
        info = ingredients_data[ing]
        
        contrib_p = (norm_pct / 100) * info["protein"]
        contrib_em = (norm_pct / 100) * info["em"]
        contrib_l = (norm_pct / 100) * info["lemak"]
        contrib_s = (norm_pct / 100) * info["serat"]
        contrib_ca = (norm_pct / 100) * info["ca"]
        contrib_ph = (norm_pct / 100) * info["p"]
        
        total_protein += contrib_p
        total_em += contrib_em
        total_lemak += contrib_l
        total_serat += contrib_s
        total_ca += contrib_ca
        total_p += contrib_ph
        
        results.append({
            "Bahan": ing,
            "Persentase (%)": round(norm_pct, 2),
            "Protein (%)": round(contrib_p, 2),
            "EM (kkal/kg)": round(contrib_em, 0),
        })
    
    st.dataframe(pd.DataFrame(results), use_container_width=True)
    
    # Ringkasan
    summary = pd.DataFrame({
        "Nutrien": ["Protein Kasar (%)", "Energi Metabolis (kkal/kg)", "Lemak Kasar (%)", 
                   "Serat Kasar (%)", "Kalsium (%)", "Fosfor (%)"],
        "Kandungan": [round(total_protein,2), round(total_em,0), round(total_lemak,2),
                     round(total_serat,2), round(total_ca,2), round(total_p,2)],
        "Target": [target["protein"], target["em"], "-", "-", target["ca"], target["p"]]
    })
    st.table(summary)

st.markdown("---")
st.caption("**Catatan:** Nilai adalah pendekatan. Lakukan analisis laboratorium untuk akurasi tinggi.")