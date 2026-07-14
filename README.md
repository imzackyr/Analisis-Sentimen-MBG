# Dashboard Analisis Sentimen MBG & Pencegahan Stunting

Dashboard ini dibuat dari hasil akhir notebook `SKRIPSI_AnalisisSentimenMBG_Final.ipynb`
(data Twitter + TikTok, preprocessing lexicon-based, model Complement Naive Bayes).

## Isi Folder
```
mbg_dashboard/
├── app.py                     # Aplikasi Streamlit utama
├── requirements.txt
├── data/
│   ├── hasil_sentimen.csv     # Dataset final berlabel sentimen (dari notebook)
│   ├── hasil_evaluasi.csv     # Metrik evaluasi model (accuracy, precision, recall, F1)
│   └── confusion_matrix.csv   # Confusion matrix model
└── README.md
```

## Cara Menjalankan

1. Pastikan Python 3.9+ sudah terinstall.
2. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan dashboard dari dalam folder `mbg_dashboard`:
   ```bash
   streamlit run app.py
   ```
4. Dashboard akan terbuka otomatis di browser (biasanya `http://localhost:8501`).

## Struktur Halaman

- **🏠 Ringkasan Data** — profil dataset, proporsi platform, alur analisis.
- **📊 Distribusi Sentimen** — proporsi sentimen keseluruhan, per platform, dan tren bulanan.
- **🔑 Kata Kunci & Topik** — top kata per sentimen + pencarian kata kunci interaktif.
- **🤖 Performa Model** — accuracy/precision/recall/F1 dan confusion matrix.
- **🎯 Pembuktian: MBG vs Stunting** — halaman inti yang membandingkan sentimen pada
  segmen teks yang menyebut "stunting"/"gizi" vs baseline, analisis kata pemicu sentimen
  negatif, tren waktu, dan kesimpulan.
- **🔍 Jelajah Data** — tabel data mentah dengan pencarian & unduh CSV.

## Catatan
Jika ingin memperbarui data (misalnya setelah re-run notebook dengan data baru),
tinggal timpa file di folder `data/` dengan format kolom yang sama:
`id, datetime, username, platform, text, final_text, jumlah_karakter, jumlah_kata, score, sentiment`.
