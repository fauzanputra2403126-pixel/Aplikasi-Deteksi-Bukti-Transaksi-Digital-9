import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROVIDER_CONFIGS = {
    # M-Banking
    "Bank BCA": {"header": "BCA TRANSFER"},
    "Bank Mandiri": {"header": "LIVIN MANDIRI"},
    "Bank BRI": {"header": "BRIMO BRI"},
    "Bank BNI": {"header": "BNI MOBILE"},
    "SeaBank": {"header": "SEABANK"},
    
    # E-Wallet
    "ShopeePay": {"header": "SHOPEEPAY"},
    "GoPay": {"header": "GOPAY"},
    "DANA": {"header": "DANA"},
    "OVO": {"header": "OVO"}
}

def clean_nominal_string(raw_str):
    """Membersihkan string nominal menjadi digit angka murni (misal: 'Rp 500.000' -> '500000')"""
    cleaned = ''.join(filter(str.isdigit, str(raw_str)))
    return cleaned if cleaned else "0"

def generate_reference_template(nominal_str="500000", provider_name="SeaBank", width=280, height=80):
    """
    Menghasilkan Citra Acuan Resmi (x) yang bersih dari noise, 
    di-center tepat di tengah kanvas ROI (280x80 px).
    """
    cleaned_num = clean_nominal_string(nominal_str)
    formatted_display = f"Rp {int(cleaned_num):,}".replace(",", ".") if cleaned_num.isdigit() else nominal_str
    
    # Kanvas Putih Murni (255)
    img = Image.new('L', (width, height), color=255)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
        
    bbox = draw.textbbox((0, 0), formatted_display, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    x_pos = max((width - tw) // 2, 5)
    y_pos = max((height - th) // 2, 5)
    
    # Teks Hitam Murni (0)
    draw.text((x_pos, y_pos), formatted_display, fill=0, font=font)
    return img