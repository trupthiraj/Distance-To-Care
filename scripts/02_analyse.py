import pandas as pd
import numpy as np

# ── LOAD DATA ──────────────────────────────────────────────────────────────────
practices = pd.read_csv('outputs/gp_practices_geocoded.csv')
patients = pd.read_csv('data/gp-reg-pat-prac-all.csv')

# Filter to total counts only
patients = patients[
    (patients['SEX'] == 'ALL') & 
    (patients['AGE'] == 'ALL')
][['CODE', 'NUMBER_OF_PATIENTS']].copy()

patients.columns = ['practice_code', 'registered_patients']
patients['registered_patients'] = pd.to_numeric(
    patients['registered_patients'], errors='coerce'
)

print(f"Geocoded practices: {len(practices)}")
print(f"Patient records: {len(patients)}")

# ── JOIN ───────────────────────────────────────────────────────────────────────
df = practices.merge(patients, on='practice_code', how='inner')
df = df.dropna(subset=['registered_patients', 'lat', 'lon'])

print(f"Matched practices: {len(df)}")
print()

# ── PATIENT BURDEN INDEX ───────────────────────────────────────────────────────
national_avg = df['registered_patients'].mean()
national_std = df['registered_patients'].std()

print(f"National average patients per practice: {national_avg:,.0f}")
print(f"National std dev: {national_std:,.0f}")
print()

# PBI: ratio to national average * 100
# 100 = exactly average, 200 = double the burden, 50 = half
df['pbi'] = (df['registered_patients'] / national_avg * 100).round(1)

# Burden category
def burden_category(pbi):
    if pbi >= 175: return 'Critical'
    elif pbi >= 125: return 'High'
    elif pbi >= 75: return 'Average'
    elif pbi >= 50: return 'Low'
    return 'Very Low'

df['burden'] = df['pbi'].apply(burden_category)

print("=== BURDEN DISTRIBUTION ===")
print(df['burden'].value_counts())
print()

# ── MOST OVERLOADED PRACTICES ──────────────────────────────────────────────────
print("=== TOP 15 MOST OVERLOADED PRACTICES ===")
top = df.nlargest(15, 'registered_patients')[
    ['practice_name', 'town', 'nhs_region', 
     'registered_patients', 'pbi']
]
print(top.to_string(index=False))
print()

# ── MOST UNDERSERVED ──────────────────────────────────────────────────────────
print("=== TOP 15 SMALLEST PRACTICES (potential closures/limited access) ===")
bottom = df[df['registered_patients'] > 100].nsmallest(15, 'registered_patients')[
    ['practice_name', 'town', 'nhs_region',
     'registered_patients', 'pbi']
]
print(bottom.to_string(index=False))
print()

# ── REGIONAL SUMMARY ───────────────────────────────────────────────────────────
regional = (
    df.groupby('nhs_region')
    .agg(
        practices=('practice_code', 'count'),
        total_patients=('registered_patients', 'sum'),
        avg_patients=('registered_patients', 'mean'),
        median_patients=('registered_patients', 'median'),
        max_patients=('registered_patients', 'max'),
        avg_pbi=('pbi', 'mean')
    )
    .round(0)
    .reset_index()
    .sort_values('avg_pbi', ascending=False)
)

print("=== REGIONAL PATIENT BURDEN ===")
print(regional.to_string(index=False))
print()

# ── KEY HEADLINE ───────────────────────────────────────────────────────────────
most_burdened_region = regional.iloc[0]
least_burdened_region = regional.iloc[-1]
most_overloaded = df.nlargest(1, 'registered_patients').iloc[0]

print("=== HEADLINE FINDINGS ===")
print(f"Most burdened region: {most_burdened_region['nhs_region']} "
      f"— avg {most_burdened_region['avg_patients']:,.0f} patients per practice")
print(f"Least burdened region: {least_burdened_region['nhs_region']} "
      f"— avg {least_burdened_region['avg_patients']:,.0f} patients per practice")
print(f"Most overloaded practice: {most_overloaded['practice_name']}, "
      f"{most_overloaded['town']} — {most_overloaded['registered_patients']:,.0f} patients "
      f"(PBI: {most_overloaded['pbi']})")
print(f"National average: {national_avg:,.0f} patients per practice")
print()

# ── SAVE ───────────────────────────────────────────────────────────────────────
df.to_csv('outputs/practices_with_burden.csv', index=False)
regional.to_csv('outputs/regional_burden.csv', index=False)

print("Saved: practices_with_burden.csv, regional_burden.csv")