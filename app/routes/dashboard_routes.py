from flask import Blueprint, render_template, jsonify, current_app
import datetime

# Blueprint define keren
dashboard_bp = Blueprint('dashboard', __name__)


def get_simblock_service():
    """Get simblock service from app context"""
    return current_app.config['simblock_service']


def get_attack_service():
    """Get attack service from app context"""
    return current_app.config['attack_service']


def get_ml_service():
    """Get ml service from app context"""
    return current_app.config['ml_service']


@dashboard_bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@dashboard_bp.route('/api/dashboard/status')
def dashboard_status():
    """Dashboard ke liye live data API"""
    simblock_service = get_simblock_service()
    attack_service = get_attack_service()
    ml_service = get_ml_service()

    simblock_status = simblock_service.get_status()

    # Get ML status
    ml_status = "not_trained"
    if ml_service and hasattr(ml_service, 'training_status'):
        ml_status = ml_service.training_status

    # Get last attack info
    active_attacks = attack_service.get_active_attacks()
    last_attack = "none"
    if active_attacks:
        last_attack = active_attacks[-1]['type'].replace('_', ' ').title()

    return jsonify({
        'status': 'running',
        'timestamp': datetime.datetime.now().isoformat(),
        'blockchain': simblock_status['blockchain_data'],
        'system': {
            'simulation': simblock_status['status'],
            'ml_model': ml_status,
            'last_attack': last_attack
        }
    })