# 🍱 MBG Sentiment — Dashboard Analisis Sentimen Program Makan Bergizi Gratis

Dashboard interaktif berbasis **Streamlit** untuk menganalisis sentimen publik terhadap Program Makan Bergizi Gratis (MBG) di media sosial (Twitter & TikTok), sebagai bagian dari penelitian skripsi **"Analisis Sentimen Program Makan Bergizi Gratis sebagai Upaya Pencegahan Stunting"**.

Model klasifikasi menggunakan **TF-IDF + Naive Bayes**, dengan penanganan data tidak seimbang menggunakan **SMOTE**, dan mengklasifikasikan sentimen ke dalam 2 kategori: **Positif** dan **Negatif**.

---

## ✨ Fitur

- **🏠 Ringkasan** — gambaran umum metodologi & temuan utama penelitian
- **📊 Distribusi Sentimen** — proporsi sentimen Positif/Negatif, filter berdasarkan platform & rentang waktu
- **🔑 Kata Kunci & Topik** — kata-kata yang paling sering muncul per kategori sentimen
- **🤖 Performa Model** — confusion matrix & metrik evaluasi (accuracy, precision, recall, F1)
- **🎯 Bukti: MBG & Stunting** — analisis keterkaitan sentimen dengan topik stunting
- **🔍 Jelajah Data** — tabel data mentah hasil klasifikasi, bisa difilter & diunduh
- **✍️ Uji Coba Sentimen** — masukkan teks/komentar baru secara bebas, model akan memprediksi sentimennya secara *real-time*

---

## 🗂️ Struktur Folder

Pastikan struktur folder seperti berikut sebelum menjalankan aplikasi:

```
├── app.py                     # aplikasi utama Streamlit
├── requirements.txt           # daftar dependency Python
└── data/
    ├── hasil_sentimen.csv     # data hasil klasifikasi sentimen
    ├── hasil_evaluasi.csv     # metrik evaluasi model
    ├── confusion_matrix.csv   # confusion matrix hasil testing
    ├── model.pkl              # model Naive Bayes terlatih
    └── tfidf.pkl              # TF-IDF vectorizer terlatih
```

> File-file di dalam folder `data/` dihasilkan dari notebook `SKRIPSI_AnalisisSentimenMBG.ipynb` pada bagian **"Export untuk Dashboard"** — jalankan notebook tersebut terlebih dahulu sebelum menjalankan dashboard.

---

## ⚙️ Instalasi & Menjalankan Secara Lokal

1. **Clone repo ini**
   ```bash
   git clone <url-repo-ini>
   cd <nama-folder-repo>
   ```

2. **(Opsional tapi disarankan) buat virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependency**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download data NLTK** (dibutuhkan fitur Uji Coba Sentimen, hanya perlu dilakukan sekali)
   ```bash
   python -m nltk.downloader punkt punkt_tab stopwords
   ```

5. **Jalankan aplikasi**
   ```bash
   streamlit run app.py
   ```

6. Buka browser ke `http://localhost:8501`

---

## 🧠 Alur Model (Ringkas)

1. **Data Collection** — scraping data Twitter & TikTok terkait Program MBG
2. **Preprocessing** — cleaning, tokenizing, normalisasi (slang), stopword removal, stemming (Sastrawi)
3. **Labeling** — pelabelan sentimen otomatis berbasis skor leksikon → **Positif** / **Negatif**
4. **Feature Extraction** — TF-IDF vectorization
5. **Balancing** — SMOTE pada data training (kelas minoritas)
6. **Modeling** — Multinomial Naive Bayes
7. **Evaluation** — accuracy, precision, recall, F1-score, confusion matrix
8. **Export** — model & vectorizer disimpan (`.pkl`) untuk digunakan kembali di dashboard

---

## 🛠️ Tech Stack

| Kategori | Tools |
|---|---|
| Dashboard | Streamlit, Plotly |
| NLP | NLTK, Sastrawi, Scikit-learn (TF-IDF), imbalanced-learn (SMOTE) |
| Model | Multinomial Naive Bayes |
| Data | Pandas |

---

## 📌 Catatan

- Fitur **Uji Coba Sentimen** menggunakan pipeline preprocessing yang identik dengan proses training di notebook, agar hasil prediksi konsisten.
- Jika mengalami error `HTTP 429` saat download data NLTK, tunggu beberapa menit lalu coba lagi (rate limit sementara dari server NLTK), atau unduh manual — lihat [dokumentasi NLTK](https://www.nltk.org/data.html).

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan tugas akhir/skripsi.
