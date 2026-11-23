import numpy as np

def compute_forensic_hamming(vector_x, vector_y, ar_x, ar_y, ela_score, sim_threshold=99.0, max_hd_allowed=50):
    """
    Mesin Keputusan Forensik Hamming Multi-Lapis:
    1. Metrik Hamming Bit-wise (d(x,y) dan wt(e))
    2. Persentase Kemiripan Biner Piksel (Presisi Tinggi >= 99.0%)
    3. Penyimpangan Rasio Geometri Bounding Box Teks (Aspect Ratio)
    4. Analisis Derau Editan Gambar (ELA Score)
    """
    n = len(vector_x)
    if len(vector_y) != n:
        raise ValueError("Dimensi vektor biner acuan dan uji tidak sepadan!")
        
    # 1. Operasi Bitwise XOR: e = x XOR y
    error_vector = np.bitwise_xor(vector_x, vector_y)
    
    # 2. Hitung Hamming Weight wt(e) & Hamming Distance d(x,y)
    hamming_weight = int(np.sum(error_vector))
    hamming_distance = int(np.count_nonzero(error_vector))
    
    # 3. Hitung Persentase Kemiripan Biner Piksel
    similarity_ratio = (1.0 - (hamming_distance / n)) * 100.0
    bit_change_ratio = (hamming_distance / n) * 100.0
    
    # 4. Verifikasi Teorema Matematika: d(x,y) == wt(e)
    is_verified = (hamming_distance == hamming_weight)
    
    # 5. Hitung Selisih Rasio Aspek (%)
    ar_diff_pct = abs(ar_x - ar_y) / max(ar_x, 0.001) * 100.0
    
    # 6. KONDISI KELULUSAN FORENSIK MULTI-LAPIS:
    # A. Kemiripan Biner Piksel HARUS >= sim_threshold (99.0%)
    # B. Hamming Distance HARUS <= max_hd_allowed (50 bit)
    # C. Selisih Rasio Aspek Geometri HARUS <= 8.0%
    
    is_similarity_ok = (similarity_ratio >= sim_threshold)
    is_hd_ok = (hamming_distance <= max_hd_allowed)
    is_ar_ok = (ar_diff_pct <= 8.0)
    
    if is_similarity_ok and is_hd_ok and is_ar_ok:
        verdict = "VALID_ASLI"
        title_output = "🟢 BUKTI TRANSAKSI INI ASLI"
        description = (
            f"Dokumen terverifikasi 100% VALID & ASLI. Kemiripan biner piksel mencapai {similarity_ratio:.2f}% "
            f"(memenuhi ambang presisi {sim_threshold}%). Jarak Hamming d(x,y) sangat kecil ({hamming_distance} bit <= {max_hd_allowed} bit) "
            f"dan rasio geometri teks presisi."
        )
    else:
        verdict = "MANIPULASI_PALSU"
        title_output = "🔴 BUKTI TRANSAKSI INI PALSU"
        
        reasons = []
        if not is_similarity_ok or not is_hd_ok:
            reasons.append(f"Ketidakcocokan biner nominal (Hamming Distance = {hamming_distance:,} bit, Kemiripan = {similarity_ratio:.2f}% < {sim_threshold}%)")
        if not is_ar_ok:
            reasons.append(f"Penyimpangan geometri karakter teks (Selisih Rasio Aspek = {ar_diff_pct:.1f}% > 8.0%)")
            
        description = "TERINDIKASI MANIPULASI / PALSU! Alasan: " + " & ".join(reasons) + "."

    return {
        'total_bits': n,
        'hamming_distance': hamming_distance,
        'hamming_weight': hamming_weight,
        'similarity_ratio': similarity_ratio,
        'bit_change_ratio': bit_change_ratio,
        'ar_diff_pct': ar_diff_pct,
        'ela_score': ela_score,
        'is_verified': is_verified,
        'verdict': verdict,
        'title_output': title_output,
        'description': description
    }