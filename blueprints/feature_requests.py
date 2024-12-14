from flask import Blueprint, request, jsonify
import csv
import os
from datetime import datetime
from .utils import append_csv

feature_requests_bp = Blueprint("feature_requests", __name__)

FEATURE_REQUESTS_FILE = "./data/feature_requests.csv"

# Ensure necessary files exist
os.makedirs(os.path.dirname(FEATURE_REQUESTS_FILE), exist_ok=True)
if not os.path.exists(FEATURE_REQUESTS_FILE):
    with open(FEATURE_REQUESTS_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "description", "priority", "date_submitted"])
        writer.writeheader()

@feature_requests_bp.route("/submit", methods=["POST"])
def submit_feature_request():
    """Submit a feature request."""
    try:
        data = {
            "title": request.json.get("title", ""),
            "description": request.json.get("description", ""),
            "priority": request.json.get("priority", ""),
            "date_submitted": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }
        append_csv(FEATURE_REQUESTS_FILE, data, fieldnames=data.keys())
        return jsonify({"message": "Feature request submitted successfully!"})
    except Exception as e:
        return jsonify({"error": f"Failed to submit feature request: {str(e)}"}), 500

@feature_requests_bp.route("/", methods=["GET"])
def get_feature_requests():
    """Fetch all feature requests."""
    try:
        with open(FEATURE_REQUESTS_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            requests = [row for row in reader]
        return jsonify(requests), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve feature requests: {str(e)}"}), 500