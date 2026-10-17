# Bike Sharing Analysis Dashboard

Dashboard interaktif hasil analisis dataset **Bike Sharing** (Capital Bikeshare, Washington D.C., 2011–2012) yang dibuat dengan Streamlit.

## Pertanyaan Bisnis

1. Bagaimana pola rata-rata jumlah penyewaan sepeda per jam pada hari kerja versus akhir pekan sepanjang periode 2011–2012, dan jam berapa saja yang merupakan jam sibuk untuk mengoptimalkan redistribusi armada?
2. Berapa persen penurunan rata-rata jumlah penyewaan sepeda pada kondisi cuaca buruk dibandingkan cuaca cerah sepanjang periode 2011–2012, dan bagaimana distribusinya di setiap musim?
3. Bagaimana pengelompokan hari ke dalam kategori permintaan Rendah, Sedang, dan Tinggi berdasarkan binning persentil, serta karakteristik musim dan cuaca apa yang mendominasi kelompok permintaan tinggi?

## Struktur Proyek

```
.
├── Bike-sharing-dataset/       # Dataset asli (day.csv, hour.csv, Readme.txt)
├── data/
│   ├── day.csv                 # Salinan dataset harian
│   └── hour.csv                # Salinan dataset per jam
├── dashboard/
│   ├── main_data.csv           # Data harian yang sudah dibersihkan
│   └── dashboard.py            # Aplikasi Streamlit
├── Notebook.ipynb  # Notebook analisis (sudah dieksekusi)
├── requirements.txt
└── README.md
```

## Cara Menjalankan Dashboard

1. Pastikan Python terpasang (disarankan 3.9+).
2. Install dependensi:

   ```bash
   pip install -r requirements.txt
   ```

3. Jalankan aplikasi dari root proyek:

   ```bash
   streamlit run dashboard/dashboard.py
   ```

4. Buka URL yang muncul di browser (biasanya `http://localhost:8501`).

## Isi Dashboard

- **Filter interaktif penuh** (sidebar): rentang tanggal, tahun, musim, kondisi cuaca, tipe hari, serta tombol **Reset Filter**.
- **6 KPI**: total penyewaan, rata-rata harian, pengguna terdaftar & kasual (total + %), hari puncak, dan rata-rata suhu terasa.
- **Tab Tren & Komposisi**: line chart tren (toggle Harian/Bulanan) total/terdaftar/kasual + donut komposisi pengguna.
- **Tab Pertanyaan 1**: pola 24 jam hari kerja vs akhir pekan (Plotly, hover & zoom) + tabel jam sibuk.
- **Tab Pertanyaan 2**: bar rata-rata penyewaan per cuaca (dengan error bar std) + grouped bar musim × cuaca.
- **Tab Pertanyaan 3**: distribusi kelompok permintaan (binning persentil) per musim/cuaca + profil kelompok.
- **Tab Sensitivitas Suhu**: rata-rata penyewaan per rentang suhu (bins) + sebaran suhu vs penyewaan.
- **Panel Insight Bisnis** (expander): YoY growth, komuter vs rekreasi, dampak cuaca & suhu ekstrem.
- **Eksplorasi & Unduh**: tabel data tersaring + tombol unduh CSV.

Semua chart menggunakan **Plotly** (hover, zoom, pan, toggle legend). Filter memengaruhi seluruh visualisasi dan KPI.

## Catatan Analisis

- Notebook `Proyek_Analisis_Data.ipynb` berisi proses lengkap: Data Wrangling (Gathering, Assessing, Cleaning), EDA, Visualization & Explanatory Analysis, Analisis Lanjutan (clustering manual berbasis binning), serta Conclusion & Recommendation.
- Fitur `temp`, `atemp`, `hum`, dan `windspeed` pada dataset asli sudah ternormalisasi; pada analisis dilakukan denormalisasi ke satuan asli (°C, %, km/h).
