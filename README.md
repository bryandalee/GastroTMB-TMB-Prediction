# GastroTMB — Sistem Prediksi TMB Kanker Lambung

## 📖 Tentang Proyek

Kanker lambung adalah salah satu penyebab kematian akibat kanker tertinggi di dunia, dan efektivitas pengobatannya sangat bergantung pada pemilihan antara **kemoterapi konvensional** atau **imunoterapi** modern. Salah satu biomarker penentu pilihan terapi adalah **Tumor Mutational Burden (TMB)** — jumlah mutasi somatik pada genom sel kanker. Semakin tinggi TMB, semakin besar peluang sel kanker "terlihat" dan direspons oleh sistem imun, sehingga pasien TMB-High berpotensi lebih cocok mendapat imunoterapi (PD-1/PD-L1 inhibitor), sementara TMB-Low umumnya diarahkan ke kemoterapi konvensional.

Masalahnya, penentuan TMB lewat *Whole Exome Sequencing* (WES) mahal dan memakan waktu lama. **GastroTMB** dibuat sebagai alat skrining awal berbasis *machine learning* untuk memprediksi status TMB-High/TMB-Low hanya dari status mutasi pada 10 gen kunci, sebagai alternatif yang jauh lebih cepat dan murah dibanding WES.

Proyek ini dikerjakan untuk tugas **Project CompBio** oleh **Kelompok 8**.

## ✨ Fitur Utama

- Prediksi status **TMB-High / TMB-Low** dari status mutasi 10 gen: `TTN`, `TP53`, `MUC16`, `ARID1A`, `LRP1B`, `SYNE1`, `FLG`, `FAT4`, `CSMD3`, `PCLO`
- Model **Random Forest** dilatih otomatis dari data mentah setiap kali server dijalankan (tidak perlu file model terpisah)
- Menampilkan tingkat keyakinan (confidence) prediksi beserta probabilitas TMB-High vs TMB-Low
- Menunjukkan kontribusi tiap gen yang bermutasi terhadap hasil prediksi (feature importance)
- Rekomendasi arah terapi (imunoterapi vs kemoterapi konvensional) dalam Bahasa Indonesia & English
- Web interface sederhana untuk memasukkan status mutasi gen pasien

## 🛠️ Teknologi

- **Backend:** Python, Flask, Flask-CORS
- **Machine Learning:** scikit-learn (Random Forest Classifier)
- **Data processing:** pandas, numpy
- **Frontend:** HTML, CSS, JavaScript

## 🧬 Metodologi Singkat

- **Seleksi fitur:** 10 gen dipilih berdasarkan frekuensi mutasi tertinggi pada kohort TCGA Gastric Cancer (STAD) menurut publikasi PMC (2021)
- **Threshold TMB-High:** ≥ 10 mutasi/Mb — mengikuti standar yang dipakai FDA saat menyetujui pembrolizumab untuk tumor solid TMB-tinggi (studi KEYNOTE-158)
- **Kenapa Random Forest?** Efektif menangani data genomik berdimensi tinggi (banyak fitur/gen dibanding jumlah sampel), tahan terhadap outlier, dan memberi *feature importance* untuk melihat gen mana yang paling berpengaruh
- **Alur kerja:** Data TCGA/cBioPortal (klinis + mutasi) → encoding & labeling (TMB ≥ 10 mut/Mb) → training model (split 80/20) → evaluasi

## 📊 Hasil Evaluasi Model

Dievaluasi pada test set (20% data, di luar data training):

| Kelas | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| TMB-Low | 0.93 | 0.95 | 0.94 | 132 |
| TMB-High | 0.68 | 0.57 | 0.62 | 23 |
| **Akurasi keseluruhan** | | | **0.90** | 155 |
| Macro avg | 0.81 | 0.76 | 0.78 | 155 |
| Weighted avg | 0.89 | 0.90 | 0.89 | 155 |

**Confusion Matrix:**

| | Prediksi Low | Prediksi High |
|---|---|---|
| **Aktual Low** | 126 | 6 |
| **Aktual High** | 10 | 13 |

Model lebih kuat mendeteksi kelas TMB-Low dibanding TMB-High — wajar mengingat jumlah sampel TMB-High jauh lebih sedikit (23 dari 155 data test).

## ⚠️ Limitasi & Potensi Pengembangan

**Limitasi:**
- Model dilatih 100% dari database publik internasional (cBioPortal), belum divalidasi pada sampel pasien populasi lokal Indonesia
- Semua jenis variasi mutasi disederhanakan jadi biner (mutasi/tidak), tanpa membedakan tingkat keparahan (*pathogenicity score*) tiap jenis mutasi

**Potensi pengembangan lanjutan:**
- Integrasi data multimodal — menggabungkan fitur genomik dengan rekam medis klinis pasien untuk meningkatkan akurasi
- Mengganti sistem biner (0/1) dengan skor numerik berbasis tingkat keparahan mutasi (misal skor CADD)

---

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

---


## 📚 Referensi

- Mining TCGA for TMB in Gastric Cancer — [PMC7805270](https://pmc.ncbi.nlm.nih.gov/articles/PMC7805270/)
- MUC16 prognosis pada TCGA — [PMC8173414](https://pmc.ncbi.nlm.nih.gov/articles/PMC8173414/)
- FDA Approval Summary: Pembrolizumab for TMB-High solid tumors — [PMC8416776](https://pmc.ncbi.nlm.nih.gov/articles/PMC8416776/pdf/nihms-1711511.pdf)
- FDA — Pembrolizumab approval for adults and children with TMB-H solid tumors — [fda.gov](https://www.fda.gov/drugs/drug-approvals-and-databases/fda-approves-pembrolizumab-adults-and-children-tmb-h-solid-tumors)
- Association of TMB with Efficacy of Pembrolizumab±Chemotherapy (KEYNOTE-062) — [AACR Journals](https://aacrjournals.org/clincancerres/article-abstract/28/16/3489/707386/)
- Tumor mutational burden as a biomarker for PD-1 treatment in gastric cancer — [Springer](https://link.springer.com/article/10.1186/s40880-019-0417-1)
