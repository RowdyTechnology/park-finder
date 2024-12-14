from flask import Flask
from blueprints.parks import parks_bp
from blueprints.feature_requests import feature_requests_bp
from blueprints.utility_pages import utility_pages_bp
from blueprints.user_stats import user_stats_bp
import os
import logging

# --------------------------
# Configuration and Setup
# --------------------------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__, static_folder="static", template_folder="templates")

# Configurations
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/mnt/user/appdata/parks/uploads")
CSV_FILE = os.getenv("CSV_FILE", "/mnt/user/appdata/parks/data.csv")
HOME_POINT_FILE = os.getenv("HOME_POINT_FILE", "/mnt/user/appdata/parks/home_point.csv")
FEATURE_REQUESTS_FILE = os.getenv("FEATURE_REQUESTS_FILE", "/mnt/user/appdata/parks/feature_requests.csv")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER  # Correctly configure app.config

# Ensure necessary folders and files exist
# Use os.path.join to create correct paths
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create uploads directory
os.makedirs(os.path.join(os.path.dirname(CSV_FILE)), exist_ok=True)  # Create data directory
os.makedirs(os.path.join(os.path.dirname(HOME_POINT_FILE)), exist_ok=True)  # Create data directory
os.makedirs(os.path.join(os.path.dirname(FEATURE_REQUESTS_FILE)), exist_ok=True)  # Create data directory

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "name",
                "latitude",
                "longitude",
                "crowd_rating",
                "obstacle_rating",
                "size_rating",
                "visibility_rating",
                "diversity_rating",
                "photo",
                "date_visited",
                "username",
            ],
        )
        writer.writeheader()
if not os.path.exists(HOME_POINT_FILE):
    with open(HOME_POINT_FILE, mode="w", newline="") as file:
        file.write("latitude,longitude\n")
if not os.path.exists(FEATURE_REQUESTS_FILE):
    with open(FEATURE_REQUESTS_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "title",
                "description",
                "priority",
                "date_submitted",
            ],
        )
        writer.writeheader()

# Register Blueprints
app.register_blueprint(parks_bp, url_prefix="/parks")
app.register_blueprint(feature_requests_bp, url_prefix="/feature_requests")
app.register_blueprint(utility_pages_bp)
app.register_blueprint(user_stats_bp, url_prefix="/user_stats")

# --------------------------
# Main Application
# --------------------------
if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8086, debug=debug_mode)