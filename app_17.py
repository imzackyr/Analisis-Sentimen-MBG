"""
Dashboard Analisis Sentimen Program MBG (Makan Bergizi Gratis)
"""

import re
import string

import emoji
import joblib
import nltk
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from collections import Counter
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# ==================================================================
# KONFIGURASI HALAMAN
# ==================================================================
st.set_page_config(
    page_title="MBG Sentiment · Skripsi",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🔧 REVISI: sentimen sekarang 2 kategori saja (Positif & Negatif)
SENT_COLORS = {"Positif": "#92d05d", "Negatif": "#f87171"}
SENT_ORDER = ["Positif", "Negatif"]

ACCENT = "#92d05d"      # aksen utama — dipakai konsisten di seluruh dashboard
ACCENT2 = "#d1b06c"     # aksen sekunder — dipakai terbatas untuk highlight khusus
NEUTRAL = "#7a93ab"     # abu-abu netral — pengganti warna dekoratif tambahan
PLATFORM_COLORS = {"Twitter": NEUTRAL, "TikTok": ACCENT}

# ==================================================================
# CSS — TEMA VISUAL (dark forest-green, serif + jakarta sans)
# ==================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

:root {
    /* Palet minimalis, dark theme, 1 aksen utama + 1 aksen sekunder terbatas:
       hijau (--green) = aksen utama, dipakai konsisten di seluruh UI (gizi & pertumbuhan)
       emas (--gold)   = aksen sekunder, dipakai TERBATAS (eyebrow & satu highlight khusus)
       merah (--red)   = warna FUNGSIONAL untuk data Negatif/danger, bukan dekorasi */
    --bg:     #060d18;
    --bg2:    #0a1526;
    --bg3:    #101f38;
    --card:   #152947;
    --border: #2c4568;
    --track:  #223a5c;
    --green:  #92d05d;
    --green-dim: #5fae35;
    --gold:   #d1b06c;
    --muted:  #7a93ab;
    --text:   #eef4fb;
    --text2:  #cdd9e6;
    --red:    #f87171;
}
* { box-sizing: border-box; }
html, body, [class*="css"] { font-family:'Plus Jakarta Sans', sans-serif; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:2px; }
#MainMenu { visibility:hidden; }
footer { visibility:hidden; }
.stDeployButton { display:none; }
[data-testid="stToolbarActions"] { display:none; }
.block-container { padding:1rem 2rem 4rem !important; max-width:1400px; }

/* NAVBAR */
.navbar { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px;
    padding:14px 0 16px; border-bottom:1px solid var(--border); margin-bottom:24px; }
.navbar-brand { display:flex; align-items:center; gap:12px; }
.navbar-logo { width:36px; height:36px; background:linear-gradient(135deg,var(--bg3),var(--green));
    border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; }
.navbar-title { font-family:'Playfair Display',serif; font-size:1.35rem; color:var(--text); letter-spacing:-0.02em; }
.navbar-sub { font-size:0.7rem; color:var(--text2); letter-spacing:0.12em; text-transform:uppercase; font-weight:600; }

/* Nav pindah ke atas: st.radio horizontal didandani jadi pill-tab */
div[data-testid="stRadio"][aria-label="Navigasi"],
div.top-nav div[data-testid="stRadio"] { margin-bottom:0; }
div.top-nav div[role="radiogroup"] { gap:4px; flex-wrap:wrap; row-gap:6px; }
div.top-nav label[data-baseweb="radio"] { background:transparent; border:1px solid transparent;
    border-radius:100px; padding:7px 16px !important; margin:0 !important; cursor:pointer; transition:.18s; }
div.top-nav label[data-baseweb="radio"]:hover { background:rgba(146,208,93,0.08); }
div.top-nav label[data-baseweb="radio"] > div:first-child { display:none; }
div.top-nav label[data-baseweb="radio"] p { font-size:0.82rem !important; font-weight:600; color:var(--text2) !important; margin:0 !important; white-space:nowrap; }
div.top-nav label[data-baseweb="radio"]:has(input:checked) { background:rgba(146,208,93,0.14); border-color:rgba(146,208,93,0.35); }
div.top-nav label[data-baseweb="radio"]:has(input:checked) p { color:var(--green) !important; font-weight:700; }

/* HERO */
.hero { position:relative; background:linear-gradient(135deg,#12396d 0%,#1b4e8a 45%,#0f2747 100%);
    border:1px solid var(--border); border-radius:24px; padding:44px 48px; margin-bottom:28px; overflow:hidden; }
.hero::before { content:''; position:absolute; top:-60px; right:-60px; width:280px; height:280px;
    background:radial-gradient(circle,rgba(146,208,93,0.10) 0%,transparent 70%); }
.hero::after { content:attr(data-emoji); position:absolute; font-size:150px; right:32px; bottom:-16px; opacity:0.06; line-height:1; }
.hero-eyebrow { font-size:0.7rem; font-weight:700; letter-spacing:0.15em; text-transform:uppercase;
    color:var(--gold); margin-bottom:14px; display:flex; align-items:center; gap:8px; }
.hero-eyebrow::before { content:''; width:24px; height:2px; background:var(--gold); border-radius:1px; }
.hero-title { font-family:'Playfair Display',serif; font-size:2.4rem; line-height:1.15;
    letter-spacing:-0.02em; color:var(--text); margin:0 0 14px; max-width:720px; }
.hero-title em { color:var(--green); font-style:italic; }
.hero-sub { font-size:0.95rem; color:var(--text2); line-height:1.7; max-width:620px; margin:0; }

/* STAT STRIP */
.stat-strip { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:36px; }
.stat-item { background:var(--card); border:1px solid var(--border); border-radius:14px;
    padding:18px 20px; position:relative; overflow:hidden; }
.stat-item::before { content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,var(--bar-c,var(--green)),transparent); }
.stat-num { font-family:'Playfair Display',serif; font-size:1.9rem; color:var(--text); line-height:1; margin-bottom:4px; }
.stat-label { font-size:0.74rem; color:var(--text2); font-weight:500; letter-spacing:0.03em; }

/* SECTION HEADER */
.sec { display:flex; align-items:center; gap:12px; margin:8px 0 16px; }
.sec-line { width:3px; height:22px; background:linear-gradient(180deg,var(--green),transparent); border-radius:2px; }
.sec-title { font-family:'Playfair Display',serif; font-size:1.35rem; color:var(--text); letter-spacing:-0.01em; }
.sec-sub { font-size:0.83rem; color:var(--text2); margin:-8px 0 20px 15px; line-height:1.6; }

/* CARD GRID (metodologi) */
.how-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:12px; }
.how-card { background:var(--card); border:1px solid var(--border); border-radius:16px; padding:24px 22px; }
.how-num { font-family:'Playfair Display',serif; font-size:2.6rem; color:var(--green); line-height:1; margin-bottom:10px; letter-spacing:-0.03em; opacity:0.85; }
.how-card h4 { font-size:0.92rem; font-weight:700; color:var(--text); margin:0 0 6px; }
.how-card p { font-size:0.81rem; color:var(--text2); margin:0; line-height:1.6; }

/* INFO / FINDING CARDS */
.info-card { background:var(--bg3); border-radius:14px; padding:18px 22px; border-left:3px solid var(--green); margin:12px 0; }
.info-card.warn { border-left-color:var(--gold); background:rgba(209,176,108,0.06); }
.info-card.danger { border-left-color:var(--red); }
.info-card.neutral { border-left-color:var(--muted); }
.info-card h5 { font-size:0.7rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:var(--green); margin:0 0 8px; }
.info-card.warn h5 { color:var(--gold); }
.info-card.danger h5 { color:var(--red); }
.info-card.neutral h5 { color:var(--muted); }
.info-card p { font-size:0.87rem; color:var(--text2); margin:0; line-height:1.7; }
.info-card p b { color:var(--text); }

/* PROGRESS BARS */
.bar-row { margin-bottom:14px; }
.bar-top { display:flex; justify-content:space-between; font-size:0.82rem; margin-bottom:5px; }
.bar-top .lbl { color:var(--text2); font-weight:500; }
.bar-top .val { font-family:'Playfair Display',serif; color:var(--text); font-weight:700; }
.bar-bg { background:var(--track); border-radius:100px; height:9px; overflow:hidden; }
.bar-fg { height:100%; border-radius:100px; }

/* WORD BARS */
.word-row { display:flex; align-items:center; gap:10px; margin-bottom:8px; }
.word-label { min-width:110px; font-size:0.8rem; color:var(--text2); text-align:right; }
.word-track { flex:1; background:var(--track); border-radius:100px; height:14px; position:relative; overflow:hidden; }
.word-fill { height:100%; border-radius:100px; }
.word-freq { min-width:38px; font-size:0.75rem; color:var(--text2); font-weight:600; }

/* CARD GRID for word panels */
.panel-card { background:var(--card); border:1px solid var(--border); border-radius:16px; padding:22px; margin-bottom:8px; }
.panel-title { font-size:0.78rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:16px; }

hr.div { border:none; border-top:1px solid var(--border); margin:36px 0; }
.footer { text-align:center; color:var(--text2); font-size:0.75rem; padding:24px 0 8px; letter-spacing:0.04em; }

/* SIDEBAR */
section[data-testid="stSidebar"] { background:var(--bg2); border-right:1px solid var(--border); }
section[data-testid="stSidebar"] * { color:var(--text2) !important; font-family:'Plus Jakarta Sans',sans-serif !important; }

.stTabs [data-baseweb="tab"] { font-weight:600; font-size:0.88rem; color:var(--text2); }
.stTabs [aria-selected="true"] { color:var(--green) !important; }

div[data-testid="stDataFrame"] { border:1px solid var(--border); border-radius:12px; overflow:hidden; background:var(--card); }

.how-card, .panel-card, .stat-item, .info-card{transition:.25s;}
.how-card:hover, .panel-card:hover, .stat-item:hover, .info-card:hover{
transform:translateY(-3px);
border-color:var(--green);
box-shadow:0 10px 24px rgba(146,208,93,.15);
}

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# KOMPONEN UI
# ------------------------------------------------------------------
def navbar_brand():
    st.markdown("""
    <div class="navbar-brand" style="padding:14px 0 4px;">
        <div class="navbar-logo">🍱</div>
        <div>
            <div class="navbar-title">MBG Sentiment</div>
            <div class="navbar-sub">Skripsi · Analisis Sentimen Publik</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def top_nav(pages):
    st.markdown('<div class="top-nav">', unsafe_allow_html=True)
    selected = st.radio("Navigasi", pages, horizontal=True, label_visibility="collapsed", key="page_nav")
    st.markdown('</div>', unsafe_allow_html=True)
    return selected


def hero(eyebrow, title_html, subtitle, emoji="🍱"):
    st.markdown(f"""
    <div class="hero" data-emoji="{emoji}">
        <div class="hero-eyebrow">{eyebrow}</div>
        <h1 class="hero-title">{title_html}</h1>
        <p class="hero-sub">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def stat_strip(items):
    # items: list of (num, label, color)
    html = '<div class="stat-strip">'
    for num, label, color in items:
        html += f'''<div class="stat-item" style="--bar-c:{color}">
            <div class="stat-num">{num}</div><div class="stat-label">{label}</div></div>'''
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def sec(title, subtitle=None):
    st.markdown(f'<div class="sec"><div class="sec-line"></div><div class="sec-title">{title}</div></div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="sec-sub">{subtitle}</p>', unsafe_allow_html=True)


def info_card(title, text, variant=""):
    st.markdown(f'<div class="info-card {variant}"><h5>{title}</h5><p>{text}</p></div>', unsafe_allow_html=True)


def pct_bar(label, pct, color):
    st.markdown(f"""
    <div class="bar-row">
        <div class="bar-top"><span class="lbl">{label}</span><span class="val">{pct}%</span></div>
        <div class="bar-bg"><div class="bar-fg" style="width:{pct}%;background:{color}"></div></div>
    </div>""", unsafe_allow_html=True)


def word_bars(pairs, color):
    if not pairs:
        st.caption("Tidak ada data.")
        return
    max_f = max(f for _, f in pairs)
    html = ""
    for word, freq in pairs:
        w = max(6, int(freq / max_f * 100))
        html += f"""<div class="word-row">
            <div class="word-label">{word}</div>
            <div class="word-track"><div class="word-fill" style="width:{w}%;background:{color}"></div></div>
            <div class="word-freq">{freq}</div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)


def themed(fig, height=340):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#aac0d6", size=12),
        margin=dict(t=30, b=20, l=10, r=10),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#aac0d6")),
    )
    fig.update_xaxes(gridcolor="#1c3355", zerolinecolor="#1c3355", color="#aac0d6")
    fig.update_yaxes(gridcolor="#1c3355", zerolinecolor="#1c3355", color="#aac0d6")
    return fig


def footer():
    st.markdown("""
    <hr class="div">
    <div class="footer">
        MBG Sentiment Dashboard &nbsp;·&nbsp; Tugas Akhir / Skripsi &nbsp;·&nbsp;
        Analisis Sentimen Program Makan Bergizi Gratis<br>
        Data: Twitter & TikTok &nbsp;·&nbsp; Model: TF-IDF + Naive Bayes &nbsp;·&nbsp; Labeling: Lexicon-based
    </div>""", unsafe_allow_html=True)


# ==================================================================
# LOAD DATA
# ==================================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/hasil_sentimen.csv")
    df["final_text"] = df["final_text"].fillna("")
    df["text"] = df["text"].fillna("")
    df["dt"] = pd.to_datetime(df["datetime"], errors="coerce", utc=True, format="mixed")
    df["month"] = df["dt"].dt.to_period("M").astype(str)
    return df


@st.cache_data
def load_eval():
    ev = pd.read_csv("data/hasil_evaluasi.csv")
    ev.columns = [c.strip().lstrip("\ufeff") for c in ev.columns]
    return ev


@st.cache_data
def load_cm():
    cm = pd.read_csv("data/confusion_matrix.csv", index_col=0)
    cm.columns = [c.strip() for c in cm.columns]
    cm.index = [c.strip().lstrip("\ufeff") for c in cm.index]
    return cm


df_all = load_data()
eval_df = load_eval()
cm_df = load_cm()
metrics_map = dict(zip(eval_df["Metric"], eval_df["Persentase"]))

# ==================================================================
# 🔧 REVISI: PREPROCESSING & MODEL UNTUK UJI COBA SENTIMEN BARU
# Pipeline di bawah ini DISALIN PERSIS dari notebook (B.12–B.16) supaya
# teks baru diproses dengan cara yang identik dengan data training.
# ==================================================================

# --- B.14 Normalisasi: slang dictionary (identik dengan notebook) ---
SLANG_DICT = {
    # NEGASI
    'g': 'tidak', 'ga': 'tidak', 'gaa': 'tidak', 'gaaa': 'tidak', 'gak': 'tidak',
    'gakkk': 'tidak', 'gk': 'tidak', 'ngga': 'tidak', 'nggaa': 'tidak', 'nggak': 'tidak',
    'nggk': 'tidak', 'ngk': 'tidak', 'tdk': 'tidak',
    'gada': 'tidak ada', 'gadaa': 'tidak ada', 'gaada': 'tidak ada', 'gakada': 'tidak ada',
    'gkada': 'tidak ada', 'nggada': 'tidak ada', 'nggakada': 'tidak ada',
    # KATA HUBUNG
    'yg': 'yang', 'utk': 'untuk', 'dr': 'dari', 'dgn': 'dengan', 'krn': 'karena',
    'tp': 'tapi', 'trs': 'terus', 'trus': 'terus',
    # KATA UMUM
    'udh': 'sudah', 'sdh': 'sudah', 'blm': 'belum', 'jd': 'jadi', 'jg': 'juga',
    'aja': 'saja', 'doang': 'saja', 'bgt': 'banget', 'klu': 'kalau', 'klo': 'kalau',
    'cm': 'cuma', 'cmn': 'cuma', 'org': 'orang', 'sm': 'sama', 'pd': 'pada', 'dlm': 'dalam',
    # BAHASA GAUL
    'gw': 'saya', 'gua': 'saya', 'gue': 'saya', 'sy': 'saya', 'lu': 'kamu', 'loe': 'kamu',
    # KHUSUS MBG
    'mbgnya': 'mbg', 'mbg2': 'mbg', 'mkn': 'makan', 'mknan': 'makanan', 'mknnya': 'makanan',
    'bgizi': 'bergizi', 'bergizii': 'bergizi', 'gizii': 'gizi',
    'ank': 'anak', 'anak2': 'anak', 'anak²': 'anak',
    'sklh': 'sekolah', 'sekolahan': 'sekolah', 'gratisan': 'gratis',
    'stuntingnya': 'stunting', 'pemrintah': 'pemerintah',
}

# --- B.15 Stopword removal: keep_words & custom_stopwords (identik dengan notebook) ---
KEEP_WORDS = {
    'tidak', 'tak', 'bukan', 'belum', 'jangan', 'kurang',
    'tapi', 'namun', 'meski', 'walaupun',
    'sangat', 'banget', 'sekali',
    'mbg', 'makan', 'makanan', 'bergizi', 'gizi', 'gratis', 'program', 'stunting',
    'anak', 'siswa', 'pelajar', 'sekolah',
    'pemerintah', 'presiden', 'prabowo',
    'indonesia',
    'bagus', 'baik', 'hebat', 'mantap', 'berhasil', 'bermanfaat', 'bantu', 'manfaat',
    'puas', 'senang', 'layak', 'sehat',
    'buruk', 'jelek', 'gagal', 'parah', 'rugi', 'kecewa', 'bohong', 'korup', 'korupsi',
    'basi', 'busuk', 'keracunan', 'mubazir', 'mahal', 'telat', 'rusak',
}
CUSTOM_STOPWORDS = {
    'nih', 'sih', 'dong', 'deh', 'lah', 'kok', 'yaa', 'yaaa', 'hehe', 'wkwk', 'wk',
    'wkwkwk', 'kwkwk', 'amp', 'http', 'https', 'com', 'co',
}


@st.cache_resource
def load_nlp_resources():
    """Load model, vectorizer, stemmer, dan stopwords sekali saja (resource berat)."""
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords

    stop_words = set(stopwords.words("indonesian"))
    stop_words.update(CUSTOM_STOPWORDS)
    stop_words = stop_words - KEEP_WORDS

    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    model = joblib.load("data/model.pkl")
    tfidf_vec = joblib.load("data/tfidf.pkl")

    return model, tfidf_vec, stemmer, stop_words


def clean_text(text):
    """B.12 Text Cleaning — identik dengan notebook."""
    text = str(text)
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"\brt\b", "", text)
    text = emoji.replace_emoji(text, replace="")
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_new_text(text, stemmer, stop_words):
    """Pipeline lengkap: cleaning -> tokenizing -> normalisasi -> stopword -> stemming."""
    from nltk.tokenize import word_tokenize

    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    normalized = [SLANG_DICT.get(w, w) for w in tokens]
    filtered = [w for w in normalized if w not in stop_words]
    stemmed = [stemmer.stem(w) for w in filtered]
    return " ".join(stemmed)


def predict_sentiment(text, model, tfidf_vec, stemmer, stop_words):
    final_text = preprocess_new_text(text, stemmer, stop_words)
    if not final_text.strip():
        return None, None, final_text
    vec = tfidf_vec.transform([final_text])
    label = model.predict(vec)[0]
    proba = None
    if hasattr(model, "predict_proba"):
        proba = dict(zip(model.classes_, model.predict_proba(vec)[0]))
    return label, proba, final_text

# ==================================================================
# NAVBAR ATAS — BRAND & NAVIGASI HALAMAN
# ==================================================================
PAGES = [
    "🏠 Ringkasan",
    "📊 Distribusi Sentimen",
    "🔑 Kata Kunci & Topik",
    "🤖 Performa Model",
    "🎯 Bukti: Dukungan Publik MBG",
    "🔍 Jelajah Data",
    "✍️ Uji Coba Sentimen",  # 🔧 REVISI: halaman baru
]

st.markdown('<div class="navbar">', unsafe_allow_html=True)
navbar_brand()
page = top_nav(PAGES)
st.markdown('</div>', unsafe_allow_html=True)

# ==================================================================
# SIDEBAR — FILTER DATA
# ==================================================================
st.sidebar.markdown("### 🍱 MBG Sentiment")
st.sidebar.caption("Dashboard Analisis · Skripsi")
st.sidebar.markdown("---")
st.sidebar.markdown("**Filter Data**")
platform_sel = st.sidebar.multiselect("Platform", options=sorted(df_all["platform"].unique()), default=sorted(df_all["platform"].unique()))
sentimen_sel = st.sidebar.multiselect("Sentimen", options=SENT_ORDER, default=SENT_ORDER)

df = df_all[df_all["platform"].isin(platform_sel) & df_all["sentiment"].isin(sentimen_sel)]

st.sidebar.markdown("---")
st.sidebar.caption(f"Menampilkan **{len(df):,}** dari **{len(df_all):,}** data.")

# ==================================================================
# HELPER ANALISIS
# ==================================================================
def sentiment_pct(frame):
    vc = frame["sentiment"].value_counts()
    vc = vc.reindex(SENT_ORDER).fillna(0)
    pct = (vc / vc.sum() * 100).round(2) if vc.sum() > 0 else vc
    return vc, pct


def top_words(frame, sentiment, n=10):
    text = " ".join(frame[frame["sentiment"] == sentiment]["final_text"]).split()
    return Counter(text).most_common(n)


def keyword_mask(frame, pattern):
    return frame["final_text"].str.contains(pattern, case=False, na=False, regex=True)


# ==================================================================
# PAGE 1 — RINGKASAN
# ==================================================================
if page == "🏠 Ringkasan":
    hero(
        "Analisis Sentimen Publik · Skripsi",
        "Bagaimana Persepsi Publik terhadap Program <em>MBG</em>?",
        f"Dashboard ini menyajikan bukti kuantitatif dari {len(df_all):,} unggahan Twitter dan TikTok "
        "untuk menganalisis sentimen publik terhadap Program Makan Bergizi Gratis (MBG).",
    )

    stat_strip([
        (f"{len(df_all):,}", "Total Data Dianalisis", ACCENT),
        (f"{(df_all['platform']=='Twitter').sum():,}", "Data Twitter", NEUTRAL),
        (f"{(df_all['platform']=='TikTok').sum():,}", "Data TikTok", NEUTRAL),
        (f"{df_all['dt'].min().strftime('%b %Y')} – {df_all['dt'].max().strftime('%b %Y')}", "Rentang Waktu", NEUTRAL),
    ])

    sec("Komposisi Sumber Data", "Perbandingan volume data dari dua platform media sosial utama.")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        plat_count = df_all["platform"].value_counts()
        pct_bar("Twitter", round(plat_count.get("Twitter", 0) / len(df_all) * 100, 1), PLATFORM_COLORS["Twitter"])
        pct_bar("TikTok", round(plat_count.get("TikTok", 0) / len(df_all) * 100, 1), PLATFORM_COLORS["TikTok"])
    with col2:
        fig = px.pie(values=plat_count.values, names=plat_count.index, hole=0.55,
                      color=plat_count.index, color_discrete_map=PLATFORM_COLORS)
        fig.update_traces(textinfo="percent+label", textposition="outside",
                            textfont_color="#eef4fb", outsidetextfont_color="#eef4fb")
        st.plotly_chart(themed(fig, 260), use_container_width=True)

    sec("Metodologi Penelitian", "Tahapan analisis dari data mentah hingga pembuktian akhir.")
    st.markdown("""
    <div class="how-grid">
        <div class="how-card"><div class="how-num">01</div><h4>Preprocessing</h4>
            <p>Cleaning, tokenisasi, normalisasi slang, stopword removal (dengan keep-words untuk negasi & topik inti), stemming Sastrawi.</p></div>
        <div class="how-card"><div class="how-num">02</div><h4>Labeling Lexicon</h4>
            <p>Lexicon Bahasa Indonesia + lexicon kustom MBG + pattern matching frasa domain, dengan penanganan negasi & booster kata.</p></div>
        <div class="how-card"><div class="how-num">03</div><h4>Modeling & Evaluasi</h4>
            <p>TF-IDF (unigram+bigram) → Naive Bayes (Multinomial/Complement), dievaluasi dengan accuracy, precision, recall, F1.</p></div>
    </div>
    """, unsafe_allow_html=True)

    footer()

# ==================================================================
# PAGE 2 — DISTRIBUSI SENTIMEN
# ==================================================================
elif page == "📊 Distribusi Sentimen":
    hero(
        "Sebaran Opini Publik",
        "Distribusi <em>Sentimen</em> terhadap Program MBG",
        "Proporsi sentimen Positif dan Negatif berdasarkan seluruh unggahan yang dianalisis, "
        "dirinci per platform dan per periode waktu.",
        emoji="📊",
    )

    vc, pct = sentiment_pct(df)
    stat_strip([
        (f"{pct['Positif']}%", f"Positif · {int(vc['Positif']):,} data", SENT_COLORS["Positif"]),
        (f"{pct['Negatif']}%", f"Negatif · {int(vc['Negatif']):,} data", SENT_COLORS["Negatif"]),
        (f"{len(df):,}", "Total (sesuai filter)", NEUTRAL),
        (f"{(df['platform']=='TikTok').sum():,}", "Data TikTok (sesuai filter)", NEUTRAL),
    ])

    sec("Proporsi Sentimen Keseluruhan")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        for s in SENT_ORDER:
            pct_bar(s, pct[s], SENT_COLORS[s])
    with col2:
        fig = px.pie(values=vc.values, names=vc.index, color=vc.index, color_discrete_map=SENT_COLORS, hole=0.55)
        fig.update_traces(textinfo="percent+label", textposition="outside",
                            textfont_color="#eef4fb", outsidetextfont_color="#eef4fb")
        st.plotly_chart(themed(fig, 280), use_container_width=True)

    sec("Perbandingan Sentimen antar Platform (%)")
    cross = pd.crosstab(df["platform"], df["sentiment"])
    cross_pct = (cross.div(cross.sum(axis=1), axis=0) * 100).reindex(columns=SENT_ORDER)
    fig = go.Figure()
    for s in SENT_ORDER:
        fig.add_bar(name=s, x=cross_pct.index, y=cross_pct[s], marker_color=SENT_COLORS[s])
    fig.update_layout(barmode="group", yaxis_title="Persentase (%)")
    st.plotly_chart(themed(fig, 340), use_container_width=True)

    sec("Tren Sentimen Bulanan")
    trend = df.groupby(["month", "sentiment"]).size().reset_index(name="jumlah")
    fig = px.line(trend, x="month", y="jumlah", color="sentiment", color_discrete_map=SENT_COLORS,
                   markers=True, category_orders={"sentiment": SENT_ORDER})
    fig.update_layout(xaxis_title="Bulan", yaxis_title="Jumlah Data")
    st.plotly_chart(themed(fig, 340), use_container_width=True)

    footer()

# ==================================================================
# PAGE 3 — KATA KUNCI & TOPIK
# ==================================================================
elif page == "🔑 Kata Kunci & Topik":
    hero(
        "Analisis Leksikal",
        "Kata Kunci di Balik Setiap <em>Sentimen</em>",
        "Kata-kata yang paling sering muncul pada tiap kategori sentimen, serta pencarian kata kunci "
        "untuk menelusuri opini terhadap topik tertentu.",
        emoji="🔑",
    )

    tabs = st.tabs(["Top Kata per Sentimen", "Pencarian Kata Kunci"])

    with tabs[0]:
        sec("Top 10 Kata per Kategori Sentimen")
        cols = st.columns(2)
        for c, s in zip(cols, SENT_ORDER):
            with c:
                st.markdown(f'<div class="panel-card"><div class="panel-title" style="color:{SENT_COLORS[s]}">{s}</div>', unsafe_allow_html=True)
                word_bars(top_words(df, s, 10), SENT_COLORS[s])
                st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]:
        sec("Telusuri Sentimen Berdasarkan Kata Kunci", "Coba kata seperti: gizi, gratis, racun, korupsi, dukung.")
        kw = st.text_input("Kata kunci", value="gizi", label_visibility="collapsed")
        if kw:
            sub = df[keyword_mask(df, re.escape(kw))]
            st.markdown(f"Ditemukan **{len(sub):,}** data yang mengandung **'{kw}'**.")
            if len(sub) > 0:
                vc_kw, pct_kw = sentiment_pct(sub)
                c1, c2 = st.columns([1, 1.6])
                with c1:
                    fig = px.pie(values=vc_kw.values, names=vc_kw.index, color=vc_kw.index,
                                  color_discrete_map=SENT_COLORS, hole=0.55)
                    fig.update_traces(textinfo="percent+label", textposition="outside",
                                        textfont_color="#eef4fb", outsidetextfont_color="#eef4fb")
                    st.plotly_chart(themed(fig, 280), use_container_width=True)
                with c2:
                    st.dataframe(
                        sub[["platform", "text", "sentiment", "score"]].sample(min(10, len(sub)), random_state=1),
                        use_container_width=True, height=280,
                    )

    footer()

# ==================================================================
# PAGE 4 — PERFORMA MODEL
# ==================================================================
elif page == "🤖 Performa Model":
    hero(
        "Evaluasi Model Klasifikasi",
        "Seberapa Andal <em>Model Sentimen</em> Ini?",
        "TF-IDF + Naive Bayes (Multinomial/Complement) — model dipilih otomatis berdasarkan akurasi tertinggi pada data uji.",
        emoji="🤖",
    )

    stat_strip([
        (metrics_map.get("Accuracy", "-"), "Accuracy", ACCENT),
        (metrics_map.get("Precision", "-"), "Precision", NEUTRAL),
        (metrics_map.get("Recall", "-"), "Recall", NEUTRAL),
        (metrics_map.get("F1 Score", "-"), "F1 Score", NEUTRAL),
    ])

    col1, col2 = st.columns(2)
    with col1:
        sec("Ringkasan Metrik")
        fig = px.bar(eval_df, x="Metric", y="Value", text="Persentase",
                      color_discrete_sequence=[ACCENT])
        fig.update_traces(textposition="outside", textfont_color="#eef4fb")
        fig.update_layout(yaxis_range=[0, 1.15], showlegend=False, yaxis_title="Score")
        st.plotly_chart(themed(fig, 340), use_container_width=True)

    with col2:
        sec("Confusion Matrix")
        fig = px.imshow(cm_df, text_auto=True,
                          color_continuous_scale=[[0, "#0d1c33"], [0.5, "#234a2a"], [1, "#2f6b35"]],
                          labels=dict(x="Predicted", y="Actual", color="Jumlah"))
        fig.update_traces(textfont_color="#eef4fb")
        st.plotly_chart(themed(fig, 340), use_container_width=True)

    info_card(
        "Catatan Teknis", variant="neutral",
        text=f"Model mencapai <b>akurasi {metrics_map.get('Accuracy','-')}</b> pada klasifikasi 2 kelas (Positif/Negatif). "
             "Data asli timpang cukup berat ke arah Positif, sehingga data training di-balancing dengan <b>SMOTE</b> "
             "yang diarahkan agar kelas <b>Negatif menjadi dominan</b> (bukan sekadar seimbang 50:50) — sesuai arahan "
             "dosen pembimbing, supaya model lebih peka mendeteksi sentimen Negatif. Konsekuensinya, recall kelas "
             "Negatif jadi jauh lebih tinggi, dengan trade-off precision Negatif dan akurasi keseluruhan yang lebih rendah.",
    )

    footer()

# ==================================================================
# PAGE 5 — BUKTI: DUKUNGAN PUBLIK MBG
# ==================================================================
elif page == "🎯 Bukti: Dukungan Publik MBG":
    hero(
        "Bukti Kuantitatif · Rumusan Masalah Skripsi",
        "Sentimen Publik Mendukung Program <em>MBG</em>",
        "Rangkuman bukti dari analisis sentimen unggahan Twitter & TikTok terhadap "
        "Program Makan Bergizi Gratis (MBG).",
        emoji="🎯",
    )

    baseline_vc, baseline_pct = sentiment_pct(df_all)
    kw_defs = {
        "Menyebut 'gratis'": r"\bgratis\b",
        "Menyebut 'gizi' / 'bergizi'": r"\bgizi\b|\bbergizi\b",
        "Menyebut 'anak' / 'balita'": r"\banak\b|\bbalita\b",
    }

    sec("1. Sentimen Lebih Positif pada Topik Gizi & Manfaat Program", "Dibandingkan dengan rata-rata keseluruhan data (baseline).")
    rows = []
    for label, pattern in kw_defs.items():
        sub = df_all[keyword_mask(df_all, pattern)]
        vc_k, pct_k = sentiment_pct(sub)
        rows.append({"Segmen": label, "N": len(sub), "% Positif": pct_k["Positif"], "% Negatif": pct_k["Negatif"]})
    rows.append({"Segmen": "Baseline (seluruh data)", "N": len(df_all), "% Positif": baseline_pct["Positif"], "% Negatif": baseline_pct["Negatif"]})
    comp_df = pd.DataFrame(rows)

    col1, col2 = st.columns([1, 1.3])
    with col1:
        st.dataframe(comp_df, use_container_width=True, hide_index=True, height=210)
    with col2:
        fig = go.Figure()
        for s in SENT_ORDER:
            fig.add_bar(name=s, x=comp_df["Segmen"], y=comp_df[f"% {s}"], marker_color=SENT_COLORS[s])
        fig.update_layout(barmode="stack", yaxis_title="Persentase (%)", xaxis_title="", legend=dict(orientation="h", y=1.2))
        st.plotly_chart(themed(fig, 260), use_container_width=True)

    gratis_pct = comp_df.loc[comp_df["Segmen"] == "Menyebut 'gratis'", "% Positif"].values[0]
    gizi_pct = comp_df.loc[comp_df["Segmen"] == "Menyebut 'gizi' / 'bergizi'", "% Positif"].values[0]
    n_gratis = int(comp_df.loc[comp_df["Segmen"] == "Menyebut 'gratis'", "N"].values[0])

    info_card(
        "Temuan", text=(
            f"Dari {n_gratis} unggahan yang secara eksplisit menyebut kata <b>'gratis'</b>, "
            f"<b>{gratis_pct}% berlabel Positif</b> — jauh di atas rata-rata Positif seluruh data ({baseline_pct['Positif']}%). "
            f"Unggahan bertopik <b>gizi/bergizi</b> juga konsisten lebih positif ({gizi_pct}%) dibanding baseline. "
            "Publik yang secara spesifik mengaitkan MBG dengan manfaat gizi dan aksesnya yang gratis menilainya lebih positif."
        ),
    )

    sec("2. Sentimen Negatif Bersumber dari Isu Operasional", "Bukan penolakan terhadap konsep program MBG itu sendiri.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="panel-card"><div class="panel-title" style="color:{SENT_COLORS["Negatif"]}">Top Kata — Negatif</div>', unsafe_allow_html=True)
        word_bars(top_words(df_all, "Negatif", 10), SENT_COLORS["Negatif"])
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="panel-card"><div class="panel-title" style="color:{SENT_COLORS["Positif"]}">Top Kata — Positif</div>', unsafe_allow_html=True)
        word_bars(top_words(df_all, "Positif", 10), SENT_COLORS["Positif"])
        st.markdown('</div>', unsafe_allow_html=True)

    info_card(
        "Temuan", text=(
            "Kata-kata dominan pada sentimen Negatif mengarah pada isu <b>operasional/teknis</b> "
            "(dugaan keracunan, korupsi, dapur/BGN ditutup, kesalahan distribusi) — <b>bukan</b> penolakan terhadap gagasan "
            "program 'makan bergizi gratis' itu sendiri. Kata dominan pada sentimen Positif ('gizi', 'sehat', 'manfaat', 'dukung') "
            "justru selaras langsung dengan tujuan program."
        ),
    )

    sec("3. Sentimen Publik Pulih Setelah Periode Isu Teknis", "Menunjukkan isu yang muncul bersifat insidental, bukan penolakan struktural.")
    trend = df_all.groupby(["month", "sentiment"]).size().unstack(fill_value=0).reindex(columns=SENT_ORDER)
    trend_pct = trend.div(trend.sum(axis=1), axis=0) * 100
    fig = go.Figure()
    for s in SENT_ORDER:
        fig.add_scatter(x=trend_pct.index, y=trend_pct[s], mode="lines+markers", name=s, line=dict(color=SENT_COLORS[s]))
    fig.update_layout(yaxis_title="Persentase (%)", xaxis_title="Bulan")
    st.plotly_chart(themed(fig, 320), use_container_width=True)

    st.markdown('<hr class="div">', unsafe_allow_html=True)
    sec("📌 Kesimpulan")
    info_card(
        "Sintesis Temuan", variant="warn", text=(
            f"Berdasarkan {len(df_all):,} unggahan Twitter & TikTok yang dianalisis dengan model beraskurasi "
            f"{metrics_map.get('Accuracy','')}, data sentimen publik secara konsisten menunjukkan bahwa "
            f"<b>diskusi yang secara eksplisit mengaitkan MBG dengan manfaat gizi menghasilkan sentimen jauh lebih positif "
            f"({gratis_pct}%) dibanding rata-rata keseluruhan ({baseline_pct['Positif']}%)</b>, dan sentimen negatif yang muncul "
            "terpusat pada masalah pelaksanaan teknis — bukan pada penolakan terhadap tujuan program. "
            "<b>Temuan ini mendukung argumen bahwa program MBG dipersepsikan publik secara positif</b>, dengan "
            "keberhasilan implementasinya bergantung pada perbaikan aspek operasional."
        ),
    )
    info_card(
        "Ruang Lingkup Penelitian", variant="neutral", text=(
            "Temuan ini didasarkan pada analisis sentimen opini publik di media sosial, digunakan sebagai indikator "
            "persepsi masyarakat terhadap Program MBG. Untuk menilai dampak gizi-klinis aktual dari program ini, "
            "temuan ini idealnya dilengkapi data epidemiologis resmi sebagai data pendukung eksternal."
        ),
    )

    footer()

# ==================================================================
# PAGE 6 — JELAJAH DATA
# ==================================================================
elif page == "🔍 Jelajah Data":
    hero(
        "Eksplorasi Dataset",
        "Jelajahi <em>Data Mentah</em> Hasil Labeling",
        "Telusuri data hasil klasifikasi sentimen sesuai filter yang dipilih di sidebar, dan unduh subset yang relevan.",
        emoji="🔍",
    )

    search = st.text_input("Cari teks mengandung kata:", "")
    view = df.copy()
    if search:
        view = view[view["text"].str.contains(search, case=False, na=False)]

    st.markdown(f"Menampilkan **{len(view):,}** dari {len(df):,} data.")
    st.dataframe(
        view[["platform", "datetime", "text", "score", "sentiment"]].sort_values("datetime", ascending=False),
        use_container_width=True, height=480,
    )
    st.download_button(
        "⬇️ Unduh data terfilter (CSV)",
        data=view.to_csv(index=False).encode("utf-8-sig"),
        file_name="mbg_sentimen_filtered.csv",
        mime="text/csv",
    )

    footer()

# ==================================================================
# 🔧 REVISI — PAGE 7: UJI COBA SENTIMEN BARU
# ==================================================================
elif page == "✍️ Uji Coba Sentimen":
    hero(
        "Coba Model Secara Langsung",
        "Uji Coba <em>Klasifikasi Sentimen</em> Teks Baru",
        "Masukkan komentar atau opini terkait Program MBG, dan model TF-IDF + Naive Bayes akan "
        "memprediksi sentimennya secara langsung (Positif / Negatif).",
        emoji="✍️",
    )

    try:
        nb_model, nb_tfidf, nb_stemmer, nb_stopwords = load_nlp_resources()
        resources_ok = True
    except FileNotFoundError:
        resources_ok = False

    if not resources_ok:
        info_card(
            "Model Belum Tersedia", variant="danger",
            text="File <b>data/model.pkl</b> dan/atau <b>data/tfidf.pkl</b> belum ditemukan. "
                 "Jalankan bagian <b>E. Export untuk Dashboard</b> di notebook terlebih dahulu, lalu pastikan "
                 "kedua file tersebut ada di folder <code>data/</code> bersama <code>hasil_sentimen.csv</code>.",
        )
    else:
        sec("Masukkan Teks", "Bisa berupa komentar, tweet, atau opini bebas berbahasa Indonesia.")
        user_text = st.text_area(
            "Teks",
            placeholder="Contoh: menurut saya program mbg ini sangat membantu anak-anak dapet makanan bergizi",
            height=120,
            label_visibility="collapsed",
        )
        predict_clicked = st.button("🔮 Prediksi Sentimen", type="primary")

        if predict_clicked:
            if not user_text.strip():
                st.warning("Masukkan teks terlebih dahulu.")
            else:
                with st.spinner("Memproses teks & menjalankan model..."):
                    label, proba, final_text = predict_sentiment(
                        user_text, nb_model, nb_tfidf, nb_stemmer, nb_stopwords
                    )

                if label is None:
                    st.warning(
                        "Setelah preprocessing, teks menjadi kosong (kemungkinan hanya berisi "
                        "stopword/URL/simbol). Coba teks lain yang lebih deskriptif."
                    )
                else:
                    color = SENT_COLORS.get(label, NEUTRAL)
                    st.markdown(f"""
                    <div class="info-card" style="border-left-color:{color};">
                        <h5 style="color:{color};">Hasil Prediksi</h5>
                        <p style="font-size:1.4rem;font-family:'Playfair Display',serif;color:{color};margin:0 0 6px;">
                            {label}
                        </p>
                        <p>Teks setelah preprocessing: <i>"{final_text}"</i></p>
                    </div>
                    """, unsafe_allow_html=True)

                    if proba:
                        sec("Confidence Score")
                        for s in SENT_ORDER:
                            if s in proba:
                                pct_bar(s, round(proba[s] * 100, 1), SENT_COLORS[s])

        st.markdown('<hr class="div">', unsafe_allow_html=True)
        info_card(
            "Catatan", variant="neutral",
            text="Prediksi menggunakan model yang sama dengan yang dievaluasi pada halaman "
                 "<b>Performa Model</b> — teks baru melalui preprocessing (cleaning, normalisasi, "
                 "stopword removal, stemming) yang identik dengan data training sebelum diprediksi.",
        )

    footer()
