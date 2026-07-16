# Distance to Care

In England, your GP practice is usually the first point of contact with the NHS. It is where you go when something is wrong, where referrals are made, where repeat prescriptions are managed, and where the relationship between a patient and the health system begins. Access to a GP is not optional. It is the foundation of primary care.

But not all GP practices are equal. Some serve a few thousand patients. Others serve tens of thousands. The pressure on a practice shapes everything from how quickly you can get an appointment to how much time a doctor has to spend with you. A GP managing 3,000 patients operates in a fundamentally different environment from one managing 18,000.

This project asks a simple question: how unevenly is that burden distributed across England, and where are the pressure points?

Using official NHS registration data from April 2025, covering 6,127 active GP practices and 63.7 million registered patients, it builds a Patient Burden Index for every practice in England and maps the inequality at regional, town, and practice level.

The results challenge some assumptions. The South East, not the North, carries the heaviest average patient load per practice. Several practices in commuter belt towns outside London are serving patient lists that would be considered extreme by any measure. And 583 practices across the country are operating at more than 175% of the national average burden, with no sign that is set to improve.

This is not a commentary on the quality of care. It is a picture of the structural inequality in how that care is distributed.

---

## The Finding

The South East is the most burdened region in England with an average of 12,664 registered patients per practice. The North West averages 8,519. A patient in the South East shares their GP with 49% more people than a patient in the North West.

583 practices across England are classified as Critical, meaning they serve at least 75% more patients than the national average of 10,304. GP at Hand in London registers 100,329 patients, nearly ten times the national average, making it the single most loaded practice in the dataset.

The burden does not follow the North-South divide most people expect. The South West and East of England both sit above the national average, while London and the Midlands sit below it. The inequality is more granular and more surprising than the headline narrative suggests.

---

## The Metric

Patient Burden Index (PBI) is the ratio of a practice's registered patients to the national average, scaled to 100.

A PBI of 100 means exactly average. A PBI of 200 means twice the national patient load. A PBI of 50 means half.

Burden categories:
- Critical: PBI 175 and above
- High: PBI 125 to 174
- Average: PBI 75 to 124
- Low: PBI 50 to 74
- Very Low: below 50

---

## The Tools

**Interactive map** — every GP practice in England as a dot on a dark map, coloured by burden category, with layer toggles to isolate Critical or Low burden areas. Hover any dot for practice name, town, patient count, and PBI score.

**Practice Lookup** — search 6,127 practices by name or town, filter by region and burden level, sort by any column. Built as a standalone interactive HTML tool.

**Plotly charts** — regional comparison, dot strip plot showing every practice by patient load, lollipop chart of median patients by region, and verdict cards for the most and least burdened practices.

---

## Data

GP practice list from NHS England Organisation Data Service, filtered to active England GP practices with role code RO76.

Patient registrations from NHS England GP Practice Patient List Sizes, April 2025. One record per practice showing total registered patients.

Coordinates from the postcodes.io API used to geocode 6,168 practice postcodes to latitude and longitude.

All data is official, open, and free. No simulated numbers anywhere in this project.

---

## Project Structure
```
Distance to Care/
├── data/
│   ├── epraccur.csv
│   └── gp-reg-pat-prac-all.csv
├── scripts/
│   ├── 01_clean_and_geocode.py
│   ├── 02_analyse.py
│   ├── 03_visualise.py
│   ├── 05_build_lookup.py
│   └── analysis.sql
├── outputs/
│   ├── practices_with_burden.csv
│   ├── regional_burden.csv
│   ├── map_patient_burden.html
│   ├── chart2_regional.html
│   ├── chart3_strip.html
│   ├── chart4_lollipop.html
│   ├── chart5_verdicts.html
│   └── lookup.html
└── README.md
```
---

## Run It

```bash
python scripts/01_clean_and_geocode.py
python scripts/02_analyse.py
python scripts/03_visualise.py
python scripts/05_build_lookup.py
```

Requires: pandas, folium, plotly, requests

Python, pandas, Plotly, Folium, SQL.

---

## About

Built by Trupthi Raj, a data analyst with a focus on retail, commercial, and consumer analytics.

[GitHub](https://github.com/trupthiraj) | [Tableau](https://public.tableau.com/app/profile/trupthi.raj) | [LinkedIn](https://www.linkedin.com/in/trupthi-raj/)
