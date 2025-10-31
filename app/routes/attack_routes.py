from flask import Blueprint, jsonify, request, current_app
from app.services.attack_service import AttackType

attack_bp = Blueprint('attack', __name__)


def get_attack_service():
    """Get attack service from app context"""
    return current_app.config['attack_service']


@attack_bp.route('/api/attack/double-spending', methods=['POST'])
def start_double_spending():
    """Start Double Spending Attack"""
    attack_service = get_attack_service()
    data = request.get_json() or {}

    result = attack_service.start_attack(
        AttackType.DOUBLE_SPENDING,
        {
            'amount': data.get('amount', 100),
            'attacker_nodes': data.get('attacker_nodes', 5)
        }
    )
    return jsonify(result)


@attack_bp.route('/api/attack/51-percent', methods=['POST'])
def start_51_percent():
    """Start 51% Attack"""
    attack_service = get_attack_service()
    data = request.get_json() or {}

    result = attack_service.start_attack(
        AttackType.FIFTY_ONE_PERCENT,
        {
            'hash_power': data.get('hash_power', 55),
            'duration': data.get('duration', 60)
        }
    )
    return jsonify(result)


@attack_bp.route('/api/attack/selfish-mining', methods=['POST'])
def start_selfish_mining():
    """Start Selfish Mining Attack"""
    attack_service = get_attack_service()
    data = request.get_json() or {}

    result = attack_service.start_attack(
        AttackType.SELFISH_MINING,
        {
            'max_blocks': data.get('max_blocks', 3)
        }
    )
    return jsonify(result)


@attack_bp.route('/api/attack/eclipse', methods=['POST'])
def start_eclipse_attack():
    """Start Eclipse Attack"""
    attack_service = get_attack_service()
    data = request.get_json() or {}

    result = attack_service.start_attack(
        AttackType.ECLIPSE_ATTACK,
        {
            'target_node': data.get('target_node', 25),
            'attacker_nodes': data.get('attacker_nodes', 8),
            'isolation_time': data.get('isolation_time', 45)
        }
    )
    return jsonify(result)


@attack_bp.route('/api/attack/active', methods=['GET'])
def get_active_attacks():
    """Get currently active attacks"""
    attack_service = get_attack_service()
    active_attacks = attack_service.get_active_attacks()
    return jsonify({"active_attacks": active_attacks})


@attack_bp.route('/api/attack/stats', methods=['GET'])
def get_attack_stats():
    """Get attack statistics"""
    attack_service = get_attack_service()
    stats = attack_service.get_attack_stats()
    return jsonify(stats)


@attack_bp.route('/api/attack/stop/<attack_id>', methods=['POST'])
def stop_attack(attack_id):
    """Stop a specific attack"""
    attack_service = get_attack_service()
    result = attack_service.stop_attack(attack_id)
    return jsonify(result)