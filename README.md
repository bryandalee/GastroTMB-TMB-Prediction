# GastroTMB — Sistem Prediksi TMB Kanker Lambung

## PENTING: Cara Menjalankan yang Benar

JANGAN buka index.html dengan double-click langsung.
Harus dijalankan lewat server agar prediksi berjalan benar.

---

## Cara 1: Jalankan dengan Python (DIREKOMENDASIKAN)

Buka terminal / command prompt di folder ini, lalu:

### Langkah 1 — Install dependencies (sekali saja)
    pip install flask flask-cors scikit-learn pandas numpy

### Langkah 2 — Jalankan backend Flask
    python app.py

Tunggu sampai muncul tulisan: "Model siap. 774 pasien..."

### Langkah 3 — Buka web di browser
Buka browser, ketik:
    http://localhost:5050

SELESAI. Tidak perlu buka index.html manual.

---

## Cara 2: Pakai VS Code Live Server

1. Install extension "Live Server" di VS Code
2. Klik kanan index.html → "Open with Live Server"
3. Jalankan juga: python app.py di terminal terpisah

---

## Kenapa tidak boleh double-click index.html?

Browser memblokir koneksi ke backend (localhost:5050) kalau
file dibuka lewat file:// — akibatnya prediksi selalu pakai
mode offline yang tidak membaca input dengan benar.

---

## (Opsional) Demo Publik dengan ngrok

Kalau mau membagikan demo yang jalan di komputer sendiri ke orang lain lewat internet, bisa pakai [ngrok](https://ngrok.com/download) (download terpisah, jangan taruh file `.exe`-nya di repo ini):

    ngrok http 5050

---

## Sumber Data

Data klinis dan mutasi merupakan **gabungan dari 5 studi kanker lambung** publik di [cBioPortal for Cancer Genomics](https://www.cbioportal.org/):

| Study ID | Studi |
|---|---|
| `stad_tcga` | Stomach Adenocarcinoma (TCGA, Firehose Legacy) |
| `stad_oncosg_2018` | Stomach Adenocarcinoma (OncoSG, 2018) |
| `stad_pfizer_uhongkong` | Stomach Adenocarcinoma (Pfizer and UHK, Nat Genet 2014) |
| `stad_uhongkong` | Gastric Cancer (University of Hong Kong) |
| `stad_utokyo` | Gastric Cancer (University of Tokyo) |

Total gabungan sekitar 774 sampel pasien. Detail lengkap tiap studi bisa dilihat langsung di `cbioportal.org/study/summary?id=<study_id>`. Seluruh data bersifat publik dan sudah dianonimkan (tidak memuat identitas pasien).

## ⚠️ Disclaimer

Proyek ini dibuat untuk tujuan pembelajaran/akademis. Prediksi dan rekomendasi terapi yang dihasilkan **bukan** alat diagnosis atau pengambilan keputusan klinis yang tervalidasi, dan tidak boleh menggantikan penilaian medis profesional.

---

## Struktur File
    gastrotmb/
    ├── index.html                        — antarmuka web
    ├── app.py                            — backend Flask (training otomatis dari CSV)
    ├── requirements.txt                  — daftar library Python
    ├── mutations_gabungan.txt            — data mutasi (dari cBioPortal)
    └── combined_study_clinical_data.tsv  — data klinis TMB (dari cBioPortal)

Tidak ada file model.pkl — model dilatih langsung dari CSV saat server start (~1 detik).
