# app/routes/ml_routes.py - UPDATED VERSION
from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime

ml_bp = Blueprint('ml', __name__)


def get_ml_service():
    """Get ML service from app context"""
    from flask import current_app
    return current_app.config.get('ml_service')


@ml_bp.route('/api/ml/train', methods=['POST'])
def train_model():
    """Train ML model with real data"""
    try:
        ml_service = get_ml_service()

        if ml_service is None:
            return jsonify({"status": "error", "message": "ML service not initialized"})

        result = ml_service.train_model()
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@ml_bp.route('/api/ml/status', methods=['GET'])
def get_ml_status():
    """Get ML service status"""
    try:
        ml_service = get_ml_service()

        if ml_service is None:
            return jsonify({
                "training_status": "not_initialized",
                "model_accuracy": 0,
                "total_predictions": 0,
                "recent_anomalies": 0,
                "is_detecting": False
            })

        # Get current status from ML service
        training_status = getattr(ml_service, 'training_status', 'not_trained')
        total_predictions = len(getattr(ml_service, 'predictions', []))

        # Calculate recent anomalies
        recent_predictions = getattr(ml_service, 'predictions', [])[-20:]
        recent_anomalies = len([p for p in recent_predictions if p.get('is_anomaly', False)])

        # Check if detection is running
        is_detecting = getattr(ml_service, 'is_detecting', False)
        prediction_thread = getattr(ml_service, 'prediction_thread', None)

        # Verify thread is actually alive
        if is_detecting and prediction_thread and not prediction_thread.is_alive():
            is_detecting = False
            ml_service.is_detecting = False  # Update the flag

        # Get accuracy from logs
        accuracy = 0
        ml_logs_path = "data/ml_logs.json"
        if os.path.exists(ml_logs_path):
            try:
                with open(ml_logs_path, 'r') as f:
                    data = json.load(f)
                accuracy = data.get('model_metrics', {}).get('accuracy', 0)
            except:
                pass

        return jsonify({
            "training_status": training_status,
            "model_accuracy": accuracy,
            "total_predictions": total_predictions,
            "recent_anomalies": recent_anomalies,
            "is_detecting": is_detecting
        })

    except Exception as e:
        return jsonify({
            "training_status": "error",
            "model_accuracy": 0,
            "total_predictions": 0,
            "recent_anomalies": 0,
            "is_detecting": False,
            "error": str(e)
        })

@ml_bp.route('/api/ml/predictions', methods=['GET'])
def get_predictions():
    """Get ML predictions"""
    try:
        ml_service = get_ml_service()

        if ml_service is None:
            return jsonify({"status": "error", "message": "ML service not initialized"})

        limit = request.args.get('limit', 20, type=int)
        predictions = getattr(ml_service, 'predictions', [])[-limit:]

        return jsonify({
            "recent_predictions": predictions,
            "total_predictions": len(getattr(ml_service, 'predictions', [])),
            "recent_anomalies": len([p for p in predictions if p.get('is_anomaly', False)])
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@ml_bp.route('/api/ml/metrics', methods=['GET'])
def get_metrics():
    """Get ML model metrics"""
    try:
        ml_logs_path = "data/ml_logs.json"

        if not os.path.exists(ml_logs_path):
            return jsonify({
                "model_metrics": {
                    "accuracy": 0,
                    "precision": 0,
                    "recall": 0,
                    "f1_score": 0,
                    "last_trained": None,
                    "features": []
                },
                "total_training_runs": 0
            })

        with open(ml_logs_path, 'r') as f:
            data = json.load(f)

        metrics = data.get('model_metrics', {})
        training_history = data.get('training_history', [])

        return jsonify({
            "model_metrics": {
                "accuracy": metrics.get('accuracy', 0),
                "precision": metrics.get('precision', 0),
                "recall": metrics.get('recall', 0),
                "f1_score": metrics.get('f1_score', 0),
                "last_trained": metrics.get('last_trained'),
                "features": metrics.get('features_used', [])
            },
            "total_training_runs": len(training_history)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@ml_bp.route('/api/ml/start-detection', methods=['POST'])
def start_detection():
    """Start ML anomaly detection - IMPROVED VERSION"""
    try:
        ml_service = get_ml_service()

        if ml_service is None:
            return jsonify({"status": "error", "message": "ML service not initialized"})

        # NAYA: Better status checking
        training_status = getattr(ml_service, 'training_status', 'not_trained')
        is_trained = getattr(ml_service, 'is_trained', False)

        if training_status != 'trained' or not is_trained:
            return jsonify({
                "status": "error",
                "message": "ML model not trained. Please train the model first.",
                "current_status": training_status
            })

        # Check if detection is already running
        is_detecting = getattr(ml_service, 'is_detecting', False)
        prediction_thread = getattr(ml_service, 'prediction_thread', None)

        if is_detecting and prediction_thread and prediction_thread.is_alive():
            return jsonify({
                "status": "success",
                "message": "ML detection already running"
            })

        # Start background detection
        result = ml_service.start_detection()
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@ml_bp.route('/api/ml/stop-detection', methods=['POST'])
def stop_detection():
    """Stop ML anomaly detection"""
    try:
        ml_service = get_ml_service()

        if ml_service is None:
            return jsonify({"status": "error", "message": "ML service not initialized"})

        # Stop detection
        result = ml_service.stop_detection()
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

