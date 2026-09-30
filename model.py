import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, average_precision_score, confusion_matrix
)

BASE = os.path.dirname(os.path.abspath(__file__))

TMB_THRESHOLD = 10.0
TEST_SIZE     = 0.2
RANDOM_STATE  = 42

# Metrik yang dihitung di cross-validation (sama dengan yang dilaporkan di data uji)
CV_SCORING = ['accuracy', 'balanced_accuracy', 'recall', 'precision', 'f1',
              'roc_auc', 'average_precision']

# Kandidat hyperparameter — dipilih lewat CV di data latih saja
PARAM_GRID = {'min_samples_leaf': [1, 3, 5, 10]}


# =======================================================
# DATA
# =======================================================
def load_dataset():
    clinical = pd.read_csv(os.path.join(BASE, 'combined_study_clinical_data.tsv'), sep='\t')
    mut      = pd.read_csv(os.path.join(BASE, 'mutations_gabungan.txt'), sep='\t')

    gene_columns = list(mut.columns[2:])

    mut_bin = mut.copy()
    mut_bin[gene_columns] = mut[gene_columns].map(
        lambda x: 0 if str(x).upper() == 'WT' else 1
    )

    merged = mut_bin.merge(
        clinical[['Sample ID', 'Study ID', 'TMB (nonsynonymous)']],
        left_on=['SAMPLE_ID', 'STUDY_ID'],
        right_on=['Sample ID', 'Study ID'],
        how='inner'
    ).dropna(subset=['TMB (nonsynonymous)'])

    merged['TMB_LABEL'] = (merged['TMB (nonsynonymous)'] >= TMB_THRESHOLD).astype(int)

    return merged[gene_columns], merged['TMB_LABEL'], gene_columns


# =======================================================
# EVALUASI
# =======================================================
def compute_metrics(y_true, y_pred, y_proba):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        'accuracy'          : accuracy_score(y_true, y_pred),
        'balanced_accuracy' : balanced_accuracy_score(y_true, y_pred),
        'sensitivity'       : recall_score(y_true, y_pred, zero_division=0),
        'specificity'       : recall_score(y_true, y_pred, pos_label=0, zero_division=0),
        'precision'         : precision_score(y_true, y_pred, zero_division=0),
        'f1'                : f1_score(y_true, y_pred, zero_division=0),
        'roc_auc'           : roc_auc_score(y_true, y_proba),
        'pr_auc'            : average_precision_score(y_true, y_proba),
        'confusion_matrix'  : {'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)},
    }


def train_and_evaluate():
    X, y, gene_columns = load_dataset()

    # Data uji disisihkan di awal dan TIDAK disentuh sampai evaluasi akhir.
    # stratify=y menjaga proporsi TMB-High sama di data latih dan data uji.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    # class_weight='balanced' — tanpa ini model cenderung menebak "Low" terus
    # karena TMB-High hanya ~15% data.
    search = GridSearchCV(
        RandomForestClassifier(
            n_estimators=200, class_weight='balanced', random_state=RANDOM_STATE
        ),
        PARAM_GRID,
        scoring=CV_SCORING,
        refit='average_precision',
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
    )
    search.fit(X_train, y_train)
    model = search.best_estimator_

    best = search.best_index_
    cv_metrics = {
        s: {'mean': float(search.cv_results_[f'mean_test_{s}'][best]),
            'std' : float(search.cv_results_[f'std_test_{s}'][best])}
        for s in CV_SCORING
    }

    test_metrics = compute_metrics(
        y_test, model.predict(X_test), model.predict_proba(X_test)[:, 1]
    )

    # Baseline: selalu menebak kelas mayoritas data latih, tanpa melihat gen apa pun
    majority = int(y_train.mode()[0])
    baseline_pred = np.full(len(y_test), majority)
    baseline = {
        'accuracy'          : accuracy_score(y_test, baseline_pred),
        'balanced_accuracy' : balanced_accuracy_score(y_test, baseline_pred),
        'sensitivity'       : recall_score(y_test, baseline_pred, zero_division=0),
    }

    return {
        'model'              : model,
        'gene_columns'       : gene_columns,
        'feature_importance' : dict(zip(gene_columns, model.feature_importances_.tolist())),
        'best_params'        : search.best_params_,
        'n_samples'          : len(y),
        'n_high'             : int(y.sum()),
        'n_low'              : int((y == 0).sum()),
        'n_train'            : len(y_train),
        'n_train_high'       : int(y_train.sum()),
        'n_test'             : len(y_test),
        'n_test_high'        : int(y_test.sum()),
        'cv_metrics'         : cv_metrics,
        'test_metrics'       : test_metrics,
        'baseline'           : baseline,
    }


def print_report(r):
    t, b, cm = r['test_metrics'], r['baseline'], r['test_metrics']['confusion_matrix']

    print("=" * 58)
    print("EVALUASI MODEL GastroTMB")
    print("=" * 58)
    print(f"Total      : {r['n_samples']} pasien | TMB-High: {r['n_high']} | TMB-Low: {r['n_low']}")
    print(f"Data latih : {r['n_train']} pasien | TMB-High: {r['n_train_high']}")
    print(f"Data uji   : {r['n_test']} pasien | TMB-High: {r['n_test_high']}")
    print(f"Hyperparameter terpilih (CV di data latih): {r['best_params']}")

    print("\n-- Cross-validation 5-fold di data latih (mean +/- std) --")
    for s, v in r['cv_metrics'].items():
        print(f"  {s:18s}: {v['mean']:.3f} +/- {v['std']:.3f}")

    print("\n-- Data uji (tidak pernah dipakai saat training) --")
    print(f"  {'':18s}  {'Model':>7s}  {'Baseline':>8s}")
    for k in ['accuracy', 'balanced_accuracy', 'sensitivity']:
        print(f"  {k:18s}: {t[k]:7.3f}  {b[k]:8.3f}")
    for k in ['specificity', 'precision', 'f1', 'roc_auc', 'pr_auc']:
        print(f"  {k:18s}: {t[k]:7.3f}")
    print("  (Baseline = selalu menebak kelas mayoritas)")

    print("\n-- Confusion matrix (data uji) --")
    print(f"  {'':16s}  Prediksi Low  Prediksi High")
    print(f"  {'Aktual Low':16s}  {cm['tn']:12d}  {cm['fp']:13d}")
    print(f"  {'Aktual High':16s}  {cm['fn']:12d}  {cm['tp']:13d}")
    print("=" * 58)


if __name__ == '__main__':
    print_report(train_and_evaluate())
