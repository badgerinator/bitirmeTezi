"""
AHP + TOPSIS + ELECTRE Pipeline (FINAL VERSION)
===============================================

Girdi:
- ./outputs/ahp_weights_summary.xlsx (Birlesik_Agirlik)
- ./outputs/processed_candidates_anonymized_scaled.xlsx

Çıktılar:
- TOPSIS_Ranking.xlsx
- ELECTRE_Results.xlsx
- combined_ranking_report.xlsx
(Optional: Concordance, Discordance, Outranking matrices)
"""

import pandas as pd
import numpy as np

# -------------------------------------
# Parametreler
# -------------------------------------

# Dosya yolları
weights_path = "./outputs/ahp_weights_summary.xlsx"
candidates_path = "./outputs/processed_candidates_anonymized_scaled.xlsx"

# ELECTRE threshold parametreleri (değiştirilebilir)
C_threshold = 0.65  # Concordance threshold
D_threshold = 0.35  # Discordance threshold

# -------------------------------------
# Ağırlıkları Yükle
# -------------------------------------

weights_df = pd.read_excel(weights_path, sheet_name="Birlesik_Agirlik", index_col=0)
weights = weights_df["Birlesik_Agirlik"].values
criteria_names = weights_df.index.tolist()

print(f"Kriterler: {criteria_names}")
print(f"Ağırlıklar: {weights}")

# -------------------------------------
# Aday Verisini Yükle
# -------------------------------------

candidates_df = pd.read_excel(candidates_path)
candidates_df.set_index("ID", inplace=True)

criteria_matrix = candidates_df[criteria_names].values

print(f"\nAday sayısı: {criteria_matrix.shape[0]}")
print(f"Kriter sayısı: {criteria_matrix.shape[1]}")

# -------------------------------------
# TOPSIS Hesaplama
# -------------------------------------

norm = np.linalg.norm(criteria_matrix, axis=0)
normalized_matrix = criteria_matrix / norm
weighted_matrix = normalized_matrix * weights

ideal_solution = np.max(weighted_matrix, axis=0)
anti_ideal_solution = np.min(weighted_matrix, axis=0)

distance_to_ideal = np.linalg.norm(weighted_matrix - ideal_solution, axis=1)
distance_to_anti_ideal = np.linalg.norm(weighted_matrix - anti_ideal_solution, axis=1)

topsis_scores = distance_to_anti_ideal / (distance_to_ideal + distance_to_anti_ideal)
topsis_ranking = np.argsort(topsis_scores)[::-1] + 1

topsis_df = candidates_df.copy()
topsis_df["TOPSIS_Score"] = topsis_scores
topsis_df["TOPSIS_Rank"] = topsis_ranking

# -------------------------------------
# ELECTRE Hesaplama
# -------------------------------------

n_candidates = criteria_matrix.shape[0]
n_criteria = criteria_matrix.shape[1]

C_matrix = np.zeros((n_candidates, n_candidates))
D_matrix = np.zeros((n_candidates, n_candidates))

for i in range(n_candidates):
    for j in range(n_candidates):
        if i == j:
            continue
        concordance_indices = criteria_matrix[i, :] >= criteria_matrix[j, :]
        Cij = np.sum(weights[concordance_indices])
        C_matrix[i, j] = Cij
        
        differences = np.abs(criteria_matrix[i, :] - criteria_matrix[j, :])
        max_diff = np.max(differences)
        if max_diff == 0:
            D_matrix[i, j] = 0
        else:
            Dij = np.max((criteria_matrix[j, :] - criteria_matrix[i, :]) / max_diff)
            D_matrix[i, j] = Dij

outranking_matrix = np.zeros((n_candidates, n_candidates))

for i in range(n_candidates):
    for j in range(n_candidates):
        if i == j:
            continue
        if C_matrix[i, j] >= C_threshold and D_matrix[i, j] <= D_threshold:
            outranking_matrix[i, j] = 1
        else:
            outranking_matrix[i, j] = 0

dominance_scores = np.sum(outranking_matrix, axis=1)

electre_df = pd.DataFrame({
    "ID": candidates_df.index,
    "ELECTRE_Dominance_Score": dominance_scores
}).set_index("ID")

electre_df["ELECTRE_Rank"] = electre_df["ELECTRE_Dominance_Score"].rank(ascending=False, method='min').astype(int)

# -------------------------------------
# Sonuçları Kaydet
# -------------------------------------

# TOPSIS
topsis_df_out = topsis_df[["TOPSIS_Score", "TOPSIS_Rank"]].copy()
topsis_df_out.to_excel("./outputs/TOPSIS_Ranking.xlsx")

# ELECTRE
electre_df.to_excel("./outputs/ELECTRE_Results.xlsx")

# Combined Report
combined_df = pd.DataFrame(index=candidates_df.index)
combined_df["TOPSIS_Score"] = topsis_df_out["TOPSIS_Score"]
combined_df["TOPSIS_Rank"] = topsis_df_out["TOPSIS_Rank"]
combined_df["ELECTRE_Dominance_Score"] = electre_df["ELECTRE_Dominance_Score"]
combined_df["ELECTRE_Rank"] = electre_df["ELECTRE_Rank"]

combined_df.to_excel("./outputs/combined_ranking_report.xlsx")

# -------------------------------------
# (Optional) Matrisleri de kaydet
# -------------------------------------

# Concordance matrix
pd.DataFrame(C_matrix, index=candidates_df.index, columns=candidates_df.index).to_excel("./outputs/ELECTRE_Concordance.xlsx")
# Discordance matrix
pd.DataFrame(D_matrix, index=candidates_df.index, columns=candidates_df.index).to_excel("./outputs/ELECTRE_Discordance.xlsx")
# Outranking matrix
pd.DataFrame(outranking_matrix, index=candidates_df.index, columns=candidates_df.index).to_excel("./outputs/ELECTRE_Outranking.xlsx")

# -------------------------------------
# Print log
# -------------------------------------

print("\nTOPSIS ve ELECTRE hesaplamaları başarıyla tamamlandı.")
print("Çıktılar:")
print("- ./outputs/TOPSIS_Ranking.xlsx")
print("- ./outputs/ELECTRE_Results.xlsx")
print("- ./outputs/combined_ranking_report.xlsx")
print("- ./outputs/ELECTRE_Concordance.xlsx")
print("- ./outputs/ELECTRE_Discordance.xlsx")
print("- ./outputs/ELECTRE_Outranking.xlsx")
