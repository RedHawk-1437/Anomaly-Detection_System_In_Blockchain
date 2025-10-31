from flask import Blueprint, jsonify, request, current_app

simblock_bp = Blueprint('simblock', __name__)


def get_simblock_service():
    """Get simblock service from app context"""
    return current_app.config['simblock_service']


@simblock_bp.route('/api/simblock/start', methods=['POST'])
def start_simulation():
    """SimBlock simulation start keren"""
    simblock_service = get_simblock_service()
    data = request.get_json() or {}
    node_count = data.get('node_count', 100)

    result = simblock_service.start_simulation(node_count)
    return jsonify(result)


@simblock_bp.route('/api/simblock/stop', methods=['POST'])
def stop_simulation():
    """SimBlock simulation stop keren"""
    simblock_service = get_simblock_service()
    result = simblock_service.stop_simulation()
    return jsonify(result)


@simblock_bp.route('/api/simblock/status')
def get_simulation_status():
    """Current simulation status get keren"""
    simblock_service = get_simblock_service()
    status = simblock_service.get_status()
    return jsonify(status)


@simblock_bp.route('/api/simblock/stats')
def get_simulation_stats():
    """Detailed simulation statistics"""
    simblock_service = get_simblock_service()
    status = simblock_service.get_status()

    return jsonify({
        "simulation": {
            "status": status["status"],
            "running": status["is_running"]
        },
        "blockchain": status["blockchain_data"],
        "network": {
            "hash_rate": "15.6 TH/s",
            "difficulty": "18.5T",
            "block_time": "12.5s"
        }
    })