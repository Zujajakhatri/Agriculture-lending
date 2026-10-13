# Agricultural Lending in Pakistan

Analysis of Pakistan's agricultural lending market (2020–2025) using data from the State Bank of Pakistan (SBP) and other sources, with an interactive Streamlit dashboard identifying opportunities for Digital Retail Banks (DRBs).

---

## Overview

Agriculture contributes about a quarter of Pakistan's GDP and employs around half of its labour force, yet small farmers remain underserved by formal finance. This project analyses agricultural credit across **39 banks**, **6 bank categories** and **4 provinces** to answer four questions:

1. **How large is Pakistan's agriculture financing market?**
2. **Who is currently serving it?**
3. **Where is financing demand concentrated?**
4. **Where can a Digital Retail Bank participate?**

The data is cleaned and analysed in a Jupyter notebook, exported as visualization-ready CSV files, and presented through an interactive Streamlit dashboard and a written report.

---

## Key Findings

| Question | Finding |
|----------|---------|
| **Market size** | Agricultural disbursement more than doubled, from **PKR 1,183.8 bn (2020)** to **PKR 2,542.6 bn (2025)**, a **16.5% CAGR**. Agriculture's share of total bank advances stayed at around **7%**. |
| **Who serves it** | Commercial banks provide **78.5%** of disbursement, led by HBL (17.9%) and NBP (14.7%). Concentration is low (HHI ≈ 870). **Digital banks hold only 0.05%** of the market. |
| **Where demand is** | **Punjab** is the largest market (~70% of cultivated area). **Khyber Pakhtunkhwa** holds 37% of farms on just 6% of cultivated area, a large base of very small farms. |
| **DRB opportunity** | Punjab scores highest on the DRB Opportunity Index (**85.5**), but **Khyber Pakhtunkhwa (67.7)** is the best fit for a digital, small-ticket lending model. |


---

## Project Structure

```
├── app.py                          # Streamlit dashboard
├── index.html                      # Dashboard Insights page (opened from the dashboard)
├── Agri-data_preprocessing.ipynb   # Data cleaning, analysis and CSV export
├── Raw Data 1.xlsx                 # Source workbook
├── Agri_Bank_PowerBI.csv           # Bank-level dataset
├── Agri_Market_PowerBI.csv         # Yearly market totals
├── Agri_Province_PowerBI.csv       # Provincial profile, Demand Index, DRB score
├── Agri_Crop_PowerBI.csv           # Cultivated area by province and crop
├── Agriculture_lending_report.pdf  # Written report
├── FT-Logo NEW.png                 # Logo
└── README.md
```

---

## Data

The source workbook contains four sheets:

| Sheet | Content |
|-------|---------|
| **Bank Wise Agri finance Data** | Total advances, agricultural disbursement and gross agricultural advances for 39 banks, 2020–2025 |
| **Agri-data** | Provincial population, agricultural workforce, farms, farm size and agriculture's share of GDP and employment |
| **Output-data** | Each province's share of national crop, livestock and fisheries output |
| **Crops Data** | Cultivated area by province and crop |

**Sources:** State Bank of Pakistan (agricultural credit disbursement reports), Pakistan Bureau of Statistics, banks' official websites and other public sources.

> Disbursement figures follow SBP's fiscal year (e.g. 2025 = July 2024 – June 2025). Some provincial values are estimates, and all figures are nominal.

---

## Methodology

- **Market analysis:** yearly totals, year-on-year growth, CAGR, market share and the Herfindahl-Hirschman Index (HHI).
- **Demand Index:** since province-wise lending data is not available, demand is measured through weighted proxies: share of farms (30%), agricultural workforce (20%), cultivated area (25%) and crop output (25%).
- **DRB Opportunity Score (0–100):** six equally weighted factors (agricultural employees, agriculture's share of GDP, agriculture's share of employment, number of farms, small farm size and cultivated area), each scaled relative to the top province. Levels: **High ≥ 70**, **Medium 40–70**, **Low < 40**.

---

## Dashboard

The Streamlit dashboard has four pages:

1. **Executive overview:** key metrics, market trend, top lenders and DRB scores
2. **Bank performance:** bank rankings, trends, scale vs agricultural focus and segment comparison
3. **Regional & agricultural profile:** provincial demand indicators, output shares and crop mix
4. **Trends, penetration & insights:** growth, market-share shifts, credit per farm and rankings

**Features:** year and bank-group filters, Dashboard Insights page, and downloads for the PDF report and the data processing notebook.

---

## Limitations

- Province-wise lending data is not publicly available, so demand is estimated through proxy indicators.
- Some provincial figures (employees, farms, farm size) are estimates based on assumptions.
- The Demand Index and DRB Opportunity Score use assumed weights.
- Cultivated area is a single snapshot with no year dimension.


---

## Author

**Zujaja Khatri**, Data and Research Analyst

*Disclaimer: Figures are compiled from publicly available sources and include estimates; actual values may differ.*
