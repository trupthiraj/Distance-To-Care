import pandas as pd
import folium
import plotly.graph_objects as go
import numpy as np

BG     = '#1a1a2e'
PAPER  = '#1a1a2e'
GRID   = '#2a2a4a'
TEXT   = '#ffffff'
DIM    = '#8888aa'
ACCENT = '#e94560'
GOLD   = '#f5a623'
TEAL   = '#00b4d8'
GREEN  = '#2ecc71'

BURDEN_COLORS = {
    'Critical': '#e94560',
    'High':     '#f5a623',
    'Average':  '#f5f500',
    'Low':      '#2ecc71',
    'Very Low': '#00b4d8'
}

def base(title):
    return dict(
        title=dict(text=title, font=dict(color=TEXT, size=17)),
        paper_bgcolor=PAPER,
        plot_bgcolor=BG,
        font=dict(color=TEXT, family='Arial'),
        margin=dict(l=60, r=40, t=80, b=60)
    )

df = pd.read_csv('outputs/practices_with_burden.csv')
regional = pd.read_csv('outputs/regional_burden.csv')
national_avg = df['registered_patients'].mean()

# ── CHART 1: FOLIUM MAP ────────────────────────────────────────────────────────
print("Building map...")
m = folium.Map(location=[52.8, -1.5], zoom_start=6, tiles='CartoDB dark_matter')

groups = {}
for burden in ['Critical', 'High', 'Average', 'Low', 'Very Low']:
    groups[burden] = folium.FeatureGroup(name=burden, show=True)
    m.add_child(groups[burden])

for _, row in df.iterrows():
    color = BURDEN_COLORS.get(row['burden'], '#888888')
    radius = min(max(row['registered_patients'] / 3000, 3), 12)
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        weight=0,
        tooltip=folium.Tooltip(
            f"<b>{row['practice_name']}</b><br>"
            f"{row['town']}<br>"
            f"Patients: {int(row['registered_patients']):,}<br>"
            f"PBI: {row['pbi']}<br>"
            f"Burden: {row['burden']}"
        )
    ).add_to(groups[row['burden']])

folium.LayerControl(collapsed=False).add_to(m)

legend_html = """
<div style="position:fixed; bottom:30px; left:30px; z-index:1000;
            background:#1a1a2e; padding:16px 20px; border-radius:10px;
            border:1px solid #2a2a4a; font-family:Arial; color:white;">
    <div style="font-size:13px; font-weight:700; margin-bottom:10px;">PATIENT BURDEN INDEX</div>
    <div style="font-size:11px; color:#8888aa; margin-bottom:12px;">National avg: 10,304 patients/practice</div>
"""
for label, color in BURDEN_COLORS.items():
    legend_html += f"""
    <div style="display:flex; align-items:center; margin-bottom:6px;">
        <div style="width:12px; height:12px; border-radius:50%; background:{color}; margin-right:8px;"></div>
        <span style="font-size:12px;">{label}</span>
    </div>"""
legend_html += "</div>"
m.get_root().html.add_child(folium.Element(legend_html))
m.save('outputs/map_patient_burden.html')
print("Saved: map_patient_burden.html")


# ── CHART 2: REGIONAL BAR ─────────────────────────────────────────────────────
regional_sorted = regional.sort_values('avg_patients', ascending=True)

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=regional_sorted['avg_patients'],
    y=regional_sorted['nhs_region'],
    orientation='h',
    marker=dict(
        color=regional_sorted['avg_patients'],
        colorscale=[[0, TEAL], [0.5, GOLD], [1, ACCENT]],
        showscale=False
    ),
    text=[f"{int(v):,}" for v in regional_sorted['avg_patients']],
    textposition='outside',
    textfont=dict(color=TEXT, size=11),
    hovertemplate='<b>%{y}</b><br>Avg patients: %{x:,}<extra></extra>'
))
fig2.add_vline(
    x=national_avg,
    line=dict(color=GOLD, dash='dot', width=1.5),
    annotation_text=f'National avg: {national_avg:,.0f}',
    annotation_font=dict(color=GOLD, size=10)
)
fig2.update_layout(
    **base('Regional Patient Burden — Average Patients Per Practice'),
    xaxis_title='Average Registered Patients',
    yaxis_title='',
    height=450
)
fig2.update_xaxes(gridcolor=GRID, zeroline=False)
fig2.update_yaxes(gridcolor=GRID, zeroline=False)
fig2.write_html('outputs/chart2_regional.html')
print("Saved: chart2_regional.html")


# ── CHART 3: DOT STRIP PLOT ───────────────────────────────────────────────────
region_order = regional.sort_values('avg_patients', ascending=False)['nhs_region'].tolist()

fig3 = go.Figure()

for burden in ['Very Low', 'Low', 'Average', 'High', 'Critical']:
    grp = df[df['burden'] == burden].copy()
    grp['jitter'] = grp['nhs_region'].map(
        {r: i for i, r in enumerate(region_order)}
    ) + np.random.uniform(-0.35, 0.35, len(grp))

    fig3.add_trace(go.Scatter(
        x=grp['jitter'],
        y=grp['registered_patients'],
        mode='markers',
        name=burden,
        marker=dict(
            color=BURDEN_COLORS[burden],
            size=3,
            opacity=0.5,
            line=dict(width=0)
        ),
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>'
            '%{customdata[1]}<br>'
            'Patients: %{y:,}<extra></extra>'
        ),
        customdata=grp[['practice_name', 'nhs_region']].values
    ))

fig3.update_layout(
    **base('Every GP Practice in England — Patient Load by Region'),
    legend=dict(bgcolor=BG, bordercolor=GRID, font=dict(color=TEXT)),
    height=550
)
fig3.update_xaxes(
    tickmode='array',
    tickvals=list(range(len(region_order))),
    ticktext=region_order,
    gridcolor=GRID,
    zeroline=False
)
fig3.update_yaxes(title='Registered Patients', gridcolor=GRID, zeroline=False)
fig3.write_html('outputs/chart3_strip.html')
print("Saved: chart3_strip.html")


# ── CHART 4: LOLLIPOP — MEDIAN BY REGION ─────────────────────────────────────
regional_sorted2 = regional.sort_values('median_patients', ascending=True).copy()

fig4 = go.Figure()

for _, row in regional_sorted2.iterrows():
    fig4.add_trace(go.Scatter(
        x=[0, row['median_patients']],
        y=[row['nhs_region'], row['nhs_region']],
        mode='lines',
        line=dict(color=GRID, width=2),
        showlegend=False,
        hoverinfo='skip'
    ))

fig4.add_trace(go.Scatter(
    x=regional_sorted2['median_patients'],
    y=regional_sorted2['nhs_region'],
    mode='markers+text',
    marker=dict(
        color=regional_sorted2['median_patients'],
        colorscale=[[0, TEAL], [0.5, GOLD], [1, ACCENT]],
        size=16,
        line=dict(width=0),
        showscale=False
    ),
    text=[f"{int(v):,}" for v in regional_sorted2['median_patients']],
    textposition='middle right',
    textfont=dict(color=TEXT, size=10),
    hovertemplate='<b>%{y}</b><br>Median: %{x:,} patients<extra></extra>',
    showlegend=False
))

fig4.add_vline(
    x=df['registered_patients'].median(),
    line=dict(color=GOLD, dash='dot', width=1),
    annotation_text=f"National median: {df['registered_patients'].median():,.0f}",
    annotation_font=dict(color=GOLD, size=9)
)

fig4.update_layout(
    **base('Median Patients Per Practice by Region — The Honest Picture'),
    showlegend=False,
    height=420
)
fig4.update_xaxes(title='Median Registered Patients', gridcolor=GRID, zeroline=False)
fig4.update_yaxes(gridcolor=GRID, zeroline=False)
fig4.write_html('outputs/chart4_lollipop.html')
print("Saved: chart4_lollipop.html")


# ── CHART 5: VERDICT CARDS ────────────────────────────────────────────────────
top5 = df.nlargest(5, 'registered_patients').reset_index(drop=True)
bottom5 = df[df['registered_patients'] > 1000].nsmallest(5, 'registered_patients').reset_index(drop=True)

def card(row, verdict, color):
    pct = abs(row['pbi'] - 100)
    direction = 'above' if row['registered_patients'] > national_avg else 'below'
    return f"""
<div class="card" style="border-top: 3px solid {color};">
  <div class="verdict" style="color:{color};">{verdict}</div>
  <div class="name">{row['practice_name'].title()}</div>
  <div class="location">{row['town'].title()} · {row['nhs_region']}</div>
  <div class="metrics">
    <div class="metric"><div class="val">{int(row['registered_patients']):,}</div><div class="lbl">PATIENTS</div></div>
    <div class="metric"><div class="val">{row['pbi']:.0f}</div><div class="lbl">PBI SCORE</div></div>
    <div class="metric"><div class="val" style="color:{color};">{pct:.0f}%</div><div class="lbl">{direction.upper()} AVG</div></div>
  </div>
</div>"""

overloaded_cards = ''.join([card(r, 'CRITICAL', ACCENT) for _, r in top5.iterrows()])
underloaded_cards = ''.join([card(r, 'LOW BURDEN', TEAL) for _, r in bottom5.iterrows()])

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Distance to Care</title>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:{BG}; font-family:Arial,sans-serif; color:{TEXT}; padding:48px 40px; }}
.header {{ margin-bottom:52px; }}
.title {{ font-size:32px; font-weight:700; }}
.title span {{ color:{ACCENT}; }}
.subtitle {{ color:{DIM}; font-size:13px; margin-top:8px; letter-spacing:0.04em; }}
.kpi-row {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:52px; }}
.kpi {{ background:#0d0d1f; border-radius:12px; padding:24px; border-top:3px solid {TEAL}; }}
.kpi-label {{ font-size:10px; color:{DIM}; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:8px; }}
.kpi-value {{ font-size:28px; font-weight:700; }}
.kpi-sub {{ font-size:12px; color:{DIM}; margin-top:6px; }}
.section-title {{ font-size:11px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:{DIM}; margin-bottom:20px; border-bottom:1px solid {GRID}; padding-bottom:10px; }}
.cards {{ display:flex; gap:14px; flex-wrap:wrap; margin-bottom:52px; }}
.card {{ background:#0d0d1f; border-radius:10px; padding:18px 16px; width:210px; }}
.verdict {{ font-size:9px; font-weight:700; letter-spacing:0.1em; margin-bottom:10px; }}
.name {{ font-size:14px; font-weight:700; margin-bottom:4px; line-height:1.3; }}
.location {{ font-size:10px; color:{DIM}; margin-bottom:14px; }}
.metrics {{ display:flex; justify-content:space-between; }}
.metric {{ text-align:center; flex:1; }}
.val {{ font-size:13px; font-weight:700; }}
.lbl {{ font-size:7px; color:{DIM}; letter-spacing:0.06em; margin-top:3px; }}
</style>
</head>
<body>
<div class="header">
  <div class="title">Distance to <span>Care</span></div>
  <div class="subtitle">NHS ENGLAND GP PATIENT BURDEN ANALYSIS · APRIL 2025 · 6,127 PRACTICES · 63.7M PATIENTS</div>
</div>
<div class="kpi-row">
  <div class="kpi"><div class="kpi-label">National Average</div><div class="kpi-value">{national_avg:,.0f}</div><div class="kpi-sub">patients per practice</div></div>
  <div class="kpi" style="border-top-color:{ACCENT};"><div class="kpi-label">Most Burdened Region</div><div class="kpi-value">South East</div><div class="kpi-sub">12,664 avg patients per practice</div></div>
  <div class="kpi" style="border-top-color:{GOLD};"><div class="kpi-label">Critical Practices</div><div class="kpi-value">{len(df[df['burden']=='Critical']):,}</div><div class="kpi-sub">serving 175% above national average</div></div>
</div>
<div class="section-title">Most Overloaded Practices</div>
<div class="cards">{overloaded_cards}</div>
<div class="section-title">Lowest Burden Practices</div>
<div class="cards">{underloaded_cards}</div>
</body>
</html>"""

with open('outputs/chart5_verdicts.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved: chart5_verdicts.html")
print()
print("All outputs saved.")