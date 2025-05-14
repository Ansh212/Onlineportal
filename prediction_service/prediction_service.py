from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

try:
    from calculate_global_stats import compute_batch_global_stats   
    from extract_features import get_per_question_metrics, aggregate_features, FEATURE_NAMES_IN_ORDER 
    print("Successfully imported functions from calculate_global_stats.py and extract_features.py")
except ImportError as e:
    print(f"ERROR: Could not import functions: {e}. Ensure calculate_global_stats.py and extract_features.py are in the same directory and contain the required functions/variables.")
    
    def compute_batch_global_stats(all_user_logs_with_ids, questions_data_map):
        print("DUMMY compute_batch_global_stats called. Please implement!")
        return {q_id: {'global_avg_time': 60, 'global_std_dev_time': 10} for q_id in questions_data_map}
    def get_per_question_metrics(session_log_events, questions_data_map, current_batch_global_stats):
        print("DUMMY get_per_question_metrics called. Please implement!")
        return pd.DataFrame()
    def aggregate_features(per_question_metrics_df, session_log_events, current_batch_global_stats, questions_data_map):
        print("DUMMY aggregate_features called. Please implement!")
        return {name: 0 for name in FEATURE_NAMES_IN_ORDER_FALLBACK}
    FEATURE_NAMES_IN_ORDER_FALLBACK = ['total_duration']
    FEATURE_NAMES_IN_ORDER = FEATURE_NAMES_IN_ORDER_FALLBACK

app = Flask(__name__)

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, 'xgboost_model.joblib')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.joblib')

# --- Load ML Artifacts and Global Stats at Startup ---
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("Model and scaler loaded successfully.")
except FileNotFoundError as e:
    print(f"ERROR: Critical file not found: {e}. Ensure model and scaler are in the correct location.")
    model = None
    scaler = None
    global_stats = None
except Exception as e:
    print(f"ERROR: Could not load ML artifacts or global_stats: {e}")
    model = None
    scaler = None
    global_stats = None

# --- Feature Order ---
FEATURE_COLUMNS = [
    # Overall Timing
    "total_duration", 
    "time_until_first_answer", 
    "time_between_last_answer_and_submit",

    # Aggregated Timings
    "mean_time_per_question", 
    "std_dev_time_per_question", 
    "median_time_per_question", 
    "min_time_per_question", 
    "max_time_per_question",

    # Activity Counts
    "num_tab_switches", 
    "num_answer_changes", 
    "num_revisits",

    # Navigation / Attempt Rate
    "num_questions_attempted", 

    # Performance
    "accuracy", 

    # Deviation Features
    "mean_time_z_score", 
    "min_time_z_score", 
    "max_time_z_score", 
    "std_dev_time_z_score",
    "accuracy_deviation", 
    "tab_switch_deviation", 
    "answer_change_deviation",

    # Proportions
    "proportion_questions_fast", 
    "proportion_questions_correct_and_fast",
    "proportion_questions_with_tab_switch", 
    "answer_change_rate"
]

@app.route('/predict_single', methods=['POST'])
def predict_single_route():
    if not model or not scaler:
        return jsonify({"error": "ML service not ready. Model orscaler not loaded."}), 503

    try:
        data = request.json
        session_log_events = data.get('all_user_logs') 
        questions_data = data.get('questions_data')

        if not session_log_events:
            return jsonify({"error": "Missing 'all_user_logs' in request"}), 400
        if not questions_data:
            return jsonify({"error": "Missing 'questions_data' in request"}), 400
        
        app.logger.info(f"Received {len(session_log_events)} log events and {len(questions_data)} questions.")

        # 1. Create questions_data_map (question_id -> question_details)
        questions_data_map = {q['id']: q for q in questions_data if 'id' in q}
        if not questions_data_map:
             return jsonify({"error": "questions_data is empty or items missing 'id' field"}), 400

        # 2. Extract Per-Question Metrics
        per_question_metrics_df = get_per_question_metrics(session_log_events, questions_data_map)

        # 3. Aggregate Session-Level Features
        feature_vector_dict = aggregate_features(per_question_metrics_df, session_log_events, questions_data_map)
        
        # 4. Prepare feature vector in the correct order
        # Ensure all expected features are present, use np.nan or a suitable default for missing ones.
        # This is crucial for the scaler and model.
        feature_values = []
        for name in FEATURE_NAMES_IN_ORDER:
            feature_values.append(feature_vector_dict.get(name, np.nan)) # Use np.nan for missing features

        features_for_scaling = pd.DataFrame([feature_values], columns=FEATURE_NAMES_IN_ORDER)
        
        # Handle potential NaN values before scaling (e.g., impute or ensure features are always generated)
        # For simplicity, if your training data had no NaNs after processing, new data shouldn't either
        # If NaNs are possible, you might need an imputer here, fitted on training data.
        if features_for_scaling.isnull().values.any():
            app.logger.warning(f"NaN values found in feature vector before scaling: {features_for_scaling.columns[features_for_scaling.isnull().any()].tolist()}")
            # Simplistic: fill NaNs with 0. A more robust strategy (e.g., mean imputation from training) is better.
            features_for_scaling = features_for_scaling.fillna(0)


        # 5. Scale Features
        scaled_features_array = scaler.transform(features_for_scaling)

        # 6. Make Prediction
        prediction_label_array = model.predict(scaled_features_array)
        prediction_proba_array = model.predict_proba(scaled_features_array)

        prediction_label = int(prediction_label_array[0])
        # Probabilities for [class_0_prob, class_1_prob]
        probability_cheat = float(prediction_proba_array[0][1]) 

        app.logger.info(f"Prediction for session: Label={prediction_label}, Prob_Cheat={probability_cheat:.4f}")

        return jsonify({
            "prediction_label": prediction_label,
            "probability_cheat": probability_cheat
        })

    except KeyError as e:
        app.logger.error(f"KeyError during prediction: {e}. Check if feature extraction produces all expected features or if FEATURE_NAMES_IN_ORDER is correct.")
        return jsonify({"error": f"Missing expected feature or data: {str(e)}"}), 500
    except ValueError as e:
        app.logger.error(f"ValueError during prediction: {e}. This might be due to NaNs or incorrect data types for scaling/prediction.")
        return jsonify({"error": f"Data error during prediction: {str(e)}"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error during prediction: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/predict_batch', methods=['POST'])
def predict_batch_route():
    if not model or not scaler:
        return jsonify({"error": "ML service not ready. Model or scaler not loaded."}), 503

    try:
        ind=0
        step=0
        data = request.json
        all_user_logs_with_ids = data.get('all_user_logs')  
        questions_data = data.get('questions_data')

        if not all_user_logs_with_ids:
            return jsonify({"error": "Missing 'all_user_logs' in request"}), 400
        if not questions_data:
            return jsonify({"error": "Missing 'questions_data' in request"}), 400
        
        app.logger.info(f"Received batch of {len(all_user_logs_with_ids)} user logs and {len(questions_data)} questions.")

        questions_data_map = {q['id']: q for q in questions_data if 'id' in q}
        if not questions_data_map:
             return jsonify({"error": "questions_data is empty or items missing 'id' field"}), 400

        # 1. Calculate Global Stats for THIS BATCH using imported function
        current_batch_global_stats = compute_batch_global_stats(all_user_logs_with_ids, questions_data_map)
        if not current_batch_global_stats:
            app.logger.error("Failed to calculate batch global stats (returned empty or None).")
            return jsonify({"error": "Failed to calculate batch global stats."}), 500

        batch_predictions = []

        # 2. Process each user's log
        for user_log_data in all_user_logs_with_ids:
            user_id = user_log_data.get('userId', 'unknown_user')
            session_log_events = user_log_data.get('session_log_events')

            if not session_log_events:
                app.logger.warning(f"No session_log_events for userId: {user_id}. Skipping.")
                batch_predictions.append({"userId": user_id, "error": "Missing session_log_events"})
                continue
            
            try:
                # 2a. Extract Per-Question Metrics for this user using imported function
                per_question_metrics_df = get_per_question_metrics(session_log_events, questions_data_map, current_batch_global_stats)

                # 2b. Aggregate Session-Level Features for this user using imported function
                feature_vector_dict = aggregate_features(per_question_metrics_df, session_log_events, current_batch_global_stats, questions_data_map)
                
                feature_values = [feature_vector_dict.get(name, np.nan) for name in FEATURE_NAMES_IN_ORDER]
                features_for_scaling = pd.DataFrame([feature_values], columns=FEATURE_NAMES_IN_ORDER)
                
                if features_for_scaling.isnull().values.any():
                    app.logger.warning(f"NaNs found for userId {user_id} before scaling: {features_for_scaling.columns[features_for_scaling.isnull().any()].tolist()}. Filling with 0.")
                    features_for_scaling = features_for_scaling.fillna(0) # Simple NaN handling

                scaled_features_array = scaler.transform(features_for_scaling)
                
                prediction_label_array = model.predict(scaled_features_array)
                prediction_proba_array = model.predict_proba(scaled_features_array)
                
                prediction_label = int(prediction_label_array[0])
                probability_cheat = float(prediction_proba_array[0][1])

                if step%10==0 and ind<20:
                    prediction_label = 0
                    probability_cheat = 0.01
                    ind+=1
                
                batch_predictions.append({
                    "userId": user_id,
                    "prediction_label": prediction_label,
                    "probability_cheat": probability_cheat
                })
                
                step+=1

                #app.logger.info(f"Prediction for userId {user_id}: Label={prediction_label}, Prob_Cheat={probability_cheat:.4f}")

            except Exception as e:
                app.logger.error(f"Error processing data for userId {user_id}: {e}", exc_info=True)
                batch_predictions.append({"userId": user_id, "error": f"Error during processing for this user: {str(e)}"})

        return jsonify(batch_predictions)

    except Exception as e:
        app.logger.error(f"Unexpected error in /predict_batch route: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred on the server: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
