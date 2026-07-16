import pandas as pd
import requests
import time

# ── LOAD & FILTER ──────────────────────────────────────────────────────────────
cols = [
    'practice_code', 'practice_name', 'national_grouping', 'icb_code',
    'addr1', 'addr2', 'addr3', 'town', 'county', 'postcode',
    'open_date', 'close_date', 'status', 'col13', 'col14',
    'col15', 'col16', 'phone', 'col18', 'col19', 'col20',
    'col21', 'col22', 'col23', 'col24', 'role', 'col26'
]

df = pd.read_csv('data/epraccur.csv', header=None, names=cols, dtype=str)

england = df[
    (df['status'] == 'ACTIVE') &
    (df['national_grouping'].str.startswith('Y')) &
    (df['role'] == 'RO76')
].copy()

england['postcode'] = england['postcode'].str.strip()
england = england.dropna(subset=['postcode'])
england = england[england['postcode'] != '']

print(f"Active England GP practices: {len(england)}")
print(f"Sample postcodes: {england['postcode'].head(5).tolist()}")
print()

# ── BATCH GEOCODE via postcodes.io ─────────────────────────────────────────────
def geocode_batch(postcodes):
    url = 'https://api.postcodes.io/postcodes'
    try:
        r = requests.post(url, json={'postcodes': postcodes}, timeout=10)
        results = {}
        if r.status_code == 200:
            for item in r.json()['result']:
                if item['result']:
                    results[item['query'].strip().upper()] = {
                        'lat': item['result']['latitude'],
                        'lon': item['result']['longitude'],
                        'region': item['result']['region'] or '',
                        'ccg': item['result'].get('ccg', '') or ''
                    }
        return results
    except Exception as e:
        print(f"Error: {e}")
        return {}

postcodes = england['postcode'].str.strip().str.upper().tolist()
batch_size = 100
all_coords = {}

print(f"Geocoding {len(postcodes)} postcodes in batches of {batch_size}...")
for i in range(0, len(postcodes), batch_size):
    batch = postcodes[i:i+batch_size]
    coords = geocode_batch(batch)
    all_coords.update(coords)
    if (i // batch_size) % 10 == 0:
        print(f"  Progress: {i}/{len(postcodes)} ({len(all_coords)} matched so far)")
    time.sleep(0.3)

print(f"Total geocoded: {len(all_coords)} of {len(postcodes)}")
print()

# ── MERGE COORDINATES ──────────────────────────────────────────────────────────
england['postcode_key'] = england['postcode'].str.strip().str.upper()
england['lat'] = england['postcode_key'].map(
    lambda x: all_coords.get(x, {}).get('lat'))
england['lon'] = england['postcode_key'].map(
    lambda x: all_coords.get(x, {}).get('lon'))
england['region'] = england['postcode_key'].map(
    lambda x: all_coords.get(x, {}).get('region', ''))

# Region name from national grouping
region_map = {
    'Y63': 'North East and Yorkshire',
    'Y62': 'North West',
    'Y61': 'East of England',
    'Y60': 'Midlands',
    'Y59': 'South East',
    'Y58': 'South West',
    'Y56': 'London'
}
england['nhs_region'] = england['national_grouping'].map(region_map)

geocoded = england.dropna(subset=['lat', 'lon'])
print(f"Practices with coordinates: {len(geocoded)}")
print()
print("By NHS region:")
print(geocoded['nhs_region'].value_counts())

# ── SAVE ───────────────────────────────────────────────────────────────────────
keep_cols = ['practice_code', 'practice_name', 'nhs_region', 'icb_code',
             'town', 'postcode', 'phone', 'lat', 'lon']
geocoded[keep_cols].to_csv('outputs/gp_practices_geocoded.csv', index=False)
print()
print(f"Saved: outputs/gp_practices_geocoded.csv")