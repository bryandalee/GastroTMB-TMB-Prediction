import os
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model import TMB_THRESHOLD, train_and_evaluate, print_report

BASE = os.path.dirname(os.path.abspath(__file__))
app  = Flask(__name__, static_folder=BASE)
CORS(app)

# =======================================================
# TRAINING + EVALUASI LANGSUNG SAAT SERVER START
# Tidak ada file model.pkl — model dilatih dari CSV (~5 detik)
# Model dilatih di data latih (80%) dan dievaluasi di data uji (20%),
# detailnya ada di model.py
# =======================================================
print("Memuat data, melatih, dan mengevaluasi model...")

RESULT = train_and_evaluate()
print_report(RESULT)

model              = RESULT['model']
GENE_COLUMNS       = RESULT['gene_columns']
FEATURE_IMPORTANCE = RESULT['feature_importance']

print(f"Model siap. {RESULT['n_samples']} pasien | "
      f"latih: {RESULT['n_train']} | uji: {RESULT['n_test']}")
print(f"Buka browser: http://localhost:5050")

# =======================================================
# SERVE FRONTEND — buka http://localhost:5050 di browser
# =======================================================
@app.route('/')
def index():
    return send_from_directory(BASE, 'index.html')

# =======================================================
# API ENDPOINTS
# =======================================================
@app.route('/api/info', methods=['GET'])
def info():
    return jsonify({
        'genes'              : GENE_COLUMNS,
        'tmb_threshold'      : TMB_THRESHOLD,
        'n_samples'          : RESULT['n_samples'],
        'n_high'             : RESULT['n_high'],
        'n_low'              : RESULT['n_low'],
        'n_train'            : RESULT['n_train'],
        'n_test'             : RESULT['n_test'],
        'n_test_high'        : RESULT['n_test_high'],
        'feature_importance' : FEATURE_IMPORTANCE,
        'test_metrics'       : RESULT['test_metrics'],
        'cv_metrics'         : RESULT['cv_metrics'],
        'baseline'           : RESULT['baseline']
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'genes' not in data:
        return jsonify({'error': 'Missing genes input'}), 400

    genes_input = data['genes']
    features    = []
    gene_status = {}

    for gene in GENE_COLUMNS:
        val    = genes_input.get(gene, 'WT')
        binary = 0 if str(val).strip().upper() == 'WT' else 1
        features.append(binary)
        gene_status[gene] = {'input': val, 'binary': binary}

    X = pd.DataFrame([features], columns=GENE_COLUMNS)

    pred_class = int(model.predict(X)[0])
    pred_proba = model.predict_proba(X)[0].tolist()
    confidence = pred_proba[pred_class] * 100

    contributions = [
        {'gene': g, 'importance': round(FEATURE_IMPORTANCE[g] * 100, 2)}
        for g in GENE_COLUMNS if gene_status[g]['binary'] == 1
    ]
    contributions.sort(key=lambda x: -x['importance'])

    is_high = pred_class == 1
    return jsonify({
        'prediction'       : 'TMB-High' if is_high else 'TMB-Low',
        'prediction_class' : pred_class,
        'confidence'       : round(confidence, 2),
        'probability_high' : round(pred_proba[1] * 100, 2),
        'probability_low'  : round(pred_proba[0] * 100, 2),
        'gene_status'      : gene_status,
        'mutated_genes'    : [g for g in GENE_COLUMNS if gene_status[g]['binary'] == 1],
        'contributions'    : contributions,
        'recommendation'   : {
            'therapy'  : 'Imunoterapi / Immunotherapy' if is_high else
                         'Kemoterapi Konvensional / Conventional Chemotherapy',
            'detail_id': (
                'Profil mutasi menunjukkan beban mutasi tinggi (TMB-High). '
                'Pasien direkomendasikan untuk dipertimbangkan mendapatkan terapi '
                'PD-1/PD-L1 inhibitor (contoh: pembrolizumab). '
                'Konfirmasi dengan sequencing panel TMB standar disarankan.'
            ) if is_high else (
                'Profil mutasi menunjukkan beban mutasi rendah (TMB-Low). '
                'Pasien disarankan untuk penanganan kemoterapi konvensional. '
                'Konfirmasi dengan sequencing panel TMB standar disarankan.'
            ),
            'detail_en': (
                'Mutation profile indicates high tumor mutational burden (TMB-High). '
                'Patient is recommended to be considered for PD-1/PD-L1 inhibitor '
                'therapy (e.g., pembrolizumab). '
                'Confirmation with standard TMB sequencing panel is advised.'
            ) if is_high else (
                'Mutation profile indicates low tumor mutational burden (TMB-Low). '
                'Patient is recommended for conventional chemotherapy. '
                'Confirmation with standard TMB sequencing panel is advised.'
            )
        }
    })


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5050)
