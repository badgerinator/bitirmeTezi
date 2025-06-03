"""
4. Temiz Pipeline - Aday Profil Skorlama
========================================

Bu betik, aday havuzu verisini işleyerek aşağıdaki skorları üretir:
- Deneyim Süresi (gün)
- Deneyim Seviyesi (Kategori)
- Yabancı Dil Skoru
- Eğitim Seviyesi Skoru
- Bilgisayar Yetkinliği Skoru
- Sertifika Sayısı + Sertifika Skoru
- Sosyal Aktivite Skoru (0-100)

SOLID prensiplerine uygun olarak modüler ve sürdürülebilir şekilde tasarlanmıştır.
Her adım açık şekilde yorumlanmıştır.
"""

# Kütüphane yüklemeleri
import pandas as pd
import re
import numpy as np
from scipy.interpolate import interp1d
from sentence_transformers import SentenceTransformer

# ---------------------- Referans Veri ve Sözlükler ----------------------

# Yabancı dil seviye dönüşümü
lang_level_dict = { 0: "Zayıf", 33: "Orta", 66: "İyi", 99: "Çok iyi" }
level_to_score = {v: k for k, v in lang_level_dict.items()}
lang_weight_dict = { "Konuşma": 40, "Yazma": 30, "Okuma": 30 }

# Eğitim seviyesi dönüşümü
education_level_dict = { "Lise": 0, "Lisans/Ön Lisans": 1, "Yüksek Lisans": 2, "Doktora": 3 }

# Bilgisayar yetkinliği interpolasyon referansı
software_reference_data = {
    "x": [0,1,2,3,4,5,7,9,12,15,25,30],
    "y": [0,15,40,60,65,70,75,80,85,90,95,100]
}
software_reference_df = pd.DataFrame(software_reference_data)

# Sertifika skoru interpolasyon referansı
certificate_reference_data = {
    "x": [0, 1, 2, 3, 5, 7, 10, 15, 20],
    "y": [0, 5, 10, 25, 50, 70, 90, 95, 100]
}
certificate_reference_df = pd.DataFrame(certificate_reference_data)

# Sosyal aktivite skoru için embedding modeli
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# ---------------------- Veri Yükleme ve Hazırlık ----------------------

# Aday verisini yükle
df = pd.read_excel("./data_sources/aday_havuzu.xlsx")

# Sütun adlarını temizle
df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()

# ---------------------- Özellik (Feature) Fonksiyonları ----------------------

# 1️⃣ Deneyim Süresi (gün cinsinden)
def handle_experience(row):
    toplam_gun = 0
    for i in range(1, 5):
        start = pd.to_datetime(row.get(f"{i}. Kuruma Başlangıç Tarihi"), errors='coerce', dayfirst=True)
        end = pd.to_datetime(row.get(f"{i}. Kurumdan Çıkış Tarihi"), errors='coerce', dayfirst=True)
        if pd.notnull(start) and pd.notnull(end):
            sure = (end - start).days
            if sure > 0:
                toplam_gun += sure
    return toplam_gun

# 2️⃣ Deneyim Seviyesi (Kategori)
def categorize_experience_days(row):
    days = row["Toplam Deneyim (gün)"]
    if days < 180:
        return 0
    elif 180 <= days < 365:
        return 1
    elif 365 <= days < 1095:
        return 2
    else:  # 1095 gün ve üzeri
        return 4

# 3️⃣ Yabancı Dil Skoru
def calculate_language_score(row):
    toplam_skor = 0
    for beceri, agirlik in lang_weight_dict.items():
        seviye = row.get(beceri, "")
        seviye_skor = level_to_score.get(seviye, 0)
        toplam_skor += (seviye_skor * agirlik) / 100
    return toplam_skor

# 4️⃣ Sertifika Sayısı
def count_certificates(row):
    metin = str(row.get("Katıldığınız Kurs/Seminer/Sertifika/ Ödül ve Takdirler", "")).strip()
    if metin == "":
        return 0
    return len(metin.split("\n"))

# 5️⃣ Sertifika Skoru (Interpolasyon)
def certificate_score_with_reference(row, reference_df):
    cert_count = count_certificates(row)
    interpolator = interp1d(reference_df["x"].values, reference_df["y"].values, kind='linear', fill_value='extrapolate')
    score = interpolator(cert_count)
    return min(score, 100)

# 6️⃣ Eğitim Seviyesi Skoru
def get_education_level(row):
    seviye = row.get("Eğitim Durumunuz", "")
    return education_level_dict.get(seviye, 0)

# 7️⃣ Bilgisayar Yetkinliği Sayısı
def count_software_skills(row):
    metin = str(row.get("Yazılım Bilginiz", "")).strip()
    if metin == "":
        return 0
    metin = re.sub(r'[\-\n,;]', ';', metin)
    metin = re.sub(r'\s{2,}', ' ', metin)
    ogeler = [item.strip() for item in metin.split(';') if item.strip() != '']
    return len(ogeler)

# 8️⃣ Bilgisayar Yetkinliği Skoru
def software_skill_score_with_reference(row, reference_df):
    yetkinlik_sayisi = count_software_skills(row)
    interpolator = interp1d(reference_df["x"].values, reference_df["y"].values, kind='linear', fill_value='extrapolate')
    score = interpolator(yetkinlik_sayisi)
    return min(score, 100)

# 9️⃣ Sosyal Aktivite Skoru (ileri seviye)
def calculate_social_activity_score_advanced(row):
    hobiler = str(row.get("Hobileriniz", "")).strip()
    dernekler = str(row.get("Üye olduğunuz dernek ve kuruluşlar", "")).strip()
    
    if hobiler == "" and dernekler == "":
        return 0
    
    hobiler_clean = re.sub(r'[\-\n,;]', ';', hobiler)
    hobiler_list = [item.strip() for item in hobiler_clean.split(';') if item.strip() != '']
    hobiler_sayisi = len(hobiler_list)
    
    dernek_clean = re.sub(r'[\-\n,;]', ';', dernekler)
    dernek_list = [item.strip() for item in dernek_clean.split(';') if item.strip() != '']
    dernek_sayisi = len(dernek_list)
    
    full_text = hobiler + " " + dernekler
    kelime_sayisi = len(full_text.split())
    embedding_norm = np.linalg.norm(embedding_model.encode(full_text))
    
    hobi_skor = min(hobiler_sayisi * 20, 60)
    dernek_skor = min(dernek_sayisi * 25, 50)
    zenginlik_skor = min((embedding_norm / 10 * 50) + (kelime_sayisi / 50 * 25), 50)
    
    ham_skor = hobi_skor + dernek_skor + zenginlik_skor
    normalize_skor = min(ham_skor / 150 * 100, 100)
    
    return normalize_skor

# ---------------------- Pipeline Uygulama ----------------------

df["Toplam Deneyim (gün)"] = df.apply(handle_experience, axis=1)
df["Deneyim Seviyesi (Kategori)"] = df.apply(categorize_experience_days, axis=1)
df["Yabancı Dil Skoru"] = df.apply(calculate_language_score, axis=1)
df["Katıldığınız Kurs/Seminer/Sertifika Sayısı"] = df.apply(count_certificates, axis=1)
df["Katıldığınız Kurs/Seminer/Sertifika Skoru"] = df.apply(certificate_score_with_reference, axis=1, reference_df=certificate_reference_df)
df["Eğitim Seviyesi Skoru"] = df.apply(get_education_level, axis=1)
df["Yazılım Bilgisi Sayısı"] = df.apply(count_software_skills, axis=1)
df["Basic Computer Skills Skoru"] = df.apply(software_skill_score_with_reference, axis=1, reference_df=software_reference_df)
df["Sosyal Aktivite Skoru"] = df.apply(calculate_social_activity_score_advanced, axis=1)

min_sa = df["Sosyal Aktivite Skoru"].min()
max_sa = df["Sosyal Aktivite Skoru"].max()
df["Sosyal Aktivite Skoru (0-100)"] = ((df["Sosyal Aktivite Skoru"] - min_sa) / (max_sa - min_sa)) * 100

# ---------------------- Anonim Çıktı Kaydetme ----------------------

anon_columns = [
    "ID",      
    "Deneyim Seviyesi (Kategori)",          
    "Yabancı Dil Skoru",
    "Eğitim Seviyesi Skoru",
    "Basic Computer Skills Skoru",
    "Katıldığınız Kurs/Seminer/Sertifika Skoru",
    "Sosyal Aktivite Skoru (0-100)"
]

df_anon = df[anon_columns].copy()
df_anon.to_excel("./outputs/processed_candidates_anonymized.xlsx", index=False)

df.to_excel("./outputs/processed_candidates_full.xlsx", index=False)

print("Pipeline başarıyla tamamlandı ve çıktılar kaydedildi.")
