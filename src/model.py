import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import xgboost as xgb
from src.config import DATA_PROCESSED, MODELS_DIR

def train_model(save_model=True):
    
    print("Loading feature set...")
    df = pd.read_csv(DATA_PROCESSED / "feature_engineered_data.csv")
    
    # Target column
    target = "is_late"
    X = df.drop(columns=[target])
    y = df[target]
    
    print(f"Dataset shape: {X.shape}")
    print(f"Target distribution:\n{y.value_counts()}")
    
    # Train/test split (stratify to preserve imbalance)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train size: {X_train.shape}, Test size: {X_test.shape}")
    
    # Calculate scale_pos_weight for imbalance (negative/positive ratio)
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1
    print(f"Scale pos weight: {scale_pos_weight:.2f}")
    
    # XGBoost classifier
    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric='logloss',
        use_label_encoder=False
    )
    
    print("Training XGBoost model...")
    model.fit(X_train, y_train)
    
    # Evaluation
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred))
    
    print(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model
    if save_model:
        model_path = MODELS_DIR / "model.pkl"
        joblib.dump(model, model_path)
        print(f"\nModel saved to {model_path}")
    
    return model, X_test, y_test

if __name__ == "__main__":
    train_model()