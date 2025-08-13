# ✅ Updated: finance_tools.py
import re
from datetime import datetime
from firebase_config import db

# 🔍 Detect and route financial logic
# def try_financial_logic(message: str, uid=None):
#     if "sip" in message.lower() or "निवेश" in message:
#         return detect_sip(message)
#     if "loan" in message.lower() or "emi" in message.lower():
#         return detect_loan(message)
#     if "net worth" in message.lower() or "कुल संपत्ति" in message:
#         return detect_net_worth(message)
#     if "goal" in message.lower() or "save" in message.lower() or "बचत" in message:
#         return goal_saving_prediction(message, uid)
#     return None

# 🧾 Spending Summary with Alerts
def try_financial_logic(query):
    # logic here
    return "some response"

def summarize_spending(transactions):
    # logic here
    return "some summary"
def summarize_spending(transactions, spending_limit=10000):
    categories = {}
    alerts = []
    total_spent = 0

    for txn in transactions.get("transaction", []):
        amount = abs(txn.get("amount", 0))
        cat = txn.get("category", "Other")
        categories[cat] = categories.get(cat, 0) + amount
        total_spent += amount

    summary = "🧾 90-Day Spending Summary:\n"
    for cat, amt in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        summary += f"- {cat}: ₹{round(amt, 2)}\n"
        if amt > spending_limit:
            alerts.append(f"⚠️ High spending on {cat}: ₹{round(amt)}")

    summary += f"\n💰 Total spent: ₹{round(total_spent)}"

    if alerts:
        summary += "\n\n🚨 Alerts:\n" + "\n".join(alerts)

    # return both summary and data
    return summary, categories, total_spent

# 🎯 Predict goal-based savings and store to Firestore
def goal_saving_prediction(message, uid=None):
    r = 0.12 / 12  # 12% annual default monthly return
    goal_match = re.search(r'goal.*?(\d{4,9})', message)
    save_match = re.search(r'(save|invest|बचत).*?(\d{3,6})', message)
    years_match = re.search(r'(\d{1,2})\s*(saal|years)', message)

    fv = int(goal_match.group(1)) if goal_match else None
    pmt = int(save_match.group(2)) if save_match else None
    n = int(years_match.group(1)) * 12 if years_match else None

    reply = None
    save_record = {}

    if fv and n and not pmt:
        pmt_required = fv / (((1 + r)**n - 1) / r * (1 + r))
        reply = f"🧮 To reach ₹{fv} in {n//12} years, save ₹{round(pmt_required)} per month."
        save_record = {"goal_amount": fv, "monthly_save": round(pmt_required), "duration_months": n}

    elif pmt and n and not fv:
        fv_calculated = pmt * (((1 + r)**n - 1) / r) * (1 + r)
        reply = f"📈 If you save ₹{pmt}/month for {n//12} years, you’ll have approx ₹{round(fv_calculated)}."
        save_record = {"goal_amount": round(fv_calculated), "monthly_save": pmt, "duration_months": n}

    elif pmt and fv and not n:
        months = 1
        while True:
            future_val = pmt * (((1 + r)**months - 1) / r) * (1 + r)
            if future_val >= fv:
                break
            months += 1
            if months > 600:
                return "❌ Goal not reachable in a reasonable time."
        years = months // 12
        rem_months = months % 12
        reply = f"⏳ With ₹{pmt}/month, you'll reach ₹{fv} in approx {years} years and {rem_months} months."
        save_record = {"goal_amount": fv, "monthly_save": pmt, "duration_months": months}

    # ✅ Save to Firestore if uid is present
    if uid and save_record:
        save_record.update({
            "start_date": datetime.utcnow(),
            "progress_percent": 0,
            "status": "ongoing"
        })
        db.collection("users").document(uid).collection("goals").add(save_record)

    return reply
