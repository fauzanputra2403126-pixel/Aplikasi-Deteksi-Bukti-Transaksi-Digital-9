import numpy as np
from PIL import Image, ImageOps, ImageChops

def extract_roi_and_binarize(uploaded_image, target_size=(280, 80)):
    """
    Mengambil 1 gambar upload (y), melakukan isolasi ROI teks nominal,
    penyetelan posisi di tengah (centering), menghitung Rasio Aspek (Aspect Ratio),
    binarisasi (0 & 1), dan meratakannya menjadi Vektor Biner 1D.
    """
    # 1. Buka Gambar Uji & Convert Grayscale + Autocontrast
    raw_img = Image.open(uploaded_image).convert('L')
    contrast_img = ImageOps.autocontrast(raw_img)
    
    # 2. Binarisasi Adaptive Thresholding
    np_img = np.array(contrast_img)
    mean_val = np.mean(np_img)
    threshold = int(mean_val * 0.85)
    
    binary_np = np.where(np_img < threshold, 0, 255).astype(np.uint8)
    binary_pil = Image.fromarray(binary_np)
    
    # 3. Cari Bounding Box Teks Nominal & Crop
    inverted = ImageOps.invert(binary_pil)
    bbox = inverted.getbbox()
    
    if bbox:
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        aspect_ratio = w / float(max(h, 1))
        cropped_text = binary_pil.crop(bbox)
    else:
        aspect_ratio = 1.0
        cropped_text = binary_pil
        
    # 4. Fitting & Centering ke Kanvas Target (280x80 px)
    canvas = Image.new('L', target_size, color=255)
    cw, ch = cropped_text.size
    tw, th = target_size
    
    scale = min((tw - 20) / max(cw, 1), (th - 20) / max(ch, 1), 1.0)
    new_w = max(int(cw * scale), 1)
    new_h = max(int(ch * scale), 1)
    
    resized_text = cropped_text.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    paste_x = (tw - new_w) // 2
    paste_y = (th - new_h) // 2
    canvas.paste(resized_text, (paste_x, paste_y))
    
    # 5. Konversi Kanvas ROI ke Vektor Biner (Bit 1 = Teks, Bit 0 = Latar)
    np_canvas = np.array(canvas)
    binary_matrix = np.where(np_canvas < 128, 1, 0).astype(np.uint8)
    binary_vector = binary_matrix.flatten()
    
    return canvas, binary_vector, aspect_ratio

def convert_template_to_vector(template_pil_image, target_size=(280, 80)):
    """Mengonversi Gambar Acuan Backend (x) ke Vektor Biner 1D dan Rasio Aspek."""
    canvas, vec, aspect_ratio = extract_roi_and_binarize(template_pil_image, target_size=target_size)
    return vec, aspect_ratio

def compute_ela_score(uploaded_image, quality=90):
    """Menghitung Skor Error Level Analysis (ELA) untuk deteksi editan foto."""
    import io
    img = Image.open(uploaded_image).convert('RGB')
    buffer = io.BytesIO()
    img.save(buffer, 'JPEG', quality=quality)
    buffer.seek(0)
    resaved = Image.open(buffer)
    
    diff = ImageChops.difference(img, resaved)
    np_diff = np.array(diff)
    return float(np.mean(np_diff))