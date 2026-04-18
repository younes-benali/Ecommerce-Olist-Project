import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    ConfusionMatrixDisplay
)
import joblib
from src.config import DATA_PROCESSED, MODELS_DIR, REPORTS_METRICS, REPORTS_FIGURES

def evaluate_model(save_results=True):
    
    print("Loading feature set...")
    df = pd.read_csv(DATA_PROCESSED / "feature_engineered_data.csv")
    
    target = "is_late"
    X = df.drop(columns=[target])
    y = df[target]
    
    print(f"Dataset shape: {X.shape}")
    
    # Use same split as model.py (must match random_state=42, stratify)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Test set size: {X_test.shape[0]}")
    
    # Load model
    model_path = MODELS_DIR / "model.pkl"
    print(f"Loading model from {model_path}")
    model = joblib.load(model_path)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Metrics
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    print(f"ROC AUC: {roc_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save metrics as JSON
    if save_results:
        metrics = {
            "roc_auc": roc_auc,
            "accuracy": report["accuracy"],
            "precision_class_1": report["1"]["precision"],
            "recall_class_1": report["1"]["recall"],
            "f1_class_1": report["1"]["f1-score"],
            "support_class_0": int(report["0"]["support"]),
            "support_class_1": int(report["1"]["support"])
        }
        metrics_path = REPORTS_METRICS / "metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=4)
        print(f"Metrics saved to {metrics_path}")
    
    # ---- Plot 1: Confusion Matrix ----
    fig, ax = plt.subplots(figsize=(6, 5))
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["On Time", "Late"])
    disp.plot(ax=ax, cmap="Blues", values_format="d")
    ax.set_title("Confusion Matrix")
    plt.tight_layout()
    if save_results:
        plt.savefig(REPORTS_FIGURES / "confusion_matrix.png", dpi=150)
        print(f"Saved confusion matrix to {REPORTS_FIGURES / 'confusion_matrix.png'}")
    plt.show()
    
    # ---- Plot 2: ROC Curve ----
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, label=f"XGBoost (AUC = {roc_auc:.3f})", linewidth=2)
    ax.plot([0, 1], [0, 1], "k--", label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve")
    ax.legend()
    plt.tight_layout()
    if save_results:
        plt.savefig(REPORTS_FIGURES / "roc_curve.png", dpi=150)
        print(f"Saved ROC curve to {REPORTS_FIGURES / 'roc_curve.png'}")
    plt.show()
    
    # ---- Plot 3: Feature Importance (top 20) ----
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        feature_names = X.columns
        indices = np.argsort(importances)[::-1][:20]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(indices)), importances[indices], align="center")
        ax.set_yticks(range(len(indices)))
        ax.set_yticklabels([feature_names[i] for i in indices])
        ax.invert_yaxis()
        ax.set_xlabel("Feature Importance")
        ax.set_title("Top 20 Feature Importances")
        plt.tight_layout()
        if save_results:
            plt.savefig(REPORTS_FIGURES / "feature_importance.png", dpi=150)
            print(f"Saved feature importance plot to {REPORTS_FIGURES / 'feature_importance.png'}")
        plt.show()
    else:
        print("Model does not have feature_importances_ attribute")
    
    return metrics

if __name__ == "__main__":
    evaluate_model()