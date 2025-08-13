from flask import Flask, request, jsonify
from firebase_config import auth_client, db, init_firebase  # ✅ import init
from firebase_admin import auth, exceptions as firebase_exceptions
from flask_cors import CORS
from ai_logic import get_ai_reply
from finance_tools import try_financial_logic, summarize_spending
from yodlee_client import get_access_token, login_user, fetch_accounts  
from yodlee_client import get_access_token, login_user, fetch_networth, fetch_transactions
from datetime import datetime, timedelta
from mock_data import mock_user_data

# ✅ Initialize Firebase Admin SDK
init_firebase()

app = Flask(__name__)
CORS(app, origins=["http://10.9.3.100:3000"], supports_credentials=True) 


@app.route('/bank', methods=['POST'])
def get_bank_data():
    try:
        data = request.json
        id_token = data.get('idToken')

        if not id_token:
            return jsonify({"error": "Missing ID token"}), 401

        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']

        access_token = get_access_token()
        user_session = login_user(access_token)
        accounts = fetch_accounts(access_token, user_session)

        # 🧮 Calculate totals
        total_bank = 0
        total_investment = 0
        total_loan = 0

        for acc in accounts:
            balance = acc.get("balance", {}).get("amount", 0)
            acc_type = acc.get("accountType", "").upper()

            if acc_type == "BANK":
                total_bank += balance
            elif acc_type == "INVESTMENT":
                total_investment += balance
            elif acc_type == "LOAN":
                total_loan += balance

        net_worth = total_bank + total_investment - total_loan

        # ✅ Save or return
        result = {
            "bank": total_bank,
            "investment": total_investment,
            "loan": total_loan,
            "netWorth": net_worth,
        }

        db.collection("users").document(user_id).collection("networth_history").add({
            "timestamp": datetime.now(),
            **result
        })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({"message": "✅ NiveshSathi API is running."})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message")
    id_token = data.get("idToken")

    if not user_message or not id_token:
        return jsonify({"error": "Missing input"}), 400

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
    except firebase_exceptions.FirebaseError:
        return jsonify({"error": "Invalid token"}), 401

    # 🧠 Net Worth Logic
    if "net worth" in user_message.lower() or "कुल संपत्ति" in user_message:
        try:
            app_token = get_access_token()
            user_token = login_user(app_token, uid)
            networth_data = fetch_networth(app_token, uid)
            value = networth_data["networth"][0]["value"]
            currency = networth_data["networth"][0].get("currency", "INR")
            reply = f"🧠 Your live net worth is: ₹{value} {currency}"
        except:
            # Fallback to mock
            user = mock_user_data.get("user123")
            if user:
                total_assets = sum([a["balance"] for a in user["bank_accounts"]]) + \
                               sum([i["amount"] for i in user["investments"]])
                total_loans = sum([l["amount"] for l in user["loans"]])
                networth = total_assets - total_loans
                reply = f"🧪 (Mock) Your net worth is ₹{networth} (Assets: ₹{total_assets}, Loans: ₹{total_loans})"
            else:
                reply = "⚠️ Unable to fetch net worth from live or mock."

        save_to_history(uid, user_message, reply)
        return jsonify({"reply": reply})

    # 💸 Spending Summary
    if "spending" in user_message.lower() or "spent" in user_message.lower() or "खर्च" in user_message:
        try:
            app_token = get_access_token()
            user_token = login_user(app_token, uid)
            to_date = datetime.today().strftime("%Y-%m-%d")
            from_date = (datetime.today() - timedelta(days=90)).strftime("%Y-%m-%d")
            txn_data = fetch_transactions(app_token, uid, from_date, to_date)
            summary, cat_dict, total = summarize_spending(txn_data)

            db.collection("users").document(uid).collection("spending_trends").add({
                "from": from_date,
                "to": to_date,
                "categories": cat_dict,
                "total": total,
                "generated": datetime.utcnow()
            })
        except:
            # Mock fallback
            summary = "🧪 (Mock) Spending summary not available. Please try again later."

        save_to_history(uid, user_message, summary)
        return jsonify({"reply": summary})

    # 📈 SIP, Loan, Goal
    reply = try_financial_logic(user_message, uid)
    if reply:
        save_to_history(uid, user_message, reply)
        return jsonify({"reply": reply})

    # 🧠 AI fallback
    reply = get_ai_reply(user_message)
    save_to_history(uid, user_message, reply)
    return jsonify({"reply": reply})


@app.route('/goals', methods=['POST'])
def get_goals():
    data = request.get_json()
    id_token = data.get("idToken")
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
    except:
        return jsonify({"error": "Invalid ID token"}), 401

    goals_ref = db.collection("users").document(uid).collection("goals")
    docs = goals_ref.stream()
    goals = [{**doc.to_dict(), "id": doc.id} for doc in docs]
    return jsonify({"goals": goals})


@app.route('/mock/networth/<user_id>')
def mock_networth(user_id):
    user = mock_user_data.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    total_assets = sum([a["balance"] for a in user["bank_accounts"]]) + \
                   sum([i["amount"] for i in user["investments"]])
    total_loans = sum([l["amount"] for l in user["loans"]])
    networth = total_assets - total_loans

    return jsonify({
        "assets": total_assets,
        "loans": total_loans,
        "networth": networth
    })


def save_to_history(uid, question, answer):
    db.collection("users").document(uid).collection("chats").add({
        "question": question,
        "answer": answer,
        "timestamp": datetime.utcnow()
    })


if __name__ == '__main__':
    app.run(debug=True)
