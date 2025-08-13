# ✅ yodlee_routes.py
from flask import Blueprint, request, jsonify
from yodlee_client import (
    get_access_token,
    login_user,
    fetch_transactions,
    fetch_holdings,
    fetch_networth,
)

yodlee_data_bp = Blueprint("yodlee_data", __name__)

@yodlee_data_bp.route("/yodlee/transactions", methods=["POST"])
def get_transactions():
    data = request.get_json()
    username = data.get("username")
    from_date = data.get("fromDate")
    to_date = data.get("toDate")

    app_token = get_access_token()
    user_session = login_user(app_token, username)

    result = fetch_transactions(app_token, username, from_date, to_date)
    return jsonify(result)

@yodlee_data_bp.route("/yodlee/holdings", methods=["POST"])
def get_holdings():
    data = request.get_json()
    username = data.get("username")

    app_token = get_access_token()
    user_session = login_user(app_token, username)

    result = fetch_holdings(app_token, username)
    return jsonify(result)

@yodlee_data_bp.route("/yodlee/networth", methods=["POST"])
def get_networth():
    data = request.get_json()
    username = data.get("username")

    app_token = get_access_token()
    user_session = login_user(app_token, username)

    result = fetch_networth(app_token, username)
    return jsonify(result)
