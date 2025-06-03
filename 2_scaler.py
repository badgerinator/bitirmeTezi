"""
0-100 Arası Ölçeklendirme Pipeline'ı
===================================

Bu betik, processed_candidates_anonymized.xlsx dosyasını okuyup
sayısal değerleri 0-100 aralığında normalize eder ve yeni bir dosya olarak kaydeder.
"""

# Kütüphaneler
import pandas as pd

# ---------------------- Dosya Yükleme ----------------------

# Girdi dosyasını oku
df = pd.read_excel("./outputs/processed_candidates_anonymized.xlsx")

# ---------------------- Hangi Sütunlar Scale Edilecek? ----------------------

# 'Aday ID' hariç diğer tüm sayısal sütunları scale edeceğiz
# Örneğin mevcut kolonlar:
# ['Aday ID', 'Toplam Deneyim (gün)', 'Yabancı Dil Skoru', 'Eğitim Seviyesi Skoru',
#  'Basic Computer Skills Skoru', 'Katıldığınız Kurs/Seminer/Sertifika Sayısı', 'Sosyal Aktivite Skoru (0-100)']

# Aday ID harici kolonları seç
columns_to_scale = [col for col in df.columns if col != "ID" and col != "Deneyim Seviyesi (Kategori)"]

# ---------------------- Ölçeklendirme (Min-Max Scaling) ----------------------

# Her kolon için 0-100 scale işlemi
for col in columns_to_scale:
    min_val = df[col].min()
    max_val = df[col].max()
    
    # Eğer min == max ise tüm değerleri 0 olarak bırakıyoruz (tek tip veri varsa bölme hatasını önlemek için)
    if min_val == max_val:
        df[col + " (Scaled)"] = 0
    else:
        df[col + " (Scaled)"] = ((df[col] - min_val) / (max_val - min_val)) * 100

# ---------------------- Sonuçları Kaydetme ----------------------

# Yeni dosya adı
output_path = "./outputs/processed_candidates_anonymized_scaled.xlsx"

# Kaydet
df.to_excel(output_path, index=False)

# Bilgilendirme
print(f"Scale edilmiş dosya başarıyla kaydedildi: {output_path}")
