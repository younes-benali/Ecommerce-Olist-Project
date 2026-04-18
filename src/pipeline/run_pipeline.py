# src/pipeline/run_pipeline.py
import sys
import logging
from pathlib import Path

# Add project root to path (in case script is run directly)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.preprocessing import build_order_summary
from src.features import build_feature_set
from src.model import train_model
from src.evaluate import evaluate_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_full_pipeline(skip_preprocessing=False, skip_features=False, skip_training=False, skip_evaluation=False):
    """
    Execute the complete ML pipeline.
    
    Args:
        skip_preprocessing: If True, assume order_summary_clean.csv already exists
        skip_features: If True, assume feature_engineered_data.csv already exists
        skip_training: If True, assume model.pkl already exists
        skip_evaluation: If True, skip evaluation step
    """
    logger.info("=" * 60)
    logger.info("Starting Olist Delivery Prediction Pipeline")
    logger.info("=" * 60)
    
    try:
        # Step 1: Build clean order summary
        if not skip_preprocessing:
            logger.info("Step 1/4: Building clean order summary...")
            build_order_summary(save_csv=True)
            logger.info("Step 1 completed.")
        else:
            logger.info("Step 1 skipped (using existing order_summary_clean.csv).")
        
        # Step 2: Feature engineering
        if not skip_features:
            logger.info("Step 2/4: Engineering features...")
            build_feature_set(save_csv=True)
            logger.info("Step 2 completed.")
        else:
            logger.info("Step 2 skipped (using existing feature_engineered_data.csv).")
        
        # Step 3: Train model
        if not skip_training:
            logger.info("Step 3/4: Training XGBoost model...")
            model, X_test, y_test = train_model(save_model=True)
            logger.info("Step 3 completed.")
        else:
            logger.info("Step 3 skipped (using existing model.pkl).")
            model = None
        
        # Step 4: Evaluate
        if not skip_evaluation:
            logger.info("Step 4/4: Evaluating model...")
            metrics = evaluate_model(save_results=True)
            logger.info(f"Evaluation completed. ROC AUC: {metrics['roc_auc']:.4f}")
        else:
            logger.info("Step 4 skipped.")
        
        logger.info("=" * 60)
        logger.info("Pipeline finished successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Olist ML pipeline")
    parser.add_argument("--skip-preprocessing", action="store_true", help="Skip cleaning step")
    parser.add_argument("--skip-features", action="store_true", help="Skip feature engineering step")
    parser.add_argument("--skip-training", action="store_true", help="Skip model training step")
    parser.add_argument("--skip-evaluation", action="store_true", help="Skip evaluation step")
    
    args = parser.parse_args()
    
    run_full_pipeline(
        skip_preprocessing=args.skip_preprocessing,
        skip_features=args.skip_features,
        skip_training=args.skip_training,
        skip_evaluation=args.skip_evaluation
    )