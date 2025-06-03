"""
AHP Ağırlık Hesaplama + Birleşik Ağırlık (CR ≤ 0.15 filtreli) + CI/CR/Lambda_max
===============================================================================

Çıktılar:
- Uzman_Agirliklari
- Birlesik_Agirlik (sadece CR ≤ 0.15 uzmanlardan)
- Consistency_Results
"""

import pandas as pd
import numpy as np

# RI değerleri
RI_dict = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49
}

# Dosya yolu
input_path = "./data_sources/ahp_expert_filled.xlsx"

# Dosya oku
wb = pd.ExcelFile(input_path)
sheet_names = wb.sheet_names
print(f"Bulunan uzmanlar: {sheet_names}")

# Sonuçlar
expert_weights = {}
expert_lambda_max = {}
expert_ci = {}
expert_cr = {}

# Her sheet için hesaplama
for sheet in sheet_names:
    print(f"\n---- {sheet} ----")
    
    df = wb.parse(sheet_name=sheet, index_col=0)
    matrix = df.astype(float).values
    n = matrix.shape[0]
    
    column_sums = matrix.sum(axis=0)
    normalized_matrix = matrix / column_sums
    
    weights = normalized_matrix.mean(axis=1)
    
    lambda_max = np.dot(column_sums, weights)
    
    CI = (lambda_max - n) / (n - 1)
    
    RI = RI_dict[n]
    CR = CI / RI if RI != 0 else 0.0
    
    # Kayıt
    expert_weights[sheet] = weights
    expert_lambda_max[sheet] = lambda_max
    expert_ci[sheet] = CI
    expert_cr[sheet] = CR
    
    # Ekrana yaz
    print("Kriter Ağırlıkları:")
    for crit, w in zip(df.columns, weights):
        print(f" - {crit}: {w:.4f}")
    print(f"Lambda max: {lambda_max:.4f}")
    print(f"CI: {CI:.4f}")
    print(f"CR: {CR:.4f} → {'TUTARLI' if CR < 0.1 else ('KABUL EDILEBILIR' if CR <= 0.15 else 'TUTARSIZ - HARIC')}")

# --------------- CR ≤ 0.15 Filtreleme ----------------

valid_experts = [sheet for sheet in sheet_names if expert_cr[sheet] <= 0.15]
print(f"\n==== Konsolideye dahil edilecek uzmanlar (CR ≤ 0.15): {valid_experts}")

# --------------- Birleşik Ağırlık Hesaplama (Geometric Mean) ---------------

if len(valid_experts) == 0:
    print("\nUYARI: Hiçbir uzman CR ≤ 0.15 değil! Konsolide ağırlık hesaplanamayacak.")
    combined_weights = np.full(n, np.nan)
    lambda_max_combined = np.nan
    CI_combined = np.nan
    CR_combined = np.nan
else:
    print("\n==== Birleşik Ağırlık (Geometric Mean) Hesaplanıyor ====")

    summary_df = pd.DataFrame({sheet: expert_weights[sheet] for sheet in sheet_names},
                              index=df.columns)

    valid_summary_df = summary_df[valid_experts]

    combined_weights = np.exp(np.log(valid_summary_df).mean(axis=1))
    combined_weights = combined_weights / combined_weights.sum()

    # Konsolide Lambda_max hesapla
    matrix_list = []
    for sheet in valid_experts:
        df = wb.parse(sheet_name=sheet, index_col=0)
        matrix = df.astype(float).values
        matrix_list.append(matrix)

    matrix_array = np.array(matrix_list)
    geo_mean_matrix = np.exp(np.mean(np.log(matrix_array), axis=0))

    column_sums_combined = geo_mean_matrix.sum(axis=0)
    lambda_max_combined = np.dot(column_sums_combined, combined_weights)

    CI_combined = (lambda_max_combined - n) / (n - 1)
    RI_combined = RI_dict[n]
    CR_combined = CI_combined / RI_combined if RI_combined != 0 else 0.0

    # Ekrana yaz
    print("\nBirleşik Ağırlıklar:")
    for crit, w in zip(valid_summary_df.index, combined_weights):
        print(f" - {crit}: {w:.4f}")

    print(f"\nBirleşik Lambda max: {lambda_max_combined:.4f}")
    print(f"Birleşik CI: {CI_combined:.4f}")
    print(f"Birleşik CR: {CR_combined:.4f} → {'TUTARLI' if CR_combined < 0.1 else ('KABUL EDILEBILIR' if CR_combined <= 0.15 else 'TUTARSIZ')}")

# --------------- Sonuçları Kaydetme ----------------

output_path = "./outputs/ahp_weights_summary.xlsx"

with pd.ExcelWriter(output_path) as writer:
    # Sheet 1 → Uzman ağırlıkları
    summary_df = pd.DataFrame({sheet: expert_weights[sheet] for sheet in sheet_names},
                              index=df.columns)
    summary_df.to_excel(writer, sheet_name="Uzman_Agirliklari")
    
    # Sheet 2 → Birleşik ağırlık (sadece CR ≤ 0.15 uzmanlardan)
    combined_df = pd.DataFrame({"Birlesik_Agirlik": combined_weights}, index=df.columns)
    combined_df.to_excel(writer, sheet_name="Birlesik_Agirlik")
    
    # Sheet 3 → Consistency sonuçları
    consistency_data = {
        "Lambda_max": {**expert_lambda_max, "Birlesik": lambda_max_combined},
        "CI": {**expert_ci, "Birlesik": CI_combined},
        "CR": {**expert_cr, "Birlesik": CR_combined}
    }
    consistency_df = pd.DataFrame(consistency_data)
    consistency_df.to_excel(writer, sheet_name="Consistency_Results")

print(f"\nAHP hesaplamaları ve tüm sonuçlar başarıyla kaydedildi: {output_path}")
