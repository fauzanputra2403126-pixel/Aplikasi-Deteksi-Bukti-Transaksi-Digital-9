import streamlit as st
from PIL import Image
import numpy as np
from modules.template_generator import generate_reference_template, PROVIDER_CONFIGS
from modules.converter import extract_roi_and_binarize, convert_template_to_vector, compute_ela_score
from modules.hamming import compute_forensic_hamming

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="VerifyID - Multi-Bank Transaction Forensics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS UI Gen-Z (Dark Theme & Glowing Badges)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 100%);
        color: #f3f4f6;
    }
    .status-badge-asli {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 14px;
        font-weight: 700;
        font-size: 26px;
        text-align: center;
        box-shadow: 0 4px 25px rgba(16, 185, 129, 0.45);
        margin-bottom: 24px;
    }
    .status-badge-palsu {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 14px;
        font-weight: 700;
        font-size: 26px;
        text-align: center;
        box-shadow: 0 4px 25px rgba(239, 68, 68, 0.45);
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header Utama
st.title("🛡️ VerifyID: Sistem Deteksi Transaksi Digital")
st.caption("Verifikasi Keaslian Resi m-Banking & e-Wallet Berbasis Hamming Distance & Weight Forensics")
st.markdown("---")

# 4. Sidebar Panel Parameter Transaksi
with st.sidebar:
    st.header("⚙️ Parameter Backend")
    
    st.subheader("1. Pilih Provider Transfer")
    provider_choice = st.selectbox(
        "Pilih m-Banking / e-Wallet:",
        list(PROVIDER_CONFIGS.keys())
    )
    
    st.subheader("2. Nominal Tagihan Sistem")
    nominal_tagihan_input = st.text_input("Nominal Tagihan Resmi (Rp)", value="Rp 500.000")
    
    st.subheader("3. Ambang Sensitivitas Deteksi")
    sim_threshold_input = st.slider(
        "Ambang Kemiripan Biner Minimum (%)",
        min_value=90.0,
        max_value=99.9,
        value=99.0,
        step=0.1,
        help="Semakin tinggi (misal 99.0%), semakin ketat sistem menolak resi manipulasi/editan."
    )
    
    st.markdown("---")
    st.info(f"**Provider:** {provider_choice}\n\n**Ambang Batas Presisi:** {sim_threshold_input}%")

# 5. Main Area Input 1 Gambar & Display Preview
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📤 Unggah 1 Bukti Transaksi")
    uploaded_file = st.file_uploader(
        f"Pilih berkas resi ({provider_choice}) - JPG/PNG", 
        type=['png', 'jpg', 'jpeg']
    )
    
    if uploaded_file:
        st.image(uploaded_file, caption=f"Gambar Bukti Uji ({provider_choice})", use_container_width=True)

with col_right:
    st.subheader("🔬 Ekstraksi Biner ROI Terpusat")
    if uploaded_file:
        # A. Citra Acuan Resmi Backend (x)
        template_img = generate_reference_template(
            nominal_str=nominal_tagihan_input,
            provider_name=provider_choice
        )
        vec_x, ar_x = convert_template_to_vector(template_img)
        
        # B. Ekstraksi ROI Auto-Centered Gambar Uji Diunggah (y)
        roi_img, vec_y, ar_y = extract_roi_and_binarize(uploaded_file)
        
        c1, c2 = st.columns(2)
        with c1:
            st.image(template_img, caption=f"Acuan Backend ({provider_choice})", use_container_width=True)
        with c2:
            st.image(roi_img, caption="ROI Auto-Centered (y)", use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        btn_analyze = st.button("🚀 Verifikasi Keaslian Resi", type="primary", use_container_width=True)

# 6. Output Hasil Verifikasi Forensik
if uploaded_file and 'btn_analyze' in locals() and btn_analyze:
    st.markdown("---")
    st.header("📋 Hasil Evaluasi Integritas Data")
    
    ela_score = compute_ela_score(uploaded_file)
    results = compute_forensic_hamming(vec_x, vec_y, ar_x, ar_y, ela_score, sim_threshold=sim_threshold_input)
    
    # Display Banner Status Utama
    if results['verdict'] == "VALID_ASLI":
        st.markdown(f'<div class="status-badge-asli">{results["title_output"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-badge-palsu">{results["title_output"]}</div>', unsafe_allow_html=True)
        
    st.write(f"**Keterangan Analisis:** {results['description']}")
    
    # Dashboard Metrik Angka
    st.markdown("### 📊 Dashboard Metrik Hamming Forensik")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Kemiripan Biner Piksel", f"{results['similarity_ratio']:.2f} %")
    m2.metric("Hamming Distance d(x,y)", f"{results['hamming_distance']:,} bit")
    m3.metric("Hamming Weight wt(e)", f"{results['hamming_weight']:,} bit")
    m4.metric("Total Bit Vektor (n)", f"{results['total_bits']:,} bit")
    
    # Verifikasi Teorema Matematika
    st.markdown("### 📐 Pembuktian Formulasi Teori Pengkodean")
    if results['is_verified']:
        st.success(f"✅ **Terbukti Mutlak:** Nilai $d(x,y)$ tepat ekuivalen dengan $wt(x \\oplus y)$ yaitu **{results['hamming_distance']:,} bit**.")
    else:
        st.error("⚠️ Ketidaksesuaian komputasi biner!")
elif not uploaded_file:
    st.info("👆 Silakan pilih provider di sidebar dan unggah 1 lembar gambar resi untuk verifikasi.")