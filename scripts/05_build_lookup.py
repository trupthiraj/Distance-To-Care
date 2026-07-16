import pandas as pd
import json

df = pd.read_csv('outputs/practices_with_burden.csv')

# Keep only what we need
cols = ['practice_name', 'town', 'nhs_region', 
        'registered_patients', 'pbi', 'burden']
df = df[cols].fillna('')
df['registered_patients'] = df['registered_patients'].astype(int)
df['pbi'] = df['pbi'].round(1)

# Sort by patients descending by default
df = df.sort_values('registered_patients', ascending=False)

data_json = df.to_json(orient='records')

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Distance to Care — Practice Lookup</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #1a1a2e; font-family: Arial, sans-serif; color: #ffffff; padding: 32px 40px; }}
.header {{ margin-bottom: 36px; }}
.title {{ font-size: 28px; font-weight: 700; }}
.title span {{ color: #e94560; }}
.subtitle {{ color: #8888aa; font-size: 13px; margin-top: 6px; }}
.controls {{ display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }}
.controls input, .controls select {{
  background: #0d0d1f; border: 1px solid #2a2a4a; color: #ffffff;
  padding: 10px 14px; border-radius: 8px; font-size: 13px; outline: none;
}}
.controls input {{ width: 280px; }}
.controls input::placeholder {{ color: #8888aa; }}
.controls select {{ cursor: pointer; }}
.stats {{ color: #8888aa; font-size: 12px; margin-bottom: 16px; }}
.stats span {{ color: #ffffff; font-weight: 600; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
thead th {{
  text-align: left; padding: 10px 14px; color: #8888aa;
  font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase;
  border-bottom: 1px solid #2a2a4a; cursor: pointer; user-select: none;
}}
thead th:hover {{ color: #ffffff; }}
tbody tr {{ border-bottom: 1px solid #14142a; }}
tbody tr:hover {{ background: #0d0d1f; }}
tbody td {{ padding: 10px 14px; color: #cccccc; }}
tbody td:first-child {{ color: #ffffff; font-weight: 500; }}
.badge {{
  display: inline-block; padding: 3px 10px; border-radius: 20px;
  font-size: 10px; font-weight: 700; letter-spacing: 0.06em;
}}
.Critical {{ background: rgba(233,69,96,0.2); color: #e94560; }}
.High {{ background: rgba(245,166,35,0.2); color: #f5a623; }}
.Average {{ background: rgba(245,245,0,0.15); color: #f5f500; }}
.Low {{ background: rgba(46,204,113,0.2); color: #2ecc71; }}
.Very-Low {{ background: rgba(0,180,216,0.2); color: #00b4d8; }}
.no-results {{ text-align: center; padding: 48px; color: #8888aa; }}
</style>
</head>
<body>
<div class="header">
  <div class="title">Distance to <span>Care</span></div>
  <div class="subtitle">NHS ENGLAND · GP PRACTICE LOOKUP · APRIL 2025 · 6,127 PRACTICES</div>
</div>
<div class="controls">
  <input type="text" id="search" placeholder="Search practice name or town...">
  <select id="regionFilter">
    <option value="">All Regions</option>
    <option>East of England</option>
    <option>London</option>
    <option>Midlands</option>
    <option>North East and Yorkshire</option>
    <option>North West</option>
    <option>South East</option>
    <option>South West</option>
  </select>
  <select id="burdenFilter">
    <option value="">All Burden Levels</option>
    <option>Critical</option>
    <option>High</option>
    <option>Average</option>
    <option>Low</option>
    <option>Very Low</option>
  </select>
</div>
<div class="stats">Showing <span id="count">0</span> practices</div>
<table>
  <thead>
    <tr>
      <th onclick="sortTable('practice_name')">Practice</th>
      <th onclick="sortTable('town')">Town</th>
      <th onclick="sortTable('nhs_region')">Region</th>
      <th onclick="sortTable('registered_patients')">Patients</th>
      <th onclick="sortTable('pbi')">PBI</th>
      <th>Burden</th>
    </tr>
  </thead>
  <tbody id="tableBody"></tbody>
</table>
<div id="noResults" class="no-results" style="display:none;">No practices found.</div>

<script>
const data = {data_json};
let sortCol = 'registered_patients';
let sortDir = -1;

function render() {{
  const search = document.getElementById('search').value.toLowerCase();
  const region = document.getElementById('regionFilter').value;
  const burden = document.getElementById('burdenFilter').value;

  let filtered = data.filter(r => {{
    const matchSearch = !search ||
      r.practice_name.toLowerCase().includes(search) ||
      r.town.toLowerCase().includes(search);
    const matchRegion = !region || r.nhs_region === region;
    const matchBurden = !burden || r.burden === burden;
    return matchSearch && matchRegion && matchBurden;
  }});

  filtered.sort((a, b) => {{
    let va = a[sortCol], vb = b[sortCol];
    if (va < vb) return sortDir;
    if (va > vb) return -sortDir;
    return 0;
  }});

  document.getElementById('count').textContent = filtered.length.toLocaleString();
  const tbody = document.getElementById('tableBody');
  const noResults = document.getElementById('noResults');

  if (filtered.length === 0) {{
    tbody.innerHTML = '';
    noResults.style.display = 'block';
    return;
  }}

  noResults.style.display = 'none';
  tbody.innerHTML = filtered.slice(0, 500).map(r => {{
    const burdenClass = r.burden.replace(' ', '-');
    return `<tr>
      <td>${{r.practice_name}}</td>
      <td>${{r.town}}</td>
      <td>${{r.nhs_region}}</td>
      <td>${{r.registered_patients.toLocaleString()}}</td>
      <td>${{r.pbi}}</td>
      <td><span class="badge ${{burdenClass}}">${{r.burden}}</span></td>
    </tr>`;
  }}).join('');
}}

function sortTable(col) {{
  if (sortCol === col) sortDir *= -1;
  else {{ sortCol = col; sortDir = -1; }}
  render();
}}

document.getElementById('search').addEventListener('input', render);
document.getElementById('regionFilter').addEventListener('change', render);
document.getElementById('burdenFilter').addEventListener('change', render);

render();
</script>
</body>
</html>"""

with open('outputs/lookup.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved: outputs/lookup.html")