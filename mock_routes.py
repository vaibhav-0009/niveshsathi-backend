from flask import Blueprint, jsonify
from mock_data import mock_user_data

mock_bp = Blueprint("mock", __name__)

@mock_bp.route('/mock/networth/<user_id>')
def networth(user_id):
    user = mock_user_data.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    total_assets = sum([a["balance"] for a in user["bank_accounts"]]) + sum([i["amount"] for i in user["investments"]])
    total_loans = sum([l["amount"] for l in user["loans"]])
    networth = total_assets - total_loans

    return jsonify({
        "assets": total_assets,
        "loans": total_loans,
        "networth": networth
    })
