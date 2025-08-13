from flask import Blueprint, request, jsonify
from firebase_admin import auth
from firebase_config import db
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

# ---- Signup ----
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({"error": "Missing email, password, or name"}), 400

    try:
        # Create user with Firebase Auth
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )

        # Store basic user info in Firestore
        db.collection("users").document(user.uid).set({
            "email": email,
            "name": name,
            "created": datetime.utcnow()
        })

        return jsonify({
            "message": "✅ Signup successful",
            "uid": user.uid
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ---- Update Password ----
@auth_bp.route("/update-password", methods=["POST"])
def update_password():
    data = request.get_json()
    id_token = data.get("idToken")
    new_password = data.get("new_password")

    if not id_token or not new_password:
        return jsonify({"error": "Missing ID token or new password"}), 400

    try:
        decoded = auth.verify_id_token(id_token)
        uid = decoded["uid"]

        # Update password using Admin SDK
        auth.update_user(uid, password=new_password)

        return jsonify({"message": "✅ Password updated successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to update password: {str(e)}"}), 400


# ---- Logout (revoke tokens) ----
@auth_bp.route("/logout", methods=["POST"])
def logout():
    data = request.get_json()
    id_token = data.get("idToken")

    if not id_token:
        return jsonify({"error": "Missing ID token"}), 400

    try:
        decoded = auth.verify_id_token(id_token)
        uid = decoded["uid"]

        # Revoke refresh tokens to logout user
        auth.revoke_refresh_tokens(uid)

        return jsonify({"message": "✅ User logged out successfully (tokens revoked)."})
    except Exception as e:
        return jsonify({"error": f"Failed to logout: {str(e)}"}), 400
