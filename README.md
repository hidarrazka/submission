# Bike Sharing Analysis Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Dashboard interaktif hasil analisis dataset **Bike Sharing** (Capital Bikeshare, Washington D.C., 2011–2012) yang dibangun menggunakan [Streamlit](https://streamlit.io/) dan [Plotly](https://plotly.com/python/).

> [!NOTE]
> Dashboard ini menyediakan filter interaktif penuh, 6 KPI utama, serta visualisasi untuk menjawab tiga pertanyaan bisnis terkait pola penyewaan sepeda.

---

## 📋 Daftar Isi

- [Pertanyaan Bisnis](#-pertanyaan-bisnis)
- [Struktur Proyek](#-struktur-proyek)
- [Setup Environment](#%EF%B8%8F-setup-environment)
  - [Anaconda](#-anaconda)
  - [Shell/Terminal](#-shellterminal)
- [Menjalankan Dashboard](#-menjalankan-dashboard)
- [Isi Dashboard](#-isi-dashboard)
- [Catatan Analisis](#-catatan-analisis)

---

## 🎯 Pertanyaan Bisnis

1. Bagaimana pola rata-rata jumlah penyewaan sepeda per jam pada **hari kerja versus akhir pekan** sepanjang periode 2011–2012, dan jam berapa saja yang merupakan jam sibuk untuk mengoptimalkan redistribusi armada?
2. Berapa persen **penurunan rata-rata penyewaan pada kondisi cuaca buruk** dibandingkan cuaca cerah sepanjang periode 2011–2012, dan bagaimana distribusinya di setiap musim?
3. Bagaimana **pengelompokan hari ke dalam kategori permintaan Rendah, Sedang, dan Tinggi** berdasarkan binning persentil, serta karakteristik musim dan cuaca apa yang mendominasi kelompok permintaan tinggi?

---

## 📁 Struktur Proyek

```
.
├── Bike-sharing-dataset/       # Dataset asli (day.csv, hour.csv, Readme.txt)
├── data/
│   ├── day.csv                 # Salinan dataset harian
│   └── hour.csv                # Salinan dataset per jam
├── dashboard/
│   ├── main_data.csv           # Data harian yang sudah dibersihkan
│   └── dashboard.py            # Aplikasi Streamlit
├── Notebook.ipynb              # Notebook analisis (sudah dieksekusi)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Environment

> [!IMPORTANT]
> Setup environment diperlukan untuk membuat lingkungan yang **terisolasi**, sehingga dependency yang digunakan tidak mengalami konflik dengan package atau konfigurasi pada environment lain, serta mengurangi risiko error saat dashboard dijalankan.

### 🐍 Anaconda

Jika Anda menggunakan [Anaconda](https://www.anaconda.com/) atau [Miniconda](https://docs.conda.io/en/latest/miniconda.html), jalankan perintah berikut:

```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

### 🖥️ Shell/Terminal

Jika Anda menggunakan terminal biasa dengan [pipenv](https://pipenv.pypa.io/), jalankan perintah berikut:

```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

---

## 🚀 Menjalankan Dashboard

Setelah environment terpasang dan dependensi terinstal, jalankan aplikasi Streamlit dengan perintah berikut:

```bash
streamlit run dashboard/dashboard.py
```

> [!TIP]
> Buka browser dan akses **`http://localhost:8501`** untuk melihat dashboard.

---

## 📊 Isi Dashboard

| Bagian | Deskripsi |
|--------|-----------|
| **Filter Interaktif** | Sidebar berisi filter rentang tanggal, tahun, musim, kondisi cuaca, tipe hari, serta tombol **Reset Filter** |
| **6 KPI Utama** | Total penyewaan, rata-rata harian, pengguna terdaftar & kasual (total + %), hari puncak, dan rata-rata suhu terasa |
| **Tab Tren & Komposisi** | Line chart tren (toggle Harian/Bulanan) total/terdaftar/kasual + donut komposisi pengguna |
| **Tab Pertanyaan 1** | Pola 24 jam hari kerja vs akhir pekan (Plotly, hover & zoom) + tabel jam sibuk |
| **Tab Pertanyaan 2** | Bar rata-rata penyewaan per cuaca (dengan error bar std) + grouped bar musim × cuaca |
| **Tab Pertanyaan 3** | Distribusi kelompok permintaan (binning persentil) per musim/cuaca + profil kelompok |
| **Tab Sensitivitas Suhu** | Rata-rata penyewaan per rentang suhu (bins) + sebaran suhu vs penyewaan |
| **Panel Insight Bisnis** | YoY growth, komuter vs rekreasi, dampak cuaca & suhu ekstrem (expander) |
| **Eksplorasi & Unduh** | Tabel data tersaring + tombol unduh CSV |

> [!NOTE]
> Semua chart menggunakan **Plotly** (hover, zoom, pan, toggle legend). Filter memengaruhi seluruh visualisasi dan KPI.

---

## 📝 Catatan Analisis

- Notebook `Notebook.ipynb` berisi proses lengkap: Data Wrangling (Gathering, Assessing, Cleaning), EDA, Visualization & Explanatory Analysis, Analisis Lanjutan (clustering manual berbasis binning), serta Conclusion & Recommendation.
- Fitur `temp`, `atemp`, `hum`, dan `windspeed` pada dataset asli sudah ternormalisasi; pada analisis dilakukan denormalisasi ke satuan asli (°C, %, km/h).

---

## 📚 Dataset

Dataset **Bike Sharing Dataset** tersedia di [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/bike+sharing+attribute) dan berisi data sewa Capital Bikeshare di Washington D.C. selama tahun 2011–2012.
