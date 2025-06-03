"""
AHP + TOPSIS + ELECTRE Pipeline
===============================

Girdi:
- ./outputs/ahp_weights_summary.xlsx (Birlesik_Agirlik)
- ./outputs/processed_candidates_anonymized_scaled.xlsx

Çıktılar:
- TOPSIS_Ranking.xlsx
- ELECTRE_Results.xlsx
"""

import pandas as pd
import numpy as np

# --------------- Parametreler ----------------

# Dosya yolları
weights_path = "./outputs/ahp_weights_summary.xlsx"
candidates_path = "./outputs/processed_candidates_anonymized_scaled.xlsx"

# ELECTRE threshold parametreleri
# Concordance threshold → default = 0.65 (literatürde 0.6-0.7 arası yaygın)
C_threshold = 0.65
# Discordance threshold → default = 0.35
D_threshold = 0.35

# --------------- Ağırlıkları Yükle ----------------

# Birleşik ağırlıkları oku
weights_df = pd.read_excel(weights_path, sheet_name="Birlesik_Agirlik", index_col=0)
weights = weights_df["Birlesik_Agirlik"].values
criteria_names = weights_df.index.tolist()

print(f"Kriterler: {criteria_names}")
print(f"Ağırlıklar: {weights}")

# --------------- Aday Verisini Yükle ----------------

candidates_df = pd.read_excel(candidates_path)
candidates_df.set_index("ID", inplace=True)

# Kriter matrisini çıkar
criteria_matrix = candidates_df[criteria_names].values

print(f"\nAday sayısı: {criteria_matrix.shape[0]}")
print(f"Kriter sayısı: {criteria_matrix.shape[1]}")

# --------------- TOPSIS Hesaplama ----------------

# Normalize et (vektör normu ile)
norm = np.linalg.norm(criteria_matrix, axis=0)
normalized_matrix = criteria_matrix / norm

# Ağırlıklı normalize matris
weighted_matrix = normalized_matrix * weights

# Ideal ve anti-ideal çözümler
ideal_solution = np.max(weighted_matrix, axis=0)
anti_ideal_solution = np.min(weighted_matrix, axis=0)

# Mesafe hesapla
distance_to_ideal = np.linalg.norm(weighted_matrix - ideal_solution, axis=1)
distance_to_anti_ideal = np.linalg.norm(weighted_matrix - anti_ideal_solution, axis=1)

# TOPSIS skorları
topsis_scores = distance_to_anti_ideal / (distance_to_ideal + distance_to_anti_ideal)

# Sıralama (yüksek skor daha iyi)
topsis_ranking = np.argsort(topsis_scores)[::-1] + 1

# TOPSIS sonuç dataframe
topsis_df = candidates_df.copy()
topsis_df["TOPSIS_Score"] = topsis_scores
topsis_df["TOPSIS_Rank"] = topsis_ranking

# --------------- ELECTRE Hesaplama ----------------

n_candidates = criteria_matrix.shape[0]
n_criteria = criteria_matrix.shape[1]

# Concordance ve Discordance matrisleri
C_matrix = np.zeros((n_candidates, n_candidates))
D_matrix = np.zeros((n_candidates, n_candidates))

for i in range(n_candidates):
    for j in range(n_candidates):
        if i == j:
            continue
        
        # Cij: hangi kriterlerde i aday j'den daha iyi?
        concordance_indices = criteria_matrix[i, :] >= criteria_matrix[j, :]
        Cij = np.sum(weights[concordance_indices])
        C_matrix[i, j] = Cij
        
        # Dij: hangi kriterlerde i aday j'den çok kötü?
        differences = np.abs(criteria_matrix[i, :] - criteria_matrix[j, :])
        max_diff = np.max(differences)
        if max_diff == 0:
            D_matrix[i, j] = 0
        else:
            Dij = np.max((criteria_matrix[j, :] - criteria_matrix[i, :]) / max_diff)
            D_matrix[i, j] = Dij

# Outranking (dominance) matrisi
outranking_matrix = np.zeros((n_candidates, n_candidates))

for i in range(n_candidates):
    for j in range(n_candidates):
        if i == j:
            continue
        if C_matrix[i, j] >= C_threshold and D_matrix[i, j] <= D_threshold:
            outranking_matrix[i, j] = 1  # i dominates j
        else:
            outranking_matrix[i, j] = 0

# Dominance score → kaç adaya üstün geliyor?
dominance_scores = np.sum(outranking_matrix, axis=1)

# ELECTRE sonuç dataframe
electre_df = pd.DataFrame({
    "ID": candidates_df.index,
    "ELECTRE_Dominance_Score": dominance_scores
}).set_index("ID")

# Sıralama
electre_df["ELECTRE_Rank"] = electre_df["ELECTRE_Dominance_Score"].rank(ascending=False, method='min').astype(int)

# --------------- Sonuçları Kaydet ----------------

# TOPSIS
topsis_df_out = topsis_df[["TOPSIS_Score", "TOPSIS_Rank"]].copy()
topsis_df_out.to_excel("./outputs/TOPSIS_Ranking.xlsx")

# ELECTRE
electre_df.to_excel("./outputs/ELECTRE_Results.xlsx")

# Matrisleri de istersen kaydedebiliriz (advanced kullanım için):
pd.DataFrame(C_matrix, index=candidates_df.index, columns=candidates_df.index).to_excel("./outputs/ELECTRE_Concordance.xlsx")
pd.DataFrame(D_matrix, index=candidates_df.index, columns=candidates_df.index).to_excel("./outputs/ELECTRE_Discordance.xlsx")
pd.DataFrame(outranking_matrix, index=candidates_df.index, columns=candidates_df.index).to_excel("./outputs/ELECTRE_Outranking.xlsx")

print("\nTOPSIS ve ELECTRE hesaplamaları başarıyla tamamlandı.")
print("Çıktılar:")
print("- ./outputs/TOPSIS_Ranking.xlsx")
print("- ./outputs/ELECTRE_Results.xlsx")
