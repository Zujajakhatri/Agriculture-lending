"""
Agricultural Lending in Pakistan — Streamlit dashboard
Single-file application. Run with:  streamlit run app.py

Data: the four CSV exports produced by the final cell of
"Agri-data_preprocessing.ipynb" (Power BI datasets). Place them next to app.py
(or in a ./data folder):
    Agri_Bank_PowerBI.csv, Agri_Market_PowerBI.csv,
    Agri_Province_PowerBI.csv, Agri_Crop_PowerBI.csv

All calculations below reuse the notebook's methodology (same formulas,
same rounding, same treatment of zeros / missing values).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from streamlit import config as _st_config

# ── Monochrome theme without a separate config.toml ──────────────────────────
# Streamlit reads its theme from server config; we set it here so the whole
# app (sliders, tags, radios) is black/grey instead of the default red, and is
# always rendered in light mode. The first session after a server start
# reruns once so the theme takes effect.
_THEME = {
    "theme.base": "light",
    "theme.primaryColor": "#000000",
    "theme.backgroundColor": "#FFFFFF",
    "theme.secondaryBackgroundColor": "#F3F3F3",
    "theme.textColor": "#1A1A1A",
}
_needs_rerun = False
for _k, _v in _THEME.items():
    try:
        if _st_config.get_option(_k) != _v:
            _st_config.set_option(_k, _v)
            _needs_rerun = True
    except Exception:
        pass

# ════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Agricultural Lending in Pakistan",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="expanded",
)
if _needs_rerun:
    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# CONSTANTS  (column names exactly as exported by the notebook)
# ════════════════════════════════════════════════════════════════════════════
TA = "Total Advances (PKR Bn)"
DISB = "Agricultural Credit Disbursement (PKR Bn)"
GROSS = "Agriculture Gross Advances (PKR Bn)"
MSHARE = "Disbursement Market Share (%)"
DSHARE = "Agri Disbursement Share (%)"
GSHARE = "Agri Gross Advances Share (%)"
DGROW = "Disbursement Growth (%)"
GGROW = "Gross Advances Growth (%)"

FARMS = "Estimated Number of Farms"
EMP = "Estimated Number of Employees"
FSIZE = "Estimated Avg. Farm Size (Acres)"
EPF = "Employees per Farm"
EGROW = "Employee Growth (%)"
GDP = "Agriculture – Provincial GDP Contribution (%)"
EMPSH = "Agricultural Share of Employment (%)"
AREA = "Cultivated Area (Acres)"
DPF = "National Disbursement per Farm (PKR)"

SEG_MFB = "MFB + Digital"
SEG_COM = "Commercial / Islamic / Specialized"

LOGO_FILE = "FT-Logo NEW.png"   # keep the logo image in the same folder as app.py
PREPARED_BY = "Prepared by: Zujaja Khatri – Data and Research Analyst"
DISCLAIMER = ("<b style='color:#555;font-weight:600'>Disclaimer:</b> Figures are compiled from publicly available "
              "sources and include estimates; actual values may differ.")

FONT = "IBM Plex Sans, Helvetica Neue, Arial, sans-serif"
INK = "#000000"
GREYS = ["#000000", "#3a3a3a", "#666666", "#8f8f8f", "#b8b8b8", "#dadada"]
PROV_COLORS = ["#000000", "#555555", "#8f8f8f", "#c2c2c2"]
HILITE, MUTED = "#000000", "#c4c4c4"

ST_VER = tuple(int(p) for p in st.__version__.split(".")[:2])
NUM_FMT = "localized" if ST_VER >= (1, 46) else "%d"   # thousands separators where supported

# ════════════════════════════════════════════════════════════════════════════
# STYLING
# ════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root{
  --ink:#000000; --ink-2:#2b2b2b; --mid:#6b6b6b; --soft:#9a9a9a;
  --line:#e2e2e2; --panel:#f5f5f5; --paper:#ffffff;
}
html, body, .stApp, [class*="css"], .stMarkdown, button, input, select, textarea{
  font-family:'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif !important;
}
.stApp{ background:var(--paper); color:var(--ink-2); }
#MainMenu, footer, [data-testid="stDecoration"]{ display:none !important; }
[data-testid="stHeader"]{ background:transparent; }
.block-container{ padding-top:1.4rem; padding-bottom:3rem; max-width:1500px; }
h1,h2,h3,h4,p,li,label,span,div{ color:inherit; }

/* Sidebar */
[data-testid="stSidebar"]{ background:var(--panel); border-right:1px solid var(--line); }
.sb-logo{ display:flex; justify-content:center; padding:0 0 12px 0; margin-top:-6px; }
.sb-logo img{ width:140px; max-width:100%; height:auto; display:block; }
.sb-brand{ text-align:center; }
/* Pull sidebar content up: Streamlit leaves a tall empty header above it */
[data-testid="stSidebarHeader"]{ height:2.25rem !important; min-height:0 !important; padding-top:0.5rem !important;
                                  padding-bottom:0 !important; }
[data-testid="stSidebarUserContent"]{ padding-top:0 !important; }
.sb-brand{ border-bottom:1px solid #d0d0d0; padding:0 0 14px 0; margin-bottom:6px; }
.sb-brand .t1{ font-size:17px; font-weight:700; color:#000; line-height:1.2; letter-spacing:-0.01em; }
.sb-brand .t2{ font-size:12px; color:var(--mid); margin-top:4px; }
.sb-h{ font-size:12px; font-weight:600; color:#000; margin:18px 0 2px 0; }
.sb-note{ font-size:12px; color:var(--mid); line-height:1.5; }
.sb-ref{ list-style:none; padding:0; margin:6px 0 0 0; }
.sb-ref li{ font-size:11.5px; line-height:1.45; color:#1a1a1a; margin:0 0 9px 0; padding-left:14px; text-indent:-14px;
            word-break:break-word; }
.sb-ref li i{ color:#000; }
.sb-src{ list-style:none; padding:0; margin:4px 0 0 0; }
.sb-src li{ font-size:12.5px; line-height:1.4; margin:0 0 8px 0; padding-left:12px; position:relative; }
.sb-src li::before{ content:""; position:absolute; left:0; top:7px; width:5px; height:5px; background:#000; border-radius:50%; }
.sb-src li{ color:#1a1a1a; }
.sb-sec{ font-size:11px; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:var(--mid);
         margin:22px 0 4px 0; padding-top:14px; border-top:1px solid #d9d9d9; }
[data-testid="stSidebar"] [data-testid="stExpander"] details{ border:1px solid #dcdcdc; border-radius:8px; background:#fff; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary p{ font-size:13px; font-weight:600; }
[data-testid="stSidebar"] button[kind="secondary"]{ border-radius:8px; border-color:#cfcfcf; }

/* Download button */
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button{ background:#000; color:#fff; border:1px solid #000;
  border-radius:6px; font-weight:600; }
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button:hover{ background:#2b2b2b; color:#fff; border-color:#2b2b2b; }
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button *{ color:#fff !important; }

/* Navigation radio → list (only the page navigator, keyed "nav") */
.st-key-nav [role="radiogroup"]{ gap:2px; width:100%; }
.st-key-nav [role="radiogroup"] > div{ width:100%; }
.st-key-nav [role="radiogroup"] label{ padding:9px 12px !important; border-radius:6px; margin:0 !important; width:100%;
                   border:1px solid transparent; cursor:pointer; box-sizing:border-box; display:flex !important; }
.st-key-nav [role="radiogroup"] label:hover{ background:#e9e9e9; }
.st-key-nav [role="radiogroup"] label[data-selected="true"], .st-key-nav [role="radiogroup"] label:has(input:checked){ background:#000 !important; border-color:#000; }
.st-key-nav [role="radiogroup"] label[data-selected="true"] *, .st-key-nav [role="radiogroup"] label:has(input:checked) *{ color:#fff !important; }
.st-key-nav div:has(> div[data-testid="stMarkdownContainer"]) > div:first-child:not([data-testid]),
.st-key-nav [role="radiogroup"] > label > div:first-child{ display:none !important; }
.st-key-nav p{ font-size:14px !important; font-weight:500; }

/* Widget accents: neutralise Streamlit red */
span[data-baseweb="tag"]{ background:#1f1f1f !important; border-radius:4px !important; }
span[data-baseweb="tag"], span[data-baseweb="tag"] *{ color:#fff !important; }
div[data-baseweb="select"] > div{ border-color:#cfcfcf !important; border-radius:6px !important; background:#fff !important; }
div[data-baseweb="slider"] div[role="slider"]{ background:#000 !important; border-color:#000 !important; box-shadow:none !important; }
div[data-testid="stSliderThumbValue"], div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"]{ color:#000 !important; }
div[data-baseweb="slider"] > div > div > div{ background:#000; }
button[data-baseweb="tab"][aria-selected="true"]{ color:#000 !important; }
div[data-baseweb="tab-highlight"]{ background:#000 !important; }
div[data-baseweb="tab-border"]{ background:var(--line) !important; }
button[data-baseweb="tab"] p{ font-weight:500; }

/* Masthead */
.mast{ background:#000; color:#fff; border-radius:10px; padding:22px 28px 20px 28px;
       display:flex; justify-content:space-between; align-items:flex-end; gap:24px; flex-wrap:wrap; margin-bottom:22px; }
.mast .ttl{ font-size:28px; font-weight:700; letter-spacing:-0.02em; color:#fff; line-height:1.1; }
.mast .sub{ font-size:13.5px; color:#bdbdbd; margin-top:6px; }
.mast .meta{ text-align:right; font-size:13px; color:#fff; font-weight:500; letter-spacing:.01em;
             white-space:nowrap; align-self:center; }
.mast .meta .lbl{ color:#9a9a9a; font-weight:400; margin-right:4px; }
.mast .meta .sep{ color:#5c5c5c; margin:0 10px; }

/* Section header */
.sec{ margin:26px 0 12px 0; padding-bottom:8px; border-bottom:2px solid #000; display:flex;
      justify-content:space-between; align-items:baseline; gap:12px; flex-wrap:wrap; }
.sec .h{ font-size:19px; font-weight:700; color:#000; letter-spacing:-0.01em; }
.sec .s{ font-size:12.5px; color:var(--mid); }

/* KPI cards */
.kpi{ background:#fff; border:1px solid var(--line); border-top:3px solid #000; border-radius:4px 4px 8px 8px;
      padding:14px 16px 13px 16px; height:100%; min-height:122px; }
.kpi .l{ font-size:12.5px; color:var(--mid); font-weight:500; line-height:1.3; min-height:16px; }
.kpi .v{ font-size:27px; font-weight:600; color:#000; letter-spacing:-0.02em; margin-top:6px;
         font-variant-numeric:tabular-nums; line-height:1.15; word-break:break-word; }
.kpi .v.sm{ font-size:19px; letter-spacing:-0.01em; }
.kpi .d{ font-size:12.5px; margin-top:7px; font-variant-numeric:tabular-nums; color:var(--mid); }
.kpi .d .up{ color:#000; font-weight:600; }
.kpi .d .dn{ color:#000; font-weight:600; background:#e9e9e9; padding:1px 5px; border-radius:3px; }
.kpi.dark{ background:#000; border-color:#000; }
.kpi.dark .l, .kpi.dark .d{ color:#bdbdbd; }
.kpi.dark .v, .kpi.dark .d .up{ color:#fff; }

/* Chart cards */
.ct{ font-size:15px; font-weight:600; color:#000; letter-spacing:-0.005em; }
.cs{ font-size:12.5px; color:var(--mid); margin-top:2px; margin-bottom:2px; }
div[data-testid="stVerticalBlockBorderWrapper"]{ border-color:var(--line) !important; border-radius:8px !important; background:#fff; }

/* Insights */
.ins{ list-style:none; padding:0; margin:0; counter-reset:none; }
.ins li{ border-left:3px solid #000; background:#f7f7f7; padding:11px 14px; margin:0 0 8px 0;
         font-size:14px; line-height:1.55; color:#1a1a1a; border-radius:0 6px 6px 0; }
.ins li b{ color:#000; }

.note{ font-size:12.5px; color:var(--mid); background:#f7f7f7; border:1px solid var(--line);
       border-radius:6px; padding:9px 12px; margin:4px 0 10px 0; line-height:1.5; }
.note b{ color:#000; }

[data-testid="stDataFrame"]{ border:1px solid var(--line); border-radius:6px; }
@media (max-width: 900px){ .mast .meta{ text-align:left; white-space:normal; } .kpi .v{ font-size:22px; } }
</style>
""",
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════════════════════════
# DATA LOADING  (notebook exports → same derived columns as notebook cell 58)
# ════════════════════════════════════════════════════════════════════════════
FILES = {
    "bank": "Agri_Bank_PowerBI.csv",
    "market": "Agri_Market_PowerBI.csv",
    "province": "Agri_Province_PowerBI.csv",
    "crop": "Agri_Crop_PowerBI.csv",
}


def _find(name: str) -> Path | None:
    here = Path(__file__).resolve().parent
    for p in (here / name, here / "data" / name, Path.cwd() / name, Path.cwd() / "data" / name):
        if p.exists():
            return p
    return None


def logo_data_uri() -> str | None:
    """Read the logo image from the app folder and return it as a data URI (None if not found)."""
    import base64
    path = _find(LOGO_FILE)
    if path is None:                                   # fall back to any image with "logo" in its name
        hits = [p for p in Path(__file__).resolve().parent.glob("*") if "logo" in p.name.lower()
                and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg")]
        path = hits[0] if hits else None
    if path is None:
        return None
    mime = "image/svg+xml" if path.suffix.lower() == ".svg" else f"image/{path.suffix.lower().lstrip('.').replace('jpg', 'jpeg')}"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


@st.cache_data(show_spinner=False)
def load_data():
    paths = {k: _find(v) for k, v in FILES.items()}
    missing = [FILES[k] for k, p in paths.items() if p is None]
    if missing:
        return None, missing

    bank = pd.read_csv(paths["bank"])
    market = pd.read_csv(paths["market"])
    prov = pd.read_csv(paths["province"])
    crop = pd.read_csv(paths["crop"])

    for df in (bank, prov):
        for c in df.columns:
            if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object:
                df[c] = df[c].str.strip()

    # Bank-wise YoY growth — notebook cell 58: groupby("Bank").pct_change() * 100, rounded 2
    bank = bank.sort_values(["Bank", "Year"]).reset_index(drop=True)
    bank[DGROW] = (bank.groupby("Bank")[DISB].pct_change() * 100).round(2)
    bank[GGROW] = (bank.groupby("Bank")[GROSS].pct_change() * 100).round(2)
    # 0 → x produces ±inf in pandas; there is no meaningful growth rate, so show as n/a
    bank[[DGROW, GGROW]] = bank[[DGROW, GGROW]].replace([np.inf, -np.inf], np.nan)

    prov["DRB Opportunity Level"] = prov["DRB Opportunity Level"].astype(str)
    return {"bank": bank, "market": market, "prov": prov, "crop": crop}, []


def build_market(b: pd.DataFrame) -> pd.DataFrame:
    """Market table — identical logic to notebook cell 58 (market_pbi)."""
    m = (
        b.groupby("Year")
        .agg({TA: "sum", DISB: "sum", GROSS: "sum", "Bank": "nunique"})
        .reset_index()
        .rename(columns={"Bank": "Number of Banks"})
    )
    m["Disbursement YoY (%)"] = (m[DISB].pct_change() * 100).round(2)
    m["Gross Advances YoY (%)"] = (m[GROSS].pct_change() * 100).round(2)
    m["Agri Share of Total Advances (%)"] = (m[GROSS] / m[TA] * 100).round(2)
    return m


def cagr(start, end, years):
    """Notebook cell 20."""
    if years <= 0 or pd.isna(start) or pd.isna(end) or start <= 0:
        return np.nan
    return ((end / start) ** (1 / years) - 1) * 100


def drb_factor_indices(prov_year: pd.DataFrame) -> pd.DataFrame:
    """DRB factor indices for one year — notebook cell 58 (max-normalisation, small farms score higher)."""
    p = prov_year.set_index("Province").copy()
    out = pd.DataFrame(index=p.index)
    labels = {
        EMP: "Agri employees",
        GDP: "Agri share of GDP",
        EMPSH: "Agri share of employment",
        FARMS: "Number of farms",
        AREA: "Cultivated area",
    }
    for col, lab in labels.items():
        out[lab] = (p[col] / p[col].max() * 100).round(1)
    small = 1 / p[FSIZE]
    out["Small farm size"] = (small / small.max() * 100).round(1)
    out = out[["Agri employees", "Agri share of GDP", "Agri share of employment",
               "Number of farms", "Small farm size", "Cultivated area"]]
    return out


# ════════════════════════════════════════════════════════════════════════════
# FORMATTING & UI HELPERS
# ════════════════════════════════════════════════════════════════════════════
def f_bn(v, dec=2):
    if v is None or pd.isna(v):
        return "—"
    return f"PKR {v / 1000:,.{dec}f} Tn" if abs(v) >= 1000 else f"PKR {v:,.{dec}f} Bn"


def f_pct(v, dec=2, sign=False):
    if v is None or pd.isna(v):
        return "—"
    return f"{v:+,.{dec}f}%" if sign else f"{v:,.{dec}f}%"


def f_cnt(v, dec=2):
    if v is None or pd.isna(v):
        return "—"
    if abs(v) >= 1e6:
        return f"{v / 1e6:,.{dec}f} Mn"
    return f"{v:,.0f}"


def f_pkr(v):
    return "—" if v is None or pd.isna(v) else f"PKR {v:,.0f}"


def delta(v, unit="%", ref=""):
    if v is None or pd.isna(v):
        return f"<span>No prior-year comparison</span>"
    cls, arrow = ("up", "▲") if v >= 0 else ("dn", "▼")
    num = f"{abs(v):,.2f}{'%' if unit == '%' else ' pp'}"
    return f"<span class='{cls}'>{arrow} {num}</span> {ref}"


def kpi(label, value, foot="", small=False, dark=False):
    st.markdown(
        f"<div class='kpi{' dark' if dark else ''}'><div class='l'>{label}</div>"
        f"<div class='v{' sm' if small else ''}'>{value}</div><div class='d'>{foot}</div></div>",
        unsafe_allow_html=True,
    )


def section(title, sub=""):
    st.markdown(f"<div class='sec'><div class='h'>{title}</div><div class='s'>{sub}</div></div>",
                unsafe_allow_html=True)


def note(html):
    st.markdown(f"<div class='note'>{html}</div>", unsafe_allow_html=True)


def insights(items):
    st.markdown("<ul class='ins'>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>",
                unsafe_allow_html=True)


def show_fig(fig, title, sub=""):
    with st.container(border=True):
        st.markdown(f"<div class='ct'>{title}</div>" + (f"<div class='cs'>{sub}</div>" if sub else ""),
                    unsafe_allow_html=True)
        cfg = {"displayModeBar": False, "responsive": True}
        if ST_VER >= (1, 46):
            st.plotly_chart(fig, width="stretch", config=cfg)
        else:
            st.plotly_chart(fig, use_container_width=True, config=cfg)


def show_table(df, column_config=None, height=None, hide_index=True):
    kw = dict(hide_index=hide_index, column_config=column_config or {})
    if height:
        kw["height"] = height
    if ST_VER >= (1, 46):
        st.dataframe(df, width="stretch", **kw)
    else:
        st.dataframe(df, use_container_width=True, **kw)


def style(fig, height=360, legend=True, ysuffix="", xsuffix="", ytitle=None, xtitle=None):
    fig.update_layout(
        template="none",
        height=height,
        font=dict(family=FONT, size=12, color="#1f1f1f"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=8, r=16, t=36 if legend else 12, b=8),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, xanchor="left",
                    title=None, font=dict(size=11.5), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="white", bordercolor="#000", font=dict(family=FONT, size=12, color="#000")),
        bargap=0.28,
    )
    fig.update_xaxes(showgrid=False, linecolor="#9e9e9e", tickcolor="#9e9e9e", ticks="outside",
                     ticklen=4, ticksuffix=xsuffix, title=xtitle, title_font=dict(size=12, color="#555"),
                     automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor="#ececec", zeroline=False, linecolor="#9e9e9e",
                     ticksuffix=ysuffix, title=ytitle, title_font=dict(size=12, color="#555"), automargin=True)
    return fig


def hbar(df, x, y, height=None, fmt=",.2f", suffix="", highlight=None, hover_extra=None):
    df = df.iloc[::-1]
    colors = [HILITE if (highlight is None or n in highlight) else MUTED for n in df[y]]
    custom = df[hover_extra].values if hover_extra else None
    ht = f"<b>%{{y}}</b><br>%{{x:{fmt}}}{suffix}"
    if hover_extra:
        ht += "".join(f"<br>{c}: %{{customdata[{i}]}}" for i, c in enumerate(hover_extra))
    fig = go.Figure(go.Bar(
        x=df[x], y=df[y], orientation="h", marker_color=colors,
        text=[f"{v:{fmt}}{suffix}" if pd.notna(v) else "" for v in df[x]],
        textposition="outside", cliponaxis=False, textfont=dict(size=11.5, color="#1f1f1f"),
        customdata=custom, hovertemplate=ht + "<extra></extra>",
    ))
    style(fig, height=height or max(260, 30 * len(df) + 60), legend=False, xsuffix=suffix)
    xmax = pd.to_numeric(df[x], errors="coerce").max()
    xmin = min(0, pd.to_numeric(df[x], errors="coerce").min())
    rng = [xmin * 1.25, xmax * 1.22] if pd.notna(xmax) and xmax > 0 else None
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0", showticklabels=False, ticks="", range=rng)
    fig.update_yaxes(showgrid=False, ticks="", linecolor="#ffffff")
    return fig


# ════════════════════════════════════════════════════════════════════════════
# LOAD
# ════════════════════════════════════════════════════════════════════════════
data, missing = load_data()
if data is None:
    st.error(
        "Data files not found: " + ", ".join(missing)
        + ". Place the four CSV exports from the notebook in the same folder as app.py (or in ./data)."
    )
    st.stop()

BANK_ALL, MARKET_CSV, PROV_ALL, CROP = data["bank"], data["market"], data["prov"], data["crop"]
YEARS = sorted(BANK_ALL["Year"].unique().tolist())
ALL_TYPES = sorted(BANK_ALL["Bank Type"].unique().tolist())
TYPE_SEG = BANK_ALL.drop_duplicates("Bank Type").set_index("Bank Type")["Segment"].to_dict()

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — navigation + global filters
# ════════════════════════════════════════════════════════════════════════════
PAGES = ["Executive overview", "Bank performance", "Regional & agricultural profile",
         "Trends, penetration & insights"]

SHORT_TYPE = {
    "Conventional + Islamic Banking": "Conventional + Islamic",
    "Full Islamic": "Full Islamic",
    "Foreign Commercial": "Foreign",
    "Microfinance Bank": "Microfinance",
    "Digital Bank": "Digital",
    "Specialized Bank": "Specialized",
}
SEG_LABELS = {"All banks": "All", SEG_COM: "Commercial", SEG_MFB: "MFB + Digital"}
HAS_PILLS = hasattr(st, "pills")
HAS_SEG = hasattr(st, "segmented_control")



def reset_filters():
    """Clear every filter widget so it returns to its default value."""
    for k in [k for k in st.session_state if str(k).startswith("f_")]:
        del st.session_state[k]


with st.sidebar:
    LOGO_URI = logo_data_uri()
    if LOGO_URI:
        st.markdown(f"<div class='sb-logo'><img src='{LOGO_URI}' alt='Future Technologies'></div>",
                    unsafe_allow_html=True)
    st.markdown("<div class='sb-brand'><div class='t1'>Agricultural Lending<br>in Pakistan</div>"
                "<div class='t2'>Banking & agricultural finance intelligence</div></div>",
                unsafe_allow_html=True)
    page = st.radio("Dashboard", PAGES, label_visibility="collapsed", key="nav")

    st.markdown("<div class='sb-sec'>Filters</div>", unsafe_allow_html=True)

    # Years — select one or more
    st.markdown("<div class='sb-h'>Years</div>", unsafe_allow_html=True)
    if HAS_PILLS:
        sel_years = st.pills("Years", YEARS, selection_mode="multi", default=YEARS, key="f_years",
                             label_visibility="collapsed")
    else:
        sel_years = st.multiselect("Years", YEARS, default=YEARS, key="f_years", label_visibility="collapsed")
    SEL_YEARS = sorted(sel_years) if sel_years else [YEARS[-1]]   # nothing selected -> latest year
    year = SEL_YEARS[-1]                 # snapshot cards and rankings use the latest selected year
    p0, p1 = SEL_YEARS[0], SEL_YEARS[-1]  # growth / CAGR use the first and last selected year
    st.caption(f"Snapshot: {year} · Trend: {p0}–{p1}" if p1 > p0 else f"Snapshot: {year}")

    # Bank group — three clear buttons instead of radio dots
    st.markdown("<div class='sb-h'>Bank group</div>", unsafe_allow_html=True)
    seg_opts = ["All banks", SEG_COM, SEG_MFB]
    if HAS_SEG:
        seg_choice = st.segmented_control("Bank group", seg_opts, default="All banks", key="f_seg",
                                          format_func=lambda v: SEG_LABELS[v], label_visibility="collapsed")
        if seg_choice is None:
            seg_choice = "All banks"
    else:
        seg_choice = st.radio("Bank group", seg_opts, key="f_seg", horizontal=True,
                              format_func=lambda v: SEG_LABELS[v], label_visibility="collapsed")

    # Bank types — tucked away, all selected by default
    type_opts = ALL_TYPES if seg_choice == "All banks" else [t for t in ALL_TYPES if TYPE_SEG[t] == seg_choice]
    types_key = f"f_types_{seg_choice}"
    with st.expander("Bank types", expanded=False):
        if HAS_PILLS:
            sel_types = st.pills("Bank types", type_opts, selection_mode="multi", default=type_opts, key=types_key,
                                 format_func=lambda v: SHORT_TYPE.get(v, v), label_visibility="collapsed")
        else:
            sel_types = st.multiselect("Bank types", type_opts, default=type_opts, key=types_key,
                                       format_func=lambda v: SHORT_TYPE.get(v, v), label_visibility="collapsed")
        sel_types = list(sel_types or [])
        st.caption(f"{len(sel_types)} of {len(type_opts)} selected")

    st.button("Reset filters", key="reset_btn", on_click=reset_filters,
              **({"width": "stretch"} if ST_VER >= (1, 46) else {"use_container_width": True}))

    # References (APA style): (author, year, title, publisher)
    REFERENCES = [
        ("Pakistan Bureau of Statistics", "n.d.", "PBS library", "https://www.pbs.gov.pk"),
        ("Pakistan Mercantile Exchange", "n.d.", "Electronic warehouse receipt system", "PMEX"),
        ("Securities and Exchange Commission of Pakistan", "n.d.",
         "Collateral management companies regulations", "SECP"),
        ("State Bank of Pakistan", "2020–2026",
         "Agricultural credit disbursement reports (FY2020–FY2026)",
         "Agriculture Credit & Financial Inclusion Department"),
        ("State Bank of Pakistan", "2025", "Risk coverage scheme for small farmers and underserved areas", "SBP"),
        ("State Bank of Pakistan", "n.d.", "Zarkhez-e (Asaan Digital Zarai Qarza)", "SBP"),
    ]
    st.markdown("<div class='sb-sec'>References</div>", unsafe_allow_html=True)
    st.markdown(
        "<ul class='sb-ref'>"
        + "".join(f"<li>{a}. ({y}). <i>{t}</i>. {p}{'' if p.startswith('http') else '.'}</li>"
                  for a, y, t, p in REFERENCES)
        + "</ul>",
        unsafe_allow_html=True,
    )


if not sel_types:
    st.warning("Select at least one bank type in the sidebar to populate the dashboard.")
    st.stop()

BANK = BANK_ALL[BANK_ALL["Bank Type"].isin(sel_types)].copy()
FILTERED = set(sel_types) != set(ALL_TYPES)
MARKET = MARKET_CSV.copy() if not FILTERED else build_market(BANK)
M = MARKET.set_index("Year")
BY = BANK[BANK["Year"] == year]
PROV_Y = PROV_ALL[PROV_ALL["Year"] == year]
PERIOD = BANK[BANK["Year"].isin(SEL_YEARS)]
scope_txt = "All banks" if not FILTERED else (seg_choice if set(sel_types) == set(type_opts) and seg_choice != "All banks"
                                               else ", ".join(sel_types))

# Shared numbers
cur = M.loc[year]
prev_year = year - 1 if (year - 1) in M.index else None
farms_y = PROV_Y[FARMS].sum()
dpf_y = (PROV_Y[DPF].iloc[0] if not FILTERED else cur[DISB] * 1e9 / farms_y) if farms_y else np.nan

# ════════════════════════════════════════════════════════════════════════════
# MASTHEAD
# ════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"<div class='mast'><div><div class='ttl'>{page}</div>"
    f"<div class='sub'>Agricultural lending in Pakistan · bank, market and provincial view</div></div>"
    f"<div class='meta'><span class='lbl'>Coverage:</span> {BY['Bank'].nunique()} Banks"
    f"<span class='sep'>|</span>{len(sel_types)} Banking {'Category' if len(sel_types) == 1 else 'Categories'}"
    f"<span class='sep'>|</span>"
    f"{f'{p0}–{p1} Trend Analysis' if p1 > p0 else f'{year} Snapshot'}</div></div>",
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════════════════════════
# SHARED CHART BUILDERS
# ════════════════════════════════════════════════════════════════════════════
def market_trend_fig(height=360):
    m = MARKET[MARKET["Year"].isin(SEL_YEARS)]
    fig = go.Figure()
    fig.add_bar(x=m["Year"], y=m[DISB], name="Credit disbursement", marker_color="#000",
                text=[f"{v:,.0f}" for v in m[DISB]], textposition="outside", textfont=dict(size=11),
                hovertemplate="<b>%{x}</b><br>Disbursement: PKR %{y:,.2f} Bn<extra></extra>")
    fig.add_scatter(x=m["Year"], y=m[GROSS], name="Gross advances (outstanding)", mode="lines+markers",
                    line=dict(color="#8f8f8f", width=2.5), marker=dict(size=8, color="#8f8f8f"),
                    hovertemplate="<b>%{x}</b><br>Gross advances: PKR %{y:,.2f} Bn<extra></extra>")
    style(fig, height=height, ytitle="PKR Bn")
    fig.update_xaxes(dtick=1)
    return fig


def type_share_table(b):
    """Notebook cell 27: disbursement share by bank type per year."""
    t = b.pivot_table(index="Year", columns="Bank Type", values=DISB, aggfunc="sum")
    return (t.div(t.sum(axis=1), axis=0) * 100).round(2)


def type_share_fig(height=360):
    ts = type_share_table(BANK)
    ts = ts.loc[ts.index.isin(SEL_YEARS)]
    order = ts.mean().sort_values(ascending=False).index.tolist()
    fig = go.Figure()
    for i, t in enumerate(order):
        fig.add_scatter(x=ts.index, y=ts[t], name=t, stackgroup="one", mode="lines",
                        line=dict(width=0.6, color="#ffffff"), fillcolor=GREYS[i % len(GREYS)],
                        hovertemplate=f"<b>{t}</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>")
    style(fig, height=height, ysuffix="%")
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(range=[0, 100])
    return fig


def drb_fig(df, height=300):
    d = df.sort_values("DRB Opportunity Score", ascending=True)
    shade = {"High": "#000000", "Medium": "#7a7a7a", "Low": "#c4c4c4"}
    fig = go.Figure(go.Bar(
        x=d["DRB Opportunity Score"], y=d["Province"], orientation="h",
        marker_color=[shade.get(l, "#999") for l in d["DRB Opportunity Level"]],
        text=[f"{s:.1f} · {l}" for s, l in zip(d["DRB Opportunity Score"], d["DRB Opportunity Level"])],
        textposition="outside", cliponaxis=False,
        customdata=d[["DRB Rank", "Demand Index"]].values,
        hovertemplate="<b>%{y}</b><br>DRB score: %{x:.1f}<br>Rank: %{customdata[0]}"
                      "<br>Demand index: %{customdata[1]:.1f}<extra></extra>",
    ))
    style(fig, height=height, legend=False)
    fig.update_xaxes(range=[0, 128], showgrid=True, gridcolor="#f0f0f0", title="Score (0–100)",
                     tickvals=[0, 20, 40, 60, 80, 100])
    fig.update_yaxes(showgrid=False, ticks="")
    return fig


def segment_summary(b, y_end, y_start):
    """Notebook cell 34: MFB + Digital vs rest of market."""
    seg = b.groupby(["Year", "Segment"])[DISB].sum().unstack()
    seg_share = (seg.div(seg.sum(axis=1), axis=0) * 100).round(2)
    nb = b[b["Year"] == y_end].groupby("Segment")["Bank"].nunique()
    n = y_end - y_start
    out = pd.DataFrame({
        "Segment": seg.columns,
        f"Disbursement {y_end} (PKR Bn)": seg.loc[y_end].round(1).values,
        f"Share {y_end} (%)": seg_share.loc[y_end].values,
        f"CAGR {y_start}–{y_end} (%)": [round(cagr(seg.loc[y_start, s], seg.loc[y_end, s], n), 1) for s in seg.columns],
        "No. of banks": nb.reindex(seg.columns).values,
    })
    out["Avg disbursement per bank (PKR Bn)"] = (out[f"Disbursement {y_end} (PKR Bn)"] / out["No. of banks"]).round(1)
    return out, seg_share


def share_shift():
    """Change in disbursement market share (pp) between period start and end, all in-scope banks."""
    a = BANK[BANK["Year"] == p0].set_index("Bank")[MSHARE]
    b = BANK[BANK["Year"] == p1].set_index("Bank")[MSHARE]
    out = (b - a).dropna().rename("Change (pp)").reset_index()
    return out.reindex(out["Change (pp)"].abs().sort_values(ascending=False).index).reset_index(drop=True)


def bank_cagr_table():
    """Per-bank disbursement CAGR over the trend period (notebook cagr(); zero start excluded)."""
    bc = BANK[BANK["Year"].isin([p0, p1])].pivot_table(index="Bank", columns="Year", values=DISB)
    out = pd.DataFrame({"Bank": bc.index})
    if p1 > p0:
        out[f"Disbursement {p0} (PKR Bn)"] = bc[p0].values
    out[f"Disbursement {p1} (PKR Bn)"] = bc[p1].values
    out[f"CAGR {p0}–{p1} (%)"] = [round(cagr(a_, b_, p1 - p0), 1) for a_, b_ in zip(bc[p0].values, bc[p1].values)]
    return out.dropna(subset=[f"CAGR {p0}–{p1} (%)"]).sort_values(f"CAGR {p0}–{p1} (%)", ascending=False)


def bank_type_growth():
    """Notebook cell 28: disbursement by bank type, start vs end of period, with CAGR."""
    td = BANK.pivot_table(index="Year", columns="Bank Type", values=DISB, aggfunc="sum")
    s0, s1 = td.loc[p0].round(1), td.loc[p1].round(1)
    tg = pd.DataFrame({"Bank type": td.columns})
    if p1 > p0:
        tg[f"{p0} (PKR Bn)"] = s0.values
    tg[f"{p1} (PKR Bn)"] = s1.values
    tg["CAGR (%)"] = [round(cagr(a_, b_, p1 - p0), 1) if a_ > 0 else None for a_, b_ in zip(s0.values, s1.values)]
    return tg.sort_values(f"{p1} (PKR Bn)", ascending=False)


def disbursement_per_acre():
    """Notebook cell 33: disbursement ÷ total cultivated acres."""
    return cur[DISB] * 1e9 / CROP[AREA].sum()


def trends_insights():
    m = MARKET[MARKET["Year"].isin(SEL_YEARS)]
    chg, bcg = share_shift(), bank_cagr_table()
    out = []
    if p1 > p0:
        cd, cg, ct = (cagr(M.loc[p0, k], M.loc[p1, k], p1 - p0) for k in (DISB, GROSS, TA))
        out.append(f"Between {p0} and {p1}, disbursement grew from <b>{f_bn(M.loc[p0, DISB])}</b> to "
                   f"<b>{f_bn(M.loc[p1, DISB])}</b> (CAGR <b>{cd:.1f}%</b>), while gross advances grew at "
                   f"<b>{cg:.1f}%</b> and total advances at <b>{ct:.1f}%</b>.")
    gg = m.dropna(subset=["Gross Advances YoY (%)"])
    if len(gg):
        w = gg.sort_values("Gross Advances YoY (%)").iloc[0]
        bst = m.dropna(subset=["Disbursement YoY (%)"]).sort_values("Disbursement YoY (%)").iloc[-1]
        out.append(f"The strongest disbursement year was <b>{int(bst['Year'])}</b> (+{bst['Disbursement YoY (%)']:.2f}%). "
                   f"The weakest year for the outstanding book was <b>{int(w['Year'])}</b> "
                   f"({w['Gross Advances YoY (%)']:+.2f}%), showing disbursement and outstanding balances "
                   f"do not always move together.")
    if len(chg) and p1 > p0:
        gain, loss = chg.sort_values("Change (pp)").iloc[-1], chg.sort_values("Change (pp)").iloc[0]
        out.append(f"Largest market-share gain {p0}–{p1}: <b>{gain['Bank']}</b> ({gain['Change (pp)']:+.2f} pp). "
                   f"Largest loss: <b>{loss['Bank']}</b> ({loss['Change (pp)']:+.2f} pp).")
    if len(bcg):
        fb = bcg.iloc[0]
        out.append(f"Fastest-growing in-scope lender over the period: <b>{fb['Bank']}</b> at "
                   f"{fb[f'CAGR {p0}–{p1} (%)']:.1f}% a year.")
    if len(PROV_Y):
        lo = PROV_Y.sort_values("DRB Rank").iloc[-1]
        out.append(f"<b>{lo['Province']}</b> has the lowest DRB opportunity score ({lo['DRB Opportunity Score']:.1f}, "
                   f"{lo['DRB Opportunity Level']}) despite agriculture's {lo[GDP]:.2f}% share of provincial GDP; "
                   f"its small farm base ({f_cnt(lo[FARMS])} farms) limits scale for digital lending.")
    out.append(f"Each farm received on average <b>{f_pkr(dpf_y)}</b> and each cultivated acre "
               f"<b>{f_pkr(disbursement_per_acre())}</b> of disbursement in {year}.")
    return out


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
def insights_button():
    """Front-page button that shows / hides the written Dashboard Insights (index.html)."""
    html_path = _find("index.html")
    if "show_insights" not in st.session_state:
        st.session_state["show_insights"] = False

    label = "Hide dashboard insights" if st.session_state["show_insights"] else "Dashboard insights"
    # Buttons sit right next to each other (small fixed gap)
    try:
        row = st.container(horizontal=True, gap="small")          # Streamlit 1.48+
        b1 = b2 = b3 = row
    except TypeError:                                            # older Streamlit
        b1, b2, b3, _ = st.columns([1, 1, 1.3, 4], gap="small")
    with b1:
        clicked = st.button(label, key="insights_btn", type="primary")
    with b2:
        pdf_download_button()
    with b3:
        notebook_download_button()
    if clicked:
        st.session_state["show_insights"] = not st.session_state["show_insights"]
        st.rerun()

    if st.session_state["show_insights"]:
        if html_path is None:
            note("<b>index.html</b> not found. Place it in the same folder as app.py.")
        else:
            with st.container(border=True):
                html_text = html_path.read_text(encoding="utf-8")
                if LOGO_URI:                       # the iframe can't read local files, so embed the logo
                    html_text = html_text.replace(f'src="{LOGO_FILE}"', f'src="{LOGO_URI}"')
                if hasattr(st, "iframe"):          # newer Streamlit
                    st.iframe(html_text, height=900)
                else:                               # older Streamlit
                    components.html(html_text, height=900, scrolling=True)
        st.write("")


def page_overview():
    insights_button()

    yoy_d = cur["Disbursement YoY (%)"] if prev_year else np.nan
    yoy_g = cur["Gross Advances YoY (%)"] if prev_year else np.nan
    share = cur["Agri Share of Total Advances (%)"]
    share_chg = share - M.loc[prev_year, "Agri Share of Total Advances (%)"] if prev_year else np.nan
    c_disb = cagr(M.loc[p0, DISB], M.loc[p1, DISB], p1 - p0)
    c_ta = cagr(M.loc[p0, TA], M.loc[p1, TA], p1 - p0)

    ref = f"vs {prev_year}" if prev_year else ""
    c = st.columns(4, gap="small")
    with c[0]:
        kpi("Agricultural credit disbursement", f_bn(cur[DISB]), delta(yoy_d, ref=ref), dark=True)
    with c[1]:
        kpi("Agricultural gross advances", f_bn(cur[GROSS]), delta(yoy_g, ref=ref))
    with c[2]:
        kpi("Agri share of total advances", f_pct(share), delta(share_chg, unit="pp", ref=ref))
    with c[3]:
        kpi(f"Disbursement CAGR {p0}–{p1}", f_pct(c_disb) if p1 > p0 else "—",
            f"Total advances CAGR {f_pct(c_ta)}" if p1 > p0 else "Select a period of two or more years")

    st.write("")
    top = BY.sort_values(DISB, ascending=False).head(1)
    tp = PROV_Y.sort_values("DRB Rank").head(1)
    farms_prev = PROV_ALL[PROV_ALL["Year"] == prev_year][FARMS].sum() if prev_year else np.nan
    c = st.columns(4, gap="small")
    with c[0]:
        if len(top):
            r = top.iloc[0]
            kpi("Top agricultural lender", r["Bank"], f"{f_bn(r[DISB])} · {f_pct(r[MSHARE])} market share", small=True)
    with c[1]:
        if len(tp):
            r = tp.iloc[0]
            kpi("Top province (DRB opportunity)", r["Province"],
                f"Score {r['DRB Opportunity Score']:.1f} · {r['DRB Opportunity Level']} · Demand rank {int(r['Demand Rank'])}",
                small=True)
    with c[2]:
        kpi("Number of farms (est.)", f_cnt(farms_y),
            delta((farms_y / farms_prev - 1) * 100 if prev_year and farms_prev else np.nan, ref=ref))
    with c[3]:
        dpf_prev = PROV_ALL[PROV_ALL["Year"] == prev_year][DPF].iloc[0] if prev_year and not FILTERED else np.nan
        kpi("Disbursement per farm", f_pkr(dpf_y),
            delta((dpf_y / dpf_prev - 1) * 100, ref=ref) if pd.notna(dpf_prev)
            else f"{int(cur['Number of Banks'])} banks in scope")

    section("Market size and who serves it", f"Trend period {p0}–{p1} · reporting year {year}")
    l, r = st.columns([1.35, 1], gap="medium")
    with l:
        show_fig(market_trend_fig(380), "Agricultural credit disbursement vs gross advances",
                 "How large is the market, and is the outstanding book keeping pace with new lending? PKR Bn")
    with r:
        top10 = BY.sort_values(DISB, ascending=False).head(10)
        show_fig(hbar(top10, DISB, "Bank", height=380, hover_extra=["Bank Type", MSHARE]),
                 f"Top 10 agricultural lenders, {year}", "Credit disbursement, PKR Bn")

    l, r = st.columns([1.35, 1], gap="medium")
    with l:
        show_fig(type_share_fig(340), "Share of disbursement by bank type",
                 "Which institution types carry agricultural lending? % of in-scope disbursement")
    with r:
        show_fig(drb_fig(PROV_Y, 340), f"Provincial DRB opportunity score, {year}",
                 "Where is financing demand concentrated? Notebook's six-factor index, 0–100")

    section("Management insights", "Generated from the filtered data")
    insights(overview_insights(c_disb, c_ta))


def overview_insights(c_disb, c_ta):
    out = []
    yoy = cur["Disbursement YoY (%)"] if prev_year else np.nan
    s = f"Agricultural credit disbursement reached <b>{f_bn(cur[DISB])}</b> in {year}"
    if pd.notna(yoy):
        s += f", {'up' if yoy >= 0 else 'down'} <b>{abs(yoy):.2f}%</b> on {prev_year}"
    if p1 > p0 and pd.notna(c_disb):
        s += (f". Over {p0}–{p1} it compounded at <b>{c_disb:.1f}%</b> a year against <b>{c_ta:.1f}%</b> "
              f"for total advances")
    out.append(s + ".")

    ranked = BY.sort_values(DISB, ascending=False)
    if len(ranked) >= 5:
        t5, t10 = ranked[MSHARE].head(5).sum(), ranked[MSHARE].head(10).sum()
        out.append(f"Lending is concentrated: the top 5 in-scope lenders hold <b>{t5:.2f}%</b> of industry "
                   f"disbursement and the top 10 hold <b>{t10:.2f}%</b>. <b>{ranked.iloc[0]['Bank']}</b> leads "
                   f"with {f_pct(ranked.iloc[0][MSHARE])}.")

    sh, sh0 = cur["Agri Share of Total Advances (%)"], M.loc[p0, "Agri Share of Total Advances (%)"]
    out.append(f"Agriculture's outstanding book is <b>{sh:.2f}%</b> of total advances in {year} "
               f"(vs {sh0:.2f}% in {p0}), so new disbursement growth is not translating into a larger share "
               f"of bank balance sheets." if sh <= sh0 else
               f"Agriculture's outstanding book is <b>{sh:.2f}%</b> of total advances in {year}, up from {sh0:.2f}% in {p0}.")

    if BANK["Segment"].nunique() == 2 and p1 > p0:
        ss, _ = segment_summary(BANK, year, p0) if year > p0 else segment_summary(BANK, p1, p0)
        mfb = ss[ss["Segment"] == SEG_MFB].iloc[0]
        ycol = [c for c in ss.columns if c.startswith("Share")][0]
        ccol = [c for c in ss.columns if c.startswith("CAGR")][0]
        out.append(f"Microfinance and digital banks account for <b>{mfb[ycol]:.2f}%</b> of disbursement "
                   f"({int(mfb['No. of banks'])} banks), growing at <b>{mfb[ccol]:.1f}%</b> a year — the segment a "
                   f"digital retail bank would compete in.")

    if len(PROV_Y):
        tp = PROV_Y.sort_values("DRB Rank").iloc[0]
        sm = PROV_Y.sort_values(FSIZE).iloc[0]
        out.append(f"<b>{tp['Province']}</b> ranks first on the DRB opportunity score ({tp['DRB Opportunity Score']:.1f}, "
                   f"{tp['DRB Opportunity Level']}). <b>{sm['Province']}</b> has the smallest average farm "
                   f"({sm[FSIZE]:.2f} acres across {f_cnt(sm[FARMS])} farms), the profile best suited to small-ticket "
                   f"digital lending.")
    if pd.notna(dpf_y):
        out.append(f"Average disbursement equals <b>{f_pkr(dpf_y)}</b> per farm in {year}.")
    return out


# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — BANK PERFORMANCE
# ════════════════════════════════════════════════════════════════════════════
BANK_METRICS = {
    "Agricultural credit disbursement (PKR Bn)": (DISB, ",.2f", ""),
    "Agricultural gross advances (PKR Bn)": (GROSS, ",.2f", ""),
    "Disbursement market share (%)": (MSHARE, ",.2f", "%"),
    "Agri disbursement share of advances (%)": (DSHARE, ",.2f", "%"),
    "Agri gross advances share of advances (%)": (GSHARE, ",.2f", "%"),
    "Disbursement growth, YoY (%)": (DGROW, ",.2f", "%"),
    "Gross advances growth, YoY (%)": (GGROW, ",.2f", "%"),
    "Total advances (PKR Bn)": (TA, ",.2f", ""),
}

TABLE_CFG = {
    "Rank": st.column_config.NumberColumn("Rank", format="%d", width="small"),
    TA: st.column_config.NumberColumn("Total advances (PKR Bn)", format="%.2f"),
    DISB: st.column_config.NumberColumn("Agri disbursement (PKR Bn)", format="%.2f"),
    GROSS: st.column_config.NumberColumn("Agri gross advances (PKR Bn)", format="%.2f"),
    MSHARE: st.column_config.ProgressColumn("Market share", format="%.2f%%", min_value=0, max_value=20),
    DSHARE: st.column_config.NumberColumn("Disb. share of advances", format="%.2f%%"),
    GSHARE: st.column_config.NumberColumn("Gross adv. share of advances", format="%.2f%%"),
    DGROW: st.column_config.NumberColumn("Disb. growth YoY", format="%.2f%%"),
    GGROW: st.column_config.NumberColumn("Gross adv. growth YoY", format="%.2f%%"),
}


def page_banks():
    c1, c2, c3 = st.columns([1.3, 1.1, 2.1], gap="medium")
    with c1:
        mlabel = st.selectbox("Ranking metric", list(BANK_METRICS), index=0)
    with c2:
        top_n = st.radio("Top N", [5, 10, 15, 20], index=1, horizontal=True)
    col, fmt, suf = BANK_METRICS[mlabel]
    mshort = mlabel.split(" (")[0]
    mlow = mshort[0].lower() + mshort[1:]
    ranked = BY.dropna(subset=[col]).sort_values(col, ascending=False)
    default_cmp = BY.sort_values(DISB, ascending=False)["Bank"].head(5).tolist()
    with c3:
        cmp_banks = st.multiselect("Compare banks", sorted(BANK["Bank"].unique()), default=default_cmp)

    # KPI strip for scope
    c = st.columns(4, gap="small")
    with c[0]:
        kpi("In-scope disbursement", f_bn(BY[DISB].sum()), f"{BY['Bank'].nunique()} banks · {year}", dark=True)
    with c[1]:
        kpi("In-scope gross advances", f_bn(BY[GROSS].sum()), f"Total advances {f_bn(BY[TA].sum())}")
    with c[2]:
        ind = BANK_ALL.loc[BANK_ALL["Year"] == year, DISB].sum()
        kpi("Share of industry disbursement", f_pct(BY[DISB].sum() / ind * 100 if ind else np.nan),
            "In-scope banks ÷ all banks")
    with c[3]:
        sel = BY[BY["Bank"].isin(cmp_banks)]
        kpi("Selected banks' disbursement", f_bn(sel[DISB].sum()) if len(sel) else "—",
            f"{f_pct(sel[MSHARE].sum())} market share" if len(sel) else "Pick banks to compare")

    section(f"Bank ranking: {mlow}", f"Top {top_n} · {year} · selected banks in black")
    chart_h = max(420, 30 * top_n + 80)          # same height for both charts
    l, r = st.columns(2, gap="medium")              # same width for both charts
    with l:
        show_fig(hbar(ranked.head(top_n), col, "Bank", height=chart_h, fmt=fmt, suffix=suf,
                      highlight=set(cmp_banks) if cmp_banks else None, hover_extra=["Bank Type"]),
                 f"Top {top_n} banks by {mlow}",
                 "Growth rates exclude banks with no prior-year lending" if col in (DGROW, GGROW) else mlabel)
    with r:
        tr = PERIOD[PERIOD["Bank"].isin(cmp_banks)]
        fig = go.Figure()
        order = tr[tr["Year"] == tr["Year"].max()].sort_values(col, ascending=False)["Bank"].tolist()
        for i, b in enumerate(order):
            d = tr[tr["Bank"] == b]
            fig.add_scatter(x=d["Year"], y=d[col], name=b, mode="lines+markers",
                            line=dict(color=GREYS[i % 6], width=2.2, dash="solid" if i < 6 else "dot"),
                            marker=dict(size=6),
                            hovertemplate=f"<b>{b}</b><br>%{{x}}: %{{y:{fmt}}}{suf}<extra></extra>")
        style(fig, height=chart_h, ysuffix=suf)
        fig.update_xaxes(dtick=1)
        fig.update_layout(legend=dict(orientation="h", y=-0.12, yanchor="top"))
        show_fig(fig, f"Trend for selected banks, {p0}–{p1}", mlabel)

    section("Scale vs agricultural focus", "Is a bank big in agriculture because it is big, or because it specialises?")
    l, r = st.columns(2, gap="medium")              # same width as the row above
    with l:
        d = BY.dropna(subset=[DSHARE])
        d = d[d[TA] > 0]
        lab = set(cmp_banks) if cmp_banks else set(BY.sort_values(DISB, ascending=False)["Bank"].head(3))
        fig = go.Figure(go.Scatter(
            x=d[MSHARE], y=d[DSHARE], mode="markers+text",
            text=[b.split(" (")[0].replace(" Limited", "") if b in lab else "" for b in d["Bank"]],
            textposition="top center", textfont=dict(size=10.5, color="#333"),
            marker=dict(size=np.sqrt(d[TA].clip(lower=0.01)) * 1.1 + 6,
                        color=["#000" if b in cmp_banks else "#a8a8a8" for b in d["Bank"]],
                        line=dict(width=1, color="#fff"), opacity=0.9),
            customdata=d[["Bank", "Bank Type", TA, DISB]].values,
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Market share: %{x:.2f}%"
                          "<br>Agri disbursement share: %{y:.2f}%<br>Total advances: PKR %{customdata[2]:,.2f} Bn"
                          "<br>Disbursement: PKR %{customdata[3]:,.2f} Bn<extra></extra>",
        ))
        style(fig, height=chart_h, legend=False, xsuffix="%", ysuffix="%",
              xtitle="Share of industry agri disbursement", ytitle="Agri disbursement ÷ total advances")
        fig.update_xaxes(showgrid=True, gridcolor="#ececec")
        show_fig(fig, f"Market share vs agricultural focus, {year}", "Bubble size = total advances")
    with r:
        bt = PERIOD.groupby("Bank Type", as_index=False)[[GROSS, TA]].sum()
        bt["Agri Share (%)"] = (bt[GROSS] / bt[TA] * 100).round(1)  # notebook cell 49
        bt = bt.sort_values("Agri Share (%)", ascending=False)
        show_fig(hbar(bt, "Agri Share (%)", "Bank Type", height=chart_h, fmt=".1f", suffix="%"),
                 f"Agriculture as % of total loans by bank type, {p0}–{p1}",
                 "Gross advances ÷ total advances, pooled over the period")

    section("Ranking table", f"All in-scope banks · {year} · click a column header to sort")
    t = ranked if col not in (DGROW, GGROW) else BY.sort_values(col, ascending=False, na_position="last")
    t = t[["Bank", "Bank Type", TA, DISB, GROSS, MSHARE, DSHARE, GSHARE, DGROW, GGROW]].reset_index(drop=True)
    t.insert(0, "Rank", range(1, len(t) + 1))
    cfg = dict(TABLE_CFG)
    cfg[MSHARE] = st.column_config.ProgressColumn("Market share", format="%.2f%%", min_value=0,
                                                  max_value=float(max(1, BY[MSHARE].max())))
    show_table(t, cfg, height=min(38 * len(t) + 40, 560))

    # Segment table: Full Islamic shown as its own group
    seg_table = BANK.copy()
    seg_table.loc[seg_table["Bank Type"] == "Full Islamic", "Segment"] = "Full Islamic"
    seg_table.loc[seg_table["Segment"] == SEG_COM, "Segment"] = "Commercial / Specialized"
    if seg_table["Segment"].nunique() > 1 and year > p0:
        section("Segment comparison", f"Commercial, Full Islamic and MFB + Digital banks · CAGR {p0}–{year}")
        ss, _ = segment_summary(seg_table, year, p0)
        order = ["Commercial / Specialized", "Full Islamic", SEG_MFB]
        ss["_o"] = ss["Segment"].map({k: i for i, k in enumerate(order)})
        show_table(ss.sort_values("_o").drop(columns="_o"))


# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — REGIONAL & AGRICULTURAL PROFILE
# ════════════════════════════════════════════════════════════════════════════
def page_regional():
    provs = sorted(PROV_ALL["Province"].unique())
    sel_p = st.multiselect("Provinces", provs, default=provs)
    if not sel_p:
        st.info("Select at least one province.")
        return
    P = PROV_Y[PROV_Y["Province"].isin(sel_p)]
    pcol = {p: PROV_COLORS[i % 4] for i, p in enumerate(provs)}

    note("The source data does <b>not split bank lending by province</b>, so credit is shown at national level "
         "(disbursement per farm). Provincial pages compare the agricultural demand base that the notebook's "
         "Demand Index and DRB Opportunity Score are built on.")

    c = st.columns(4, gap="small")
    with c[0]:
        kpi("Farms (est.)", f_cnt(P[FARMS].sum()), f"{len(P)} province(s) · {year}", dark=True)
    with c[1]:
        kpi("Agricultural employees (est.)", f_cnt(P[EMP].sum()),
            f"{P[EMP].sum() / P[FARMS].sum():.2f} employees per farm" if P[FARMS].sum() else "")
    with c[2]:
        kpi("Cultivated area", f"{f_cnt(P[AREA].sum())} acres", "Crop survey snapshot")
    with c[3]:
        kpi("National disbursement per farm", f_pkr(dpf_y), f"{year} · all provinces")

    section("Where is demand concentrated?", f"{year}")
    l, r = st.columns(2, gap="medium")
    with l:
        fig = go.Figure()
        for i, (cname, lab) in enumerate([("Farms – Share (%)", "Farms"), ("Employees – Share (%)", "Employees"),
                                          ("Cultivated Area – Share (%)", "Cultivated area")]):
            fig.add_bar(x=P["Province"], y=P[cname], name=lab, marker_color=["#000", "#7a7a7a", "#c4c4c4"][i],
                        text=[f"{v:.1f}" for v in P[cname]], textposition="outside", textfont=dict(size=10.5),
                        hovertemplate=f"<b>%{{x}}</b><br>{lab} share: %{{y:.2f}}%<extra></extra>")
        style(fig, height=380, ysuffix="%")
        fig.update_layout(barmode="group")
        fig.update_yaxes(range=[0, 80])
        show_fig(fig, "Province share of national demand indicators", "% of national total in the year")
    with r:
        fig = go.Figure()
        for p in P["Province"]:
            d = P[P["Province"] == p]
            fig.add_scatter(x=d[FSIZE], y=d[FARMS], mode="markers+text", name=p, text=[p],
                            textposition="top center", textfont=dict(size=11),
                            marker=dict(size=np.sqrt(d[EMP]) / 120 + 12, color=pcol[p],
                                        line=dict(color="#fff", width=1.5)),
                            customdata=d[[EMP, EPF]].values,
                            hovertemplate=f"<b>{p}</b><br>Avg farm size: %{{x:.2f}} acres<br>Farms: %{{y:,.0f}}"
                                          "<br>Employees: %{customdata[0]:,.0f}<br>Employees/farm: %{customdata[1]:.2f}"
                                          "<extra></extra>")
        style(fig, height=380, legend=False, xtitle="Average farm size (acres)", ytitle="Number of farms")
        fig.update_xaxes(showgrid=True, gridcolor="#ececec", range=[-2, P[FSIZE].max() * 1.2 + 1])
        fig.update_yaxes(range=[0, P[FARMS].max() * 1.25])
        show_fig(fig, "Number of farms vs average farm size", "Bubble size = agricultural employees")

    fig = go.Figure()
    for i, (cname, lab) in enumerate([("Crop Output (%)", "Crop"), ("Livestock Output (%)", "Livestock"),
                                      ("Fisheries Output (%)", "Fisheries")]):
        fig.add_bar(x=P["Province"], y=P[cname], name=lab, marker_color=["#000", "#7a7a7a", "#c4c4c4"][i],
                    text=P[cname], textposition="outside", textfont=dict(size=10.5),
                    hovertemplate=f"<b>%{{x}}</b><br>{lab} output share: %{{y}}%<extra></extra>")
    style(fig, height=360, ysuffix="%")
    fig.update_layout(barmode="group")
    fig.update_yaxes(range=[0, 68])
    show_fig(fig, "Province share of national agricultural output", "Crop, livestock and fisheries, %")

    section("What drives the DRB opportunity score?", "Six equally weighted factors, max-normalised (best province = 100)")
    l, r = st.columns([1.5, 1], gap="medium")
    with l:
        idx = drb_factor_indices(PROV_Y).loc[[p for p in PROV_Y.sort_values("DRB Rank")["Province"] if p in sel_p]]
        idx["DRB score"] = PROV_Y.set_index("Province").loc[idx.index, "DRB Opportunity Score"]
        z = idx.values
        xl = ["Agri<br>employees", "Agri % of<br>GDP", "Agri % of<br>employment", "Number<br>of farms",
              "Small<br>farm size", "Cultivated<br>area", "DRB<br>score"]
        fig = go.Figure(go.Heatmap(
            z=z, x=xl, y=idx.index, colorscale=[[0, "#f4f4f4"], [0.5, "#8a8a8a"], [1, "#000"]],
            zmin=0, zmax=100, showscale=False, xgap=3, ygap=3,
            text=[[f"{v:.1f}" for v in row] for row in z], texttemplate="%{text}",
            textfont=dict(size=12),
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}<extra></extra>",
        ))
        style(fig, height=130 + 55 * len(idx), legend=False)
        fig.update_xaxes(side="top", showline=False, ticks="", tickangle=0, tickfont=dict(size=11))
        fig.update_yaxes(autorange="reversed", showgrid=False, ticks="")
        show_fig(fig, f"DRB factor indices, {year}", "Darker = stronger. Index normalisation uses all four provinces")
    with r:
        show_fig(drb_fig(P, 130 + 55 * len(P) + 40), "DRB opportunity score and level",
                 "High ≥ 70 · Medium 40–70 · Low < 40")

    section("Crop profile", "Cultivated area by crop · snapshot (no year dimension)")
    l, r = st.columns([1, 1.35], gap="medium")
    with l:
        cp = st.selectbox("Province", ["All provinces"] + sel_p, key="crop_prov")
        cn = st.radio("Crops shown", [5, 10, 15], index=1, horizontal=True, key="crop_n")
        if cp == "All provinces":
            nat = CROP[CROP["Province"].isin(sel_p)].groupby("Crop", as_index=False)[AREA].sum()
            nat["Share (%)"] = (nat[AREA] / nat[AREA].sum() * 100).round(2)
        else:
            nat = CROP[CROP["Province"] == cp][["Crop", AREA, "Province Crop Share (%)"]].rename(
                columns={"Province Crop Share (%)": "Share (%)"})
        nat = nat.sort_values(AREA, ascending=False).head(cn)
        topk = nat["Share (%)"].head(5).sum()
        show_fig(hbar(nat, "Share (%)", "Crop", fmt=".1f", suffix="%", hover_extra=[AREA]),
                 f"Top crops — {cp}", f"Share of cultivated area · top 5 crops = {topk:.1f}%")
    with r:
        top_crops = (CROP.groupby("Crop")[AREA].sum().sort_values(ascending=False).head(10).index.tolist())
        hm = (CROP[CROP["Province"].isin(sel_p) & CROP["Crop"].isin(top_crops)]
              .pivot_table(index="Province", columns="Crop", values="Province Crop Share (%)", aggfunc="sum")
              .reindex(columns=top_crops).fillna(0))
        fig = go.Figure(go.Heatmap(
            z=hm.values, x=hm.columns, y=hm.index, colorscale=[[0, "#f6f6f6"], [0.35, "#9a9a9a"], [1, "#000"]],
            showscale=False, xgap=3, ygap=3, texttemplate="%{z:.1f}", textfont=dict(size=11),
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.2f}% of province cultivated area<extra></extra>",
        ))
        style(fig, height=140 + 55 * len(hm), legend=False)
        fig.update_xaxes(side="top", showline=False, ticks="", tickangle=-35, tickfont=dict(size=11))
        fig.update_yaxes(showgrid=False, ticks="")
        show_fig(fig, "Crop mix by province — 10 largest national crops",
                 "% of each province's cultivated area")

    section("Provincial profile table", f"{year}")
    cols = ["Province", "Population", EMP, FARMS, FSIZE, EPF, EGROW, GDP, EMPSH, AREA,
            "Demand Index", "Demand Rank", "DRB Opportunity Score", "DRB Opportunity Level", "DRB Rank"]
    ptab = P.sort_values("DRB Rank")[cols].copy()
    ptab[EMP] = ptab[EMP].round(0)  # display only; estimates carry fractional people
    show_table(ptab, {
        "Population": st.column_config.NumberColumn(format=NUM_FMT),
        EMP: st.column_config.NumberColumn("Employees (est.)", format=NUM_FMT),
        FARMS: st.column_config.NumberColumn("Farms (est.)", format=NUM_FMT),
        FSIZE: st.column_config.NumberColumn("Avg farm size (acres)", format="%.2f"),
        EPF: st.column_config.NumberColumn("Employees / farm", format="%.2f"),
        EGROW: st.column_config.NumberColumn("Employee growth", format="%.2f%%"),
        GDP: st.column_config.NumberColumn("Agri % of GDP", format="%.2f%%"),
        EMPSH: st.column_config.NumberColumn("Agri % of employment", format="%.2f%%"),
        AREA: st.column_config.NumberColumn("Cultivated area (acres)", format=NUM_FMT),
        "Demand Index": st.column_config.NumberColumn(format="%.1f"),
        "DRB Opportunity Score": st.column_config.ProgressColumn("DRB score", format="%.1f", min_value=0, max_value=100),
    })


# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 — TRENDS, PENETRATION & INSIGHTS
# ════════════════════════════════════════════════════════════════════════════
def page_trends():
    c1, c2 = st.columns([1, 3])
    with c1:
        top_n = st.radio("Top N", [5, 10, 15], index=1, horizontal=True, key="t_topn")

    m = MARKET[MARKET["Year"].isin(SEL_YEARS)]
    total_acres = CROP[AREA].sum()
    dpa = cur[DISB] * 1e9 / total_acres  # notebook cell 33

    # ---------- TRENDS ----------
    section("Trends", f"{p0}–{p1}")
    l, r = st.columns(2, gap="medium")
    with l:
        g = m.dropna(subset=["Disbursement YoY (%)"])
        fig = go.Figure()
        fig.add_bar(x=g["Year"], y=g["Disbursement YoY (%)"], name="Credit disbursement", marker_color="#000",
                    text=[f"{v:.1f}%" for v in g["Disbursement YoY (%)"]], textposition="outside",
                    textfont=dict(size=10.5), hovertemplate="%{x}: %{y:.2f}%<extra>Disbursement</extra>")
        style(fig, height=360, legend=False, ysuffix="%")
        fig.update_xaxes(dtick=1)
        vals = g["Disbursement YoY (%)"]
        if len(vals):
            fig.update_yaxes(range=[min(0, vals.min()) * 1.35, max(0, vals.max()) * 1.18 + 2])
        show_fig(fig, "Year-on-year growth", "Agricultural credit disbursement, %")
    with r:
        fig = go.Figure()
        fig.add_scatter(x=m["Year"], y=m["Agri Share of Total Advances (%)"], mode="lines+markers+text",
                        line=dict(color="#000", width=2.6), marker=dict(size=8, color="#000"),
                        text=[f"{v:.2f}%" for v in m["Agri Share of Total Advances (%)"]],
                        textposition="top center", textfont=dict(size=11),
                        hovertemplate="%{x}: %{y:.2f}%<extra></extra>")
        style(fig, height=360, legend=False, ysuffix="%")
        lo = m["Agri Share of Total Advances (%)"].min()
        fig.update_yaxes(range=[max(0, lo - 2), m["Agri Share of Total Advances (%)"].max() + 1.5])
        fig.update_xaxes(dtick=1)
        show_fig(fig, "Agriculture's share of total advances", "Gross agri advances ÷ total advances")

    # Change in disbursement market share (pp) between period start and end — notebook MSHARE column
    a = BANK[BANK["Year"] == p0].set_index("Bank")[MSHARE]
    b = BANK[BANK["Year"] == p1].set_index("Bank")[MSHARE]
    chg = (b - a).dropna().rename("Change (pp)").reset_index()
    chg = chg.reindex(chg["Change (pp)"].abs().sort_values(ascending=False).index).head(top_n)
    chg = chg.sort_values("Change (pp)", ascending=True)
    fig = go.Figure(go.Bar(
        x=chg["Change (pp)"], y=chg["Bank"], orientation="h",
        marker_color=["#000" if v >= 0 else "#a6a6a6" for v in chg["Change (pp)"]],
        text=[f"{v:+.2f} pp" for v in chg["Change (pp)"]], textposition="outside", cliponaxis=False,
        textfont=dict(size=11), hovertemplate="<b>%{y}</b><br>%{x:+.2f} pp<extra></extra>"))
    style(fig, height=max(300, 30 * len(chg) + 60), legend=False)
    lo_, hi_ = min(0, chg["Change (pp)"].min()), max(0, chg["Change (pp)"].max())
    pad_ = max(hi_ - lo_, 0.5) * 0.35
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0", zeroline=True, zerolinecolor="#000", ticksuffix=" pp",
                     range=[lo_ - pad_, hi_ + pad_])
    fig.update_yaxes(showgrid=False, ticks="")
    show_fig(fig, f"Biggest shifts in disbursement market share, {p0}→{p1}",
             f"Top {top_n} by absolute change, percentage points")

    l, r = st.columns([1, 1.2], gap="medium")
    with l:
        td = BANK.pivot_table(index="Year", columns="Bank Type", values=DISB, aggfunc="sum")
        s0, s1 = td.loc[p0].round(1), td.loc[p1].round(1)
        tg = pd.DataFrame({"Bank type": td.columns})
        if p1 > p0:
            tg[f"{p0} (PKR Bn)"] = s0.values
        tg[f"{p1} (PKR Bn)"] = s1.values
        tg["CAGR (%)"] = [round(cagr(a_, b_, p1 - p0), 1) if a_ > 0 else None
                                     for a_, b_ in zip(s0.values, s1.values)]  # notebook cell 28
        with st.container(border=True):
            st.markdown(f"<div class='ct'>Growth by bank type</div><div class='cs'>Compound annual growth of "
                        f"disbursement, {p0}–{p1}</div>", unsafe_allow_html=True)
            show_table(tg.sort_values(f"{p1} (PKR Bn)", ascending=False), {
                f"{p0} (PKR Bn)": st.column_config.NumberColumn(format="%.1f"),
                f"{p1} (PKR Bn)": st.column_config.NumberColumn(format="%.1f"),
                "CAGR (%)": st.column_config.NumberColumn(format="%.1f%%"),
            })
    with r:
        if BANK["Segment"].nunique() == 2:
            _, sshare = segment_summary(BANK, p1, p0) if p1 > p0 else segment_summary(BANK, p1, p1)
            sshare = sshare.loc[sshare.index.isin(SEL_YEARS)]
            fig = go.Figure()
            for s_, c_ in [(SEG_COM, "#000"), (SEG_MFB, "#8f8f8f")]:
                fig.add_scatter(x=sshare.index, y=sshare[s_], name=s_, mode="lines+markers+text",
                                line=dict(color=c_, width=2.4), marker=dict(size=7),
                                text=[f"{v:.1f}%" for v in sshare[s_]], textposition="top center",
                                textfont=dict(size=10.5),
                                hovertemplate=f"<b>{s_}</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>")
            style(fig, height=330, ysuffix="%")
            fig.update_yaxes(range=[0, 105])
            fig.update_xaxes(dtick=1)
            show_fig(fig, "Segment share of disbursement", "MFB + Digital vs Commercial / Islamic / Specialized")
        else:
            note("Segment comparison needs both segments in scope. Set the sidebar segment to <b>All banks</b>.")

    # ---------- PENETRATION ----------
    section("Penetration & opportunity", "Metrics as calculated in the notebook")
    note("The dataset contains no deposit, borrower-count, irrigation or land-tenure fields, so a credit-to-deposit "
         "ratio or a provincial financing gap cannot be calculated without new assumptions. Penetration is shown "
         "through the notebook's own measures: disbursement per farm and per acre, agriculture's share of "
         "advances, and the provincial Demand Index and DRB Opportunity Score.")
    c = st.columns(4, gap="small")
    with c[0]:
        kpi("Disbursement per farm", f_pkr(dpf_y), f"{year} · {f_cnt(farms_y)} farms", dark=True)
    with c[1]:
        kpi("Disbursement per acre", f_pkr(dpa), f"{year} · {f_cnt(total_acres)} cultivated acres")
    with c[2]:
        kpi("Agri share of total advances", f_pct(cur["Agri Share of Total Advances (%)"]), f"Gross basis · {year}")
    with c[3]:
        hi = PROV_Y[PROV_Y["DRB Opportunity Level"] == "High"]["Province"].tolist()
        kpi("High-opportunity provinces", str(len(hi)), ", ".join(hi) if hi else "None in the High band")

    l, r = st.columns(2, gap="medium")
    with l:
        yrs = [y for y in YEARS if y in SEL_YEARS]
        dpf = []
        for y in yrs:
            fy = PROV_ALL[PROV_ALL["Year"] == y][FARMS].sum()
            dpf.append(PROV_ALL[PROV_ALL["Year"] == y][DPF].iloc[0] if not FILTERED else M.loc[y, DISB] * 1e9 / fy)
        fig = go.Figure(go.Bar(x=yrs, y=dpf, marker_color="#000", text=[f"{v / 1000:,.0f}k" for v in dpf],
                               textposition="outside", textfont=dict(size=11),
                               hovertemplate="%{x}: PKR %{y:,.0f} per farm<extra></extra>"))
        style(fig, height=340, legend=False, ytitle="PKR per farm")
        fig.update_xaxes(dtick=1)
        show_fig(fig, "Credit disbursement per farm", "In-scope disbursement ÷ estimated farms, PKR")
    with r:
        d = PROV_Y.sort_values("DRB Rank")
        fig = go.Figure()
        fig.add_bar(x=d["Province"], y=d["Demand Index"], name="Demand index", marker_color="#a6a6a6",
                    text=[f"{v:.1f}" for v in d["Demand Index"]], textposition="outside",
                    hovertemplate="<b>%{x}</b><br>Demand index: %{y:.1f}<extra></extra>")
        fig.add_bar(x=d["Province"], y=d["DRB Opportunity Score"], name="DRB opportunity score", marker_color="#000",
                    text=[f"{v:.1f}" for v in d["DRB Opportunity Score"]], textposition="outside",
                    hovertemplate="<b>%{x}</b><br>DRB score: %{y:.1f}<extra></extra>")
        style(fig, height=340)
        fig.update_layout(barmode="group")
        fig.update_yaxes(range=[0, 100])
        show_fig(fig, f"Demand index vs DRB opportunity score, {year}",
                 "Demand index weights farms, employees, area and crop output; DRB score favours small farms")

    # ---------- RANKINGS ----------
    section("Rankings", f"Top {top_n} · {year} unless stated")
    bc = BANK[BANK["Year"].isin([p0, p1])].pivot_table(index="Bank", columns="Year", values=DISB)
    bank_cagr = pd.DataFrame({"Bank": bc.index})
    if p1 > p0:
        bank_cagr[f"Disbursement {p0} (PKR Bn)"] = bc[p0].values
    bank_cagr[f"Disbursement {p1} (PKR Bn)"] = bc[p1].values
    bank_cagr[f"CAGR {p0}–{p1} (%)"] = [round(cagr(a_, b_, p1 - p0), 1)
                                        for a_, b_ in zip(bc[p0].values, bc[p1].values)]
    bank_cagr = bank_cagr.dropna(subset=[f"CAGR {p0}–{p1} (%)"]).sort_values(f"CAGR {p0}–{p1} (%)", ascending=False)

    tabs = st.tabs(["Credit disbursement", "Gross advances", "Disbursement share", "Gross advances share",
                    "YoY growth", f"CAGR {p0}–{p1}"])
    specs = [(DISB, ",.2f", ""), (GROSS, ",.2f", ""), (DSHARE, ".2f", "%"), (GSHARE, ".2f", "%"), (DGROW, ".2f", "%")]
    for tab, (col, fmt, suf) in zip(tabs[:5], specs):
        with tab:
            d = BY.dropna(subset=[col]).sort_values(col, ascending=False).head(top_n)
            l, r = st.columns([1.2, 1], gap="medium")
            with l:
                show_fig(hbar(d, col, "Bank", fmt=fmt, suffix=suf, hover_extra=["Bank Type"]),
                         f"Top {top_n} by {col.replace(' (PKR Bn)', '').replace(' (%)', '').lower()}",
                         "Excludes banks with no prior-year lending" if col == DGROW else "")
            with r:
                t = d[["Bank", "Bank Type", col, DISB, MSHARE]].loc[:, lambda x: ~x.columns.duplicated()]
                t = t.reset_index(drop=True)
                t.insert(0, "Rank", range(1, len(t) + 1))
                show_table(t, TABLE_CFG)
    with tabs[5]:
        d = bank_cagr.head(top_n)
        l, r = st.columns([1.2, 1], gap="medium")
        with l:
            show_fig(hbar(d, f"CAGR {p0}–{p1} (%)", "Bank", fmt=".1f", suffix="%"),
                     f"Top {top_n} by disbursement CAGR, {p0}–{p1}",
                     "Notebook CAGR formula; banks with zero lending at the start are excluded")
        with r:
            show_table(d.reset_index(drop=True), {
                f"Disbursement {p0} (PKR Bn)": st.column_config.NumberColumn(format="%.2f"),
                f"Disbursement {p1} (PKR Bn)": st.column_config.NumberColumn(format="%.2f"),
                f"CAGR {p0}–{p1} (%)": st.column_config.NumberColumn(format="%.1f%%"),
            })

    # ---------- INSIGHTS ----------
    section("Management insights", "Generated from the filtered data")
    insights(trends_insights())


# ════════════════════════════════════════════════════════════════════════════
# PDF REPORT  (ReportLab — same filtered data and calculations as the dashboard)
# ════════════════════════════════════════════════════════════════════════════
def build_pdf_report() -> bytes:
    import io
    import re
    from datetime import date
    from reportlab.graphics.charts.barcharts import HorizontalBarChart, VerticalBarChart
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (CondPageBreak, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                    Table, TableStyle)

    BLACK, WHITE = colors.black, colors.white
    G1, G2, G3, G4 = (colors.HexColor(h) for h in ("#3a3a3a", "#6b6b6b", "#b5b5b5", "#f3f3f3"))
    LINE = colors.HexColor("#dcdcdc")
    W_PAGE, H_PAGE = A4
    MARGIN = 16 * mm
    CW = W_PAGE - 2 * MARGIN  # content width

    def clean(t):
        """Built-in PDF fonts lack some symbols: swap them for plain equivalents."""
        t = str(t)
        for a, b in {"▲": "+", "▼": "-", "→": " to ", "≥": ">=", "≤": "<=", "−": "-", "÷": "/"}.items():
            t = t.replace(a, b)
        return t

    def plain(t):
        return re.sub(r"<[^>]+>", "", clean(t))

    S = {
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=13, textColor=G1),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=7.5, leading=10, textColor=G2),
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=BLACK,
                             spaceBefore=4, spaceAfter=2),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=BLACK,
                             spaceBefore=10, spaceAfter=4),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=7.3, leading=9, textColor=G1),
        "cellr": ParagraphStyle("cellr", fontName="Helvetica", fontSize=7.3, leading=9, textColor=G1,
                                alignment=TA_RIGHT),
        "head": ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=7.3, leading=9, textColor=WHITE),
        "headr": ParagraphStyle("headr", fontName="Helvetica-Bold", fontSize=7.3, leading=9, textColor=WHITE,
                                alignment=TA_RIGHT),
        "kl": ParagraphStyle("kl", fontName="Helvetica", fontSize=7.3, leading=9, textColor=G2),
        "kv": ParagraphStyle("kv", fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=BLACK),
        "kvs": ParagraphStyle("kvs", fontName="Helvetica-Bold", fontSize=10, leading=12.5, textColor=BLACK),
        "kd": ParagraphStyle("kd", fontName="Helvetica", fontSize=7.3, leading=9.5, textColor=G2),
    }

    def P(t, st_="body"):
        return Paragraph(clean(t), S[st_])

    def section_title(t, sub=""):
        tbl = Table([[P(t, "h1"), P(sub, "small")]], colWidths=[CW * 0.62, CW * 0.38])
        tbl.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 1.5, BLACK), ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                 ("ALIGN", (1, 0), (1, 0), "RIGHT"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        return [tbl, Spacer(1, 8)]

    def kpi_grid(items):
        """items: list of (label, value, foot, small_value?) — 4 per row, first card dark."""
        rows, cw = [], CW / 4
        for i in range(0, len(items), 4):
            row = []
            for j, (lab, val, foot, sm) in enumerate(items[i:i + 4]):
                dark = (i == 0 and j == 0)
                lst = ParagraphStyle("x", parent=S["kl"], textColor=G3 if dark else G2)
                vst = ParagraphStyle("y", parent=S["kvs" if sm else "kv"], textColor=WHITE if dark else BLACK)
                dst = ParagraphStyle("z", parent=S["kd"], textColor=G3 if dark else G2)
                row.append([Paragraph(clean(lab), lst), Spacer(1, 3), Paragraph(clean(val), vst),
                            Spacer(1, 2), Paragraph(plain(foot), dst)])
            rows.append(row)
        tbl = Table(rows, colWidths=[cw] * 4)
        ts = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOX", (0, 0), (-1, -1), 0, WHITE),
              ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
              ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
              ("BACKGROUND", (0, 0), (0, 0), BLACK)]
        for r in range(len(rows)):
            ts += [("LINEABOVE", (0, r), (-1, r), 2, BLACK), ("LINEBELOW", (0, r), (-1, r), 0.5, LINE)]
            for c in range(1, 4):
                ts.append(("LINEBEFORE", (c, r), (c, r), 6, WHITE))
        tbl.setStyle(TableStyle(ts))
        return tbl

    def data_table(df, widths, right_cols=(), fmt=None):
        fmt = fmt or {}
        cols = list(df.columns)
        head = [Paragraph(clean(c), S["headr" if c in right_cols else "head"]) for c in cols]
        body = []
        for _, r in df.iterrows():
            row = []
            for c in cols:
                v = r[c]
                txt = "—" if (not isinstance(v, str) and pd.isna(v)) else (fmt[c](v) if c in fmt else str(v))
                row.append(Paragraph(clean(txt), S["cellr" if c in right_cols else "cell"]))
            body.append(row)
        tbl = Table([head] + body, colWidths=[w * CW for w in widths], repeatRows=1)
        ts = [("BACKGROUND", (0, 0), (-1, 0), BLACK), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("TOPPADDING", (0, 0), (-1, -1), 3.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
              ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
              ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE)]
        for i in range(1, len(body) + 1):
            if i % 2 == 0:
                ts.append(("BACKGROUND", (0, i), (-1, i), G4))
        tbl.setStyle(TableStyle(ts))
        return tbl

    def insight_block(items):
        rows = [[Paragraph(clean(t), S["body"])] for t in items]
        tbl = Table(rows, colWidths=[CW])
        ts = [("BACKGROUND", (0, 0), (-1, -1), G4), ("LINEBEFORE", (0, 0), (0, -1), 2.5, BLACK),
              ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
              ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]
        for i in range(len(rows) - 1):
            ts.append(("LINEBELOW", (0, i), (-1, i), 4, WHITE))
        tbl.setStyle(TableStyle(ts))
        return tbl

    def note_block(t):
        tbl = Table([[P(t, "small")]], colWidths=[CW])
        tbl.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, LINE), ("BACKGROUND", (0, 0), (-1, -1), G4),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        return tbl

    def legend(d, names, fills, y):
        x = 0
        for n, f in zip(names, fills):
            d.add(Rect(x, y, 7, 7, fillColor=f, strokeColor=None))
            d.add(String(x + 10, y + 0.5, n, fontName="Helvetica", fontSize=7, fillColor=G1))
            x += 14 + len(n) * 3.7

    def vbars(categories, series, names, fills, h=175, fmt="%.0f", suffix=""):
        d = Drawing(CW, h)
        bc = VerticalBarChart()
        bc.x, bc.y, bc.width, bc.height = 34, 18, CW - 40, h - 42
        bc.data = [list(map(float, s_)) for s_ in series]
        allv = [v for s_ in bc.data for v in s_]
        lo, hi = min(0, min(allv)), max(0, max(allv))
        bc.valueAxis.valueMin = lo * 1.3 if lo < 0 else 0
        bc.valueAxis.valueMax = hi * 1.18 if hi > 0 else 1
        bc.categoryAxis.categoryNames = [str(c) for c in categories]
        bc.categoryAxis.labels.fontName = "Helvetica"
        bc.categoryAxis.labels.fontSize = 7.5
        bc.categoryAxis.strokeColor = G3
        bc.categoryAxis.visibleTicks = 0
        bc.categoryAxis.labelAxisMode = "low"
        bc.valueAxis.labels.fontName = "Helvetica"
        bc.valueAxis.labels.fontSize = 7
        bc.valueAxis.labels.fillColor = G2
        bc.valueAxis.labelTextFormat = lambda v: f"{v:,.0f}{suffix}"
        bc.valueAxis.strokeColor = None
        bc.valueAxis.visibleGrid = 1
        bc.valueAxis.gridStrokeColor = colors.HexColor("#ececec")
        bc.valueAxis.gridStrokeWidth = 0.5
        bc.barSpacing, bc.groupSpacing = 1.5, 10
        bc.barLabelFormat = lambda v: (fmt % v) + suffix
        bc.barLabels.fontName = "Helvetica"
        bc.barLabels.fontSize = 6.5
        bc.barLabels.fillColor = G1
        bc.barLabels.nudge = 6
        for i, f in enumerate(fills):
            bc.bars[i].fillColor = f
            bc.bars[i].strokeColor = None
        d.add(bc)
        if len(names) > 1:
            legend(d, names, fills, h - 10)
        return d

    def hbars(labels, values, h=None, fmt="%.2f", suffix="", fills=None, label_w=150):
        n = len(values)
        h = h or max(110, 17 * n + 30)
        d = Drawing(CW, h)
        bc = HorizontalBarChart()
        bc.x, bc.y, bc.width, bc.height = label_w, 8, CW - label_w - 50, h - 16
        bc.data = [[float(v) for v in values[::-1]]]
        bc.categoryAxis.categoryNames = [str(l)[:40] for l in labels[::-1]]
        bc.categoryAxis.labels.fontName = "Helvetica"
        bc.categoryAxis.labels.fontSize = 7.3
        bc.categoryAxis.labels.fillColor = G1
        bc.categoryAxis.strokeColor = G3
        bc.categoryAxis.visibleTicks = 0
        bc.valueAxis.visible = 0
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(max(values), 1e-9) * 1.12
        bc.barLabelFormat = lambda v: (fmt % v) + suffix
        bc.barLabels.fontName = "Helvetica"
        bc.barLabels.fontSize = 7
        bc.barLabels.nudge = 14
        bc.barSpacing = 0
        bc.bars[0].strokeColor = None
        bc.bars[0].fillColor = BLACK
        if fills:
            for i, f in enumerate(fills[::-1]):
                bc.bars[(0, i)].fillColor = f
        d.add(bc)
        return d

    def chart_block(title, sub, drawing):
        return KeepTogether([P(title, "h2"), P(sub, "small"), Spacer(1, 4), drawing, Spacer(1, 6)])

    # ── Header / footer on every page ────────────────────────────────────────
    gen = date.today().strftime("%d %B %Y")

    def on_page(c, doc):
        c.saveState()
        if doc.page == 1:
            c.setFillColor(BLACK)
            c.rect(0, H_PAGE - 36 * mm, W_PAGE, 36 * mm, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 21)
            c.drawString(MARGIN, H_PAGE - 15 * mm, "Agricultural Lending in Pakistan")
            c.setFont("Helvetica", 9.5)
            c.setFillColor(colors.HexColor("#bdbdbd"))
            c.drawString(MARGIN, H_PAGE - 21.5 * mm, "Management report: banking and agricultural finance intelligence")
            c.setFont("Helvetica", 8.5)
            c.setFillColor(WHITE)
            c.drawString(MARGIN, H_PAGE - 29 * mm, clean(f"Reporting year {year}   |   Trend period {p0}-{p1}   |   "
                                                         f"Scope: {scope_txt}")[:120])
        else:
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(BLACK)
            c.drawString(MARGIN, H_PAGE - 11 * mm, "Agricultural Lending in Pakistan")
            c.setFont("Helvetica", 8)
            c.setFillColor(G2)
            c.drawRightString(W_PAGE - MARGIN, H_PAGE - 11 * mm, f"Reporting year {year}  |  Trend period {p0}-{p1}")
            c.setStrokeColor(BLACK)
            c.setLineWidth(0.8)
            c.line(MARGIN, H_PAGE - 13 * mm, W_PAGE - MARGIN, H_PAGE - 13 * mm)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(MARGIN, 12 * mm, W_PAGE - MARGIN, 12 * mm)
        c.setFont("Helvetica", 7)
        c.setFillColor(G2)
        c.drawString(MARGIN, 8 * mm, f"Generated {gen}  |  Figures in PKR billions unless stated  |  "
                                     f"Calculations follow Agri-data_preprocessing.ipynb")
        c.drawRightString(W_PAGE - MARGIN, 8 * mm, f"Page {doc.page}")
        c.restoreState()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=20 * mm, bottomMargin=17 * mm,
                            title="Agricultural Lending in Pakistan — Management Report",
                            author="Agricultural Lending Dashboard")
    E = [Spacer(1, 22 * mm)]

    # ═════════ 1. EXECUTIVE SUMMARY ═════════
    yoy_d = cur["Disbursement YoY (%)"] if prev_year else np.nan
    yoy_g = cur["Gross Advances YoY (%)"] if prev_year else np.nan
    share = cur["Agri Share of Total Advances (%)"]
    share_chg = share - M.loc[prev_year, "Agri Share of Total Advances (%)"] if prev_year else np.nan
    c_disb = cagr(M.loc[p0, DISB], M.loc[p1, DISB], p1 - p0)
    c_ta = cagr(M.loc[p0, TA], M.loc[p1, TA], p1 - p0)
    ref = f"vs {prev_year}" if prev_year else ""
    top = BY.sort_values(DISB, ascending=False).head(1)
    tp = PROV_Y.sort_values("DRB Rank").head(1)
    farms_prev = PROV_ALL[PROV_ALL["Year"] == prev_year][FARMS].sum() if prev_year else np.nan

    def dtxt(v, unit="%"):
        if v is None or pd.isna(v):
            return "No prior-year comparison"
        return f"{'+' if v >= 0 else '-'}{abs(v):,.2f}{'%' if unit == '%' else ' pp'} {ref}"

    items = [
        ("Agricultural credit disbursement", f_bn(cur[DISB]), dtxt(yoy_d), False),
        ("Agricultural gross advances", f_bn(cur[GROSS]), dtxt(yoy_g), False),
        ("Agri share of total advances", f_pct(share), dtxt(share_chg, "pp"), False),
        (f"Disbursement CAGR {p0}-{p1}", f_pct(c_disb) if p1 > p0 else "—",
         f"Total advances CAGR {f_pct(c_ta)}" if p1 > p0 else "Single-year period", False),
    ]
    if len(top):
        r = top.iloc[0]
        items.append(("Top agricultural lender", r["Bank"], f"{f_bn(r[DISB])} | {f_pct(r[MSHARE])} market share", True))
    if len(tp):
        r = tp.iloc[0]
        items.append(("Top province (DRB opportunity)", r["Province"],
                      f"Score {r['DRB Opportunity Score']:.1f} | {r['DRB Opportunity Level']} | "
                      f"Demand rank {int(r['Demand Rank'])}", True))
    items.append(("Number of farms (est.)", f_cnt(farms_y),
                  dtxt((farms_y / farms_prev - 1) * 100 if prev_year and farms_prev else np.nan), False))
    items.append(("Disbursement per farm", f_pkr(dpf_y), f"{year} | all provinces", False))

    E += section_title("Executive summary", f"Key figures, {year}")
    E += [kpi_grid(items), Spacer(1, 6)]

    m = MARKET[MARKET["Year"].isin(SEL_YEARS)]
    E.append(chart_block("Agricultural credit disbursement vs gross advances",
                         "PKR Bn by year: new lending (black) vs outstanding agricultural book (grey)",
                         vbars(m["Year"].tolist(), [m[DISB].tolist(), m[GROSS].tolist()],
                               ["Credit disbursement", "Gross advances (outstanding)"], [BLACK, G3], h=180)))
    E.append(KeepTogether([P("Management insights", "h2"), insight_block(overview_insights(c_disb, c_ta))]))

    # ═════════ 2. BANK PERFORMANCE ═════════
    E += [PageBreak()] + section_title("Bank performance", f"{year} | {BY['Bank'].nunique()} banks in scope")
    top10 = BY.sort_values(DISB, ascending=False).head(10)
    E.append(chart_block(f"Top 10 agricultural lenders, {year}", "Credit disbursement, PKR Bn",
                         hbars(top10["Bank"].tolist(), top10[DISB].tolist(), label_w=165)))

    rk = BY.sort_values(DISB, ascending=False).head(15)[
        ["Bank", "Bank Type", DISB, GROSS, MSHARE, DSHARE, GSHARE, DGROW]].reset_index(drop=True)
    rk.insert(0, "#", range(1, len(rk) + 1))
    rk.columns = ["#", "Bank", "Bank type", "Disb.", "Gross adv.", "Mkt share",
                  "Disb. share", "Gross share", "Disb. YoY"]
    two = lambda v: f"{v:,.2f}"
    pc = lambda v: f"{v:,.2f}%"
    E.append(KeepTogether([
        P(f"Ranking: top 15 by agricultural credit disbursement, {year}", "h2"),
        P("PKR Bn; shares are of each bank's total advances, market share is of industry disbursement", "small"),
        Spacer(1, 4),
        data_table(rk, [0.04, 0.27, 0.17, 0.09, 0.09, 0.08, 0.09, 0.09, 0.08],
                   right_cols=rk.columns[3:].tolist() + ["#"],
                   fmt={"Disb.": two, "Gross adv.": two, "Mkt share": pc, "Disb. share": pc,
                        "Gross share": pc, "Disb. YoY": pc}),
    ]))

    if BANK["Segment"].nunique() == 2 and year > p0:
        ss, _ = segment_summary(BANK, year, p0)
        ss.columns = ["Segment", f"Disbursement {year}", f"Share {year}", f"CAGR {p0}-{year}", "Banks",
                      "Avg per bank"]
        E.append(KeepTogether([
            P("Segment comparison: MFB + Digital vs rest of market", "h2"),
            P("Notebook segment analysis; PKR Bn", "small"), Spacer(1, 4),
            data_table(ss, [0.34, 0.15, 0.12, 0.13, 0.1, 0.16], right_cols=ss.columns[1:].tolist(),
                       fmt={f"Share {year}": pc, f"CAGR {p0}-{year}": lambda v: f"{v:.1f}%",
                            "Banks": lambda v: f"{int(v)}"}),
        ]))

    ts_ = type_share_table(BANK)
    tg = bank_type_growth()
    tg[f"Share {year} (%)"] = tg["Bank type"].map(ts_.loc[year]) if year in ts_.index else np.nan
    tg.columns = [c.replace(" (PKR Bn)", "").replace(" (%)", "") for c in tg.columns]
    E.append(KeepTogether([
        P("Bank types: disbursement, growth and share", "h2"),
        P(f"Disbursement in PKR Bn; CAGR over {p0}-{p1}; share of in-scope disbursement in {year}", "small"),
        Spacer(1, 4),
        data_table(tg, [0.36] + [0.64 / (len(tg.columns) - 1)] * (len(tg.columns) - 1),
                   right_cols=tg.columns[1:].tolist(),
                   fmt={c: (lambda v: f"{v:.1f}%") if c.startswith(("CAGR", "Share")) else (lambda v: f"{v:,.1f}")
                        for c in tg.columns[1:]}),
    ]))

    # ═════════ 3. REGIONAL & AGRICULTURAL PROFILE ═════════
    E += [CondPageBreak(110 * mm)] + section_title("Regional and agricultural profile", f"{year} | 4 provinces")
    E.append(note_block("The source data does not split bank lending by province, so credit is reported at national "
                        "level. Provinces are compared on the agricultural demand base used by the notebook's "
                        "Demand Index and DRB Opportunity Score."))
    E.append(Spacer(1, 4))
    pv = PROV_Y.sort_values("DRB Rank")
    pt = pv[["Province", FARMS, EMP, FSIZE, EPF, GDP, EMPSH, AREA, "Demand Index", "DRB Opportunity Score",
             "DRB Opportunity Level"]].copy()
    pt.columns = ["Province", "Farms", "Employees", "Avg farm (ac)", "Emp/ farm", "Agri % GDP", "Agri % emp.",
                  "Cultivated (ac)", "Demand idx", "DRB score", "Level"]
    big = lambda v: f"{v:,.0f}"
    E.append(KeepTogether([
        P("Provincial profile", "h2"), Spacer(1, 2),
        data_table(pt, [0.15, 0.09, 0.1, 0.08, 0.07, 0.08, 0.08, 0.1, 0.08, 0.08, 0.09],
                   right_cols=pt.columns[1:-1].tolist(),
                   fmt={"Farms": big, "Employees": big, "Cultivated (ac)": big, "Avg farm (ac)": two,
                        "Emp/ farm": two, "Agri % GDP": pc, "Agri % emp.": pc,
                        "Demand idx": lambda v: f"{v:.1f}", "DRB score": lambda v: f"{v:.1f}"}),
    ]))
    shade = {"High": BLACK, "Medium": colors.HexColor("#7a7a7a"), "Low": G3}
    E.append(chart_block(f"DRB opportunity score by province, {year}",
                         "Six equally weighted, max-normalised factors (0-100). High >= 70, Medium 40-70, Low < 40",
                         hbars(pv["Province"].tolist(), pv["DRB Opportunity Score"].tolist(), fmt="%.1f",
                               fills=[shade.get(l, G3) for l in pv["DRB Opportunity Level"]], label_w=110)))
    idx = drb_factor_indices(PROV_Y).loc[pv["Province"]].reset_index()
    idx.columns = ["Province", "Employees", "Agri % GDP", "Agri % emp.", "Farms", "Small farm size", "Cultivated"]
    E.append(KeepTogether([
        P("DRB factor indices", "h2"), P("Best province on each factor = 100", "small"), Spacer(1, 4),
        data_table(idx, [0.22] + [0.13] * 6, right_cols=idx.columns[1:].tolist(),
                   fmt={c: (lambda v: f"{v:.1f}") for c in idx.columns[1:]}),
    ]))
    top3 = (CROP.sort_values(AREA, ascending=False).groupby("Province").head(3)
            .sort_values(["Province", AREA], ascending=[True, False]))[["Province", "Crop", AREA,
                                                                        "Province Crop Share (%)"]]
    top3.columns = ["Province", "Crop", "Cultivated area (acres)", "Share of province area"]
    E.append(KeepTogether([
        P("Top 3 crops by province", "h2"), P("Cultivated area snapshot (no year dimension)", "small"),
        Spacer(1, 4),
        data_table(top3, [0.3, 0.25, 0.25, 0.2], right_cols=["Cultivated area (acres)", "Share of province area"],
                   fmt={"Cultivated area (acres)": big, "Share of province area": pc}),
    ]))

    # ═════════ 4. TRENDS, PENETRATION & INSIGHTS ═════════
    E += [CondPageBreak(110 * mm)] + section_title("Trends, penetration and insights", f"{p0}-{p1}")
    mt = m[["Year", TA, DISB, GROSS, "Disbursement YoY (%)", "Gross Advances YoY (%)",
            "Agri Share of Total Advances (%)"]].copy()
    dpf_list = []
    for y in mt["Year"]:
        fy = PROV_ALL[PROV_ALL["Year"] == y][FARMS].sum()
        dpf_list.append(PROV_ALL[PROV_ALL["Year"] == y][DPF].iloc[0] if not FILTERED else M.loc[y, DISB] * 1e9 / fy)
    mt["Per farm (PKR)"] = dpf_list
    mt.columns = ["Year", "Total advances", "Disbursement", "Gross adv.", "Disb. YoY", "Gross YoY",
                  "Agri share", "Per farm (PKR)"]
    E.append(KeepTogether([
        P("Market trend", "h2"), P("PKR Bn; agri share = gross agricultural advances / total advances", "small"),
        Spacer(1, 4),
        data_table(mt, [0.08, 0.14, 0.13, 0.13, 0.12, 0.12, 0.12, 0.16], right_cols=mt.columns.tolist(),
                   fmt={"Year": lambda v: f"{int(v)}", "Total advances": two, "Disbursement": two,
                        "Gross adv.": two, "Disb. YoY": pc, "Gross YoY": pc, "Agri share": pc,
                        "Per farm (PKR)": big}),
    ]))
    g = m.dropna(subset=["Disbursement YoY (%)"])
    if len(g):
        E.append(chart_block("Year-on-year growth", "Credit disbursement (black) vs gross advances (grey), %",
                             vbars(g["Year"].tolist(), [g["Disbursement YoY (%)"].tolist(),
                                                        g["Gross Advances YoY (%)"].tolist()],
                                   ["Credit disbursement", "Gross advances"], [BLACK, G3], h=165,
                                   fmt="%.1f", suffix="%")))

    E += [Spacer(1, 2), kpi_grid([
        ("Disbursement per farm", f_pkr(dpf_y), f"{year} | {f_cnt(farms_y)} farms", False),
        ("Disbursement per acre", f_pkr(disbursement_per_acre()), f"{year} | {f_cnt(CROP[AREA].sum())} acres", False),
        ("Agri share of total advances", f_pct(share), f"Gross basis | {year}", False),
        ("High-opportunity provinces",
         str(int((PROV_Y["DRB Opportunity Level"] == "High").sum())),
         ", ".join(PROV_Y[PROV_Y["DRB Opportunity Level"] == "High"]["Province"]) or "None", False),
    ]), Spacer(1, 4)]

    if p1 > p0:
        bcg = bank_cagr_table().head(10).reset_index(drop=True)
        bcg.columns = ["Bank", f"Disb. {p0}", f"Disb. {p1}", "CAGR"]
        sh = share_shift().head(10)
        sh.columns = ["Bank", "Change (pp)"]
        E.append(KeepTogether([
            P(f"Top 10 banks by disbursement CAGR, {p0}-{p1}", "h2"),
            P("Banks with zero lending at the start of the period are excluded", "small"), Spacer(1, 4),
            data_table(bcg, [0.52, 0.16, 0.16, 0.16], right_cols=bcg.columns[1:].tolist(),
                       fmt={f"Disb. {p0}": two, f"Disb. {p1}": two, "CAGR": lambda v: f"{v:.1f}%"}),
        ]))
        E.append(KeepTogether([
            P(f"Largest shifts in disbursement market share, {p0}-{p1}", "h2"),
            P("Top 10 by absolute change, percentage points", "small"), Spacer(1, 4),
            data_table(sh, [0.75, 0.25], right_cols=["Change (pp)"], fmt={"Change (pp)": lambda v: f"{v:+.2f} pp"}),
        ]))

    E.append(KeepTogether([P("Management insights: trends and opportunity", "h2"), insight_block(trends_insights())]))

    E.append(KeepTogether([
        P("Methodology and data notes", "h2"),
        P("Agri disbursement share = disbursement / total advances. Agri gross advances share = gross agricultural "
          "advances / total advances. Market share = bank disbursement / industry disbursement in the year. "
          "Growth = year-on-year percentage change; CAGR = (end / start)^(1 / years) - 1. Demand Index = 0.30 x farms "
          "share + 0.20 x employees share + 0.25 x cultivated area share + 0.25 x crop output share. DRB Opportunity "
          "Score = equal-weighted average of six max-normalised factors (smaller farms score higher).", "small"),
        Spacer(1, 3),
        P("The dataset has no deposit, borrower-count, irrigation or land-tenure fields, so a credit-to-deposit "
          "ratio, borrower KPIs or a provincial financing gap are not reported. Crop cultivated area is a single "
          "snapshot. This report reflects the dashboard filters active when it was downloaded.", "small"),
    ]))

    doc.build(E, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()


@st.cache_data(show_spinner=False)
def cached_pdf(_key: tuple) -> bytes:
    """Cache one PDF per filter combination (year, period, bank types)."""
    return build_pdf_report()


REPORT_PDF = "Agriculture_lending_report.pdf"   # keep this file in the same folder as app.py
NOTEBOOK_FILE = "Agri-data_preprocessing.ipynb"  # keep this file in the same folder as app.py


def notebook_download_button():
    """Download button for the data processing notebook (Agri-data_preprocessing.ipynb)."""
    nb_path = _find(NOTEBOOK_FILE)
    if nb_path is None:                                    # fall back to any notebook in the app folder
        nbs = sorted(Path(__file__).resolve().parent.glob("*.ipynb"))
        nb_path = nbs[0] if nbs else None
    if nb_path is None:
        st.button("Download data processing file (.ipynb)", key="nb_btn", type="primary", disabled=True,
                  help=f"Place {NOTEBOOK_FILE} in the same folder as app.py")
        return
    st.download_button(
        "Download data processing file (.ipynb)",
        data=nb_path.read_bytes(),
        file_name=NOTEBOOK_FILE,
        mime="application/x-ipynb+json",
        key="nb_btn",
        type="primary",
    )




def pdf_download_button():
    """Download button for the written report (Agriculture_lending_report.pdf)."""
    pdf_path = _find(REPORT_PDF)
    if pdf_path is None:                                   # fall back to any PDF in the app folder
        pdfs = sorted(Path(__file__).resolve().parent.glob("*.pdf"))
        pdf_path = pdfs[0] if pdfs else None
    if pdf_path is None:
        st.button("Download PDF report", key="pdf_btn", type="primary", disabled=True,
                  help=f"Place {REPORT_PDF} in the same folder as app.py")
        return
    st.download_button(
        "Download PDF report",
        data=pdf_path.read_bytes(),
        file_name=REPORT_PDF,
        mime="application/pdf",
        key="pdf_btn",
        type="primary",
    )


# ════════════════════════════════════════════════════════════════════════════
# ROUTER
# ════════════════════════════════════════════════════════════════════════════
if page == PAGES[0]:
    page_overview()
elif page == PAGES[1]:
    page_banks()
elif page == PAGES[2]:
    page_regional()
else:
    page_trends()

st.markdown(
    "<div style='margin-top:36px;padding-top:12px;border-top:1px solid #e2e2e2;display:flex;"
    "justify-content:space-between;align-items:flex-start;gap:24px;flex-wrap:wrap'>"
    "<div style='font-size:11.5px;color:#8a8a8a'>"
    "Agricultural Lending in Pakistan · figures in PKR billions unless stated · calculations follow "
    "Agri-data_preprocessing.ipynb"
    f"<div style='margin-top:6px;font-size:12.5px;color:#1a1a1a;font-weight:500'>{PREPARED_BY}</div></div>"
    f"<div style='font-size:11.5px;color:#8a8a8a;max-width:460px;text-align:right'>{DISCLAIMER}</div></div>",
    unsafe_allow_html=True,
)