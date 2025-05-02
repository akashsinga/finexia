# scripts/run_validation.py

import argparse
import pandas as pd
from datetime import datetime
from core.validate.prediction_tracker import update_prediction_results, analyze_prediction_timeframes, get_prediction_accuracy_by_symbol
from core.validate.model_evaluator import get_model_performance_metrics, identify_best_performing_models, identify_worst_performing_models
from core.validate.feedback_optimizer import analyze_optimal_parameters, retrain_with_feedback, batch_optimize_models

def log(msg): print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def run_validation():
    """Run the validation process to verify predictions and update model performance metrics."""
    log("Starting prediction validation...")
    verified, total = update_prediction_results()
    log(f"Verified {verified} out of {total} predictions")
    
    # Analyze accuracy
    df = get_prediction_accuracy_by_symbol()
    if not df.empty:
        log("\nPrediction Accuracy By Symbol:")
        log(df.sort_values('move_accuracy', ascending=False).head(10).to_string())
        
        # Show best and worst models
        best_models = identify_best_performing_models(min_accuracy=0.6)
        worst_models = identify_worst_performing_models(max_accuracy=0.4)
        
        log(f"\nBest performing models ({len(best_models)}):")
        log(", ".join(best_models[:10]))
        
        log(f"\nWorst performing models ({len(worst_models)}):")
        log(", ".join(worst_models[:10]))
    
    # Analyze prediction timeframes
    timeframes = analyze_prediction_timeframes()
    if timeframes:
        timeframe_df = pd.DataFrame.from_dict(timeframes, orient='index')
        log("\nPrediction Timeframes:")
        log(timeframe_df.sort_values('avg_days').head(10).to_string())
    
    return True

def optimize_single_model(symbol):
    """Analyze and optimize a single model."""
    # Analyze optimal parameters
    log(f"Analyzing optimal parameters for {symbol}...")
    params = analyze_optimal_parameters(symbol)
    
    log(f"Recommended parameters for {symbol}:")
    for key, value in params.items():
        log(f"  {key}: {value}")
    
    # Ask for confirmation
    confirm = input(f"\nDo you want to retrain {symbol} with these parameters? (y/n): ")
    
    if confirm.lower() == 'y':
        log(f"Retraining {symbol}...")
        success, result = retrain_with_feedback(symbol)
        
        if success:
            log(f"Successfully retrained {symbol}")
            if "training_result" in result:
                metrics = result["training_result"].get("move_metrics", {})
                log(f"Move model metrics: {metrics}")
                
                dir_metrics = result["training_result"].get("direction_metrics", {})
                if dir_metrics:
                    log(f"Direction model metrics: {dir_metrics}")
        else:
            log(f"Failed to retrain {symbol}: {result.get('error', 'unknown error')}")
    
    return True

def optimize_batch():
    """Optimize multiple models based on performance."""
    # Ask for batch size
    try:
        count = int(input("How many models to optimize? [5]: ") or "5")
    except ValueError:
        count = 5
    
    prioritize = input("Prioritize worst performing models? (y/n) [y]: ")
    prioritize = prioritize.lower() != 'n'
    
    log(f"Optimizing up to {count} models (prioritized: {prioritize})...")
    result = batch_optimize_models(max_symbols=count, prioritize=prioritize)
    
    log(f"Batch optimization completed: {result['status']}")
    if result["status"] == "completed":
        log(f"Successfully optimized {result['successful']}/{result['total']} models")
        
        # Show details for each symbol
        for symbol, data in result.get("details", {}).items():
            success = data.get("success", False)
            status = "✅" if success else "❌"
            log(f"{status} {symbol}: {data.get('parameters', {}).get('threshold_percent', 'N/A')}%")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run model validation and optimization tasks')
    parser.add_argument('--mode', choices=['validate', 'optimize', 'batch'], default='validate',
                        help='Mode to run: validate (check predictions), optimize (single model), batch (multiple models)')
    parser.add_argument('--symbol', help='Symbol to optimize (required for optimize mode)')
    
    args = parser.parse_args()
    
    if args.mode == 'validate':
        run_validation()
    elif args.mode == 'optimize':
        if not args.symbol:
            print("Error: --symbol is required for optimize mode")
            exit(1)
        optimize_single_model(args.symbol)
    elif args.mode == 'batch':
        optimize_batch()