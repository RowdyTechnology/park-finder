from flask import Blueprint, render_template

utility_pages_bp = Blueprint("utility_pages", __name__)

@utility_pages_bp.route("/")
def home():
    return render_template("index.html")

@utility_pages_bp.route("/parks")
def parks_page():
    return render_template("parks.html")

@utility_pages_bp.route("/feature_request")
def feature_request_page():
    return render_template("feature_request.html")

@utility_pages_bp.route("/view_feature_requests")
def view_feature_requests_page():
    return render_template("view_feature_requests.html")

@utility_pages_bp.route("/user_stats")
def user_stats_page():
    return render_template("user_stats.html")