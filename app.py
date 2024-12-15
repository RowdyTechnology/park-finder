from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    render_template,
)
import csv
import os
import math
from datetime import datetime
from werkzeug.utils import secure_filename
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
HOME_POINT_FILE = os.getenv(
    "HOME_POINT_FILE", "/mnt/user/appdata/parks/home_point.csv"
)
FEATURE_REQUESTS_FILE = os.getenv(
    "FEATURE_REQUESTS_FILE", "/mnt/user/appdata/parks/feature_requests.csv"
)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure necessary folders and files exist
for path in [UPLOAD_FOLDER, CSV_FILE, HOME_POINT_FILE, FEATURE_REQUESTS_FILE]:
    os.makedirs(os.path.dirname(path), exist_ok=True)
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


# --------------------------
# Utility Functions
# --------------------------
def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def read_csv(file_path, fieldnames):
    """Generic function to read CSV data."""
    data = []
    if os.path.exists(file_path):
        with open(file_path, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data


def write_csv(file_path, data, fieldnames):
    """Generic function to write CSV data."""
    with open(file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def append_csv(file_path, data, fieldnames):
    """Append a single row to a CSV file."""
    with open(file_path, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(data)


def calculate_average_ratings(ratings):
    """Calculate the average rating from multiple categories."""
    valid_ratings = [r for r in ratings if isinstance(r, (int, float))]
    return (
        round(sum(valid_ratings) / len(valid_ratings), 2)
        if valid_ratings
        else 0
    )


# --------------------------
# Routes: Parks Management
# --------------------------
@app.route("/add_park", methods=["POST"])
def add_park():
    try:
        file = request.files.get("photo")
        filename = ""
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        ratings = {
            key: int(request.form[key])
            for key in [
                "crowd_rating",
                "obstacle_rating",
                "size_rating",
                "visibility_rating",
                "diversity_rating",
            ]
        }
        data = {
            "name": request.form["name"],
            "latitude": latitude,
            "longitude": longitude,
            "crowd_rating": ratings["crowd_rating"],
            "obstacle_rating": ratings["obstacle_rating"],
            "size_rating": ratings["size_rating"],
            "visibility_rating": ratings["visibility_rating"],
            "diversity_rating": ratings["diversity_rating"],
            "photo": f"/uploads/{filename}" if filename else "",
            "date_visited": request.form.get(
                "date_visited", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            ),
            "username": request.form.get("username", "Unknown"),
        }
        parks = read_csv(CSV_FILE, fieldnames=data.keys())
        parks.append(data)
        write_csv(CSV_FILE, parks, fieldnames=data.keys())
        return jsonify({"message": "Park added successfully!"})
    except Exception as e:
        logging.error(f"Error adding park: {e}")
        return jsonify({"error": "Failed to add park."}), 500


@app.route("/view_parks", methods=["GET"])
def view_parks():
    try:
        parks = read_csv(CSV_FILE, fieldnames=None)
        for park in parks:
            ratings = [
                int(park.get("crowd_rating", 0)),
                int(park.get("obstacle_rating", 0)),
                int(park.get("size_rating", 0)),
                int(park.get("visibility_rating", 0)),
                int(park.get("diversity_rating", 0)),
            ]
            park["average_rating"] = calculate_average_ratings(ratings)
        return jsonify(parks)
    except Exception as e:
        logging.error(f"Error retrieving parks: {e}")
        return jsonify({"error": "Failed to retrieve parks."}), 500


@app.route("/delete_park/<int:index>", methods=["DELETE"])
def delete_park(index):
    try:
        parks = read_csv(CSV_FILE, fieldnames=None)
        if 0 <= index < len(parks):
            parks.pop(index)
            write_csv(CSV_FILE, parks, fieldnames=parks[0].keys())
            return jsonify({"message": "Park deleted successfully!"})
        else:
            return jsonify({"error": "Invalid index"}), 404
    except Exception as e:
        logging.error(f"Error deleting park: {e}")
        return jsonify({"error": "Failed to delete park."}), 500


@app.route("/edit_park/<int:index>", methods=["POST"])
def edit_park(index):
    try:
        parks = read_csv(CSV_FILE, fieldnames=None)
        if 0 <= index < len(parks):
            park = parks[index]

            name = request.form.get("name", park["name"])
            latitude = float(request.form.get("latitude", park["latitude"]))
            longitude = float(request.form.get("longitude", park["longitude"]))
            ratings = {
                key: int(request.form.get(key, park[key]))
                for key in [
                    "crowd_rating",
                    "obstacle_rating",
                    "size_rating",
                    "visibility_rating",
                    "diversity_rating",
                ]
            }
            photo = request.files.get("photo")
            filename = park["photo"]

            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            # Update the park information
            park["name"] = name
            park["latitude"] = latitude
            park["longitude"] = longitude
            park["crowd_rating"] = ratings["crowd_rating"]
            park["obstacle_rating"] = ratings["obstacle_rating"]
            park["size_rating"] = ratings["size_rating"]
            park["visibility_rating"] = ratings["visibility_rating"]
            park["diversity_rating"] = ratings["diversity_rating"]
            park["photo"] = (
                f"/uploads/{filename}" if filename else park["photo"]
            )
            park["date_visited"] = request.form.get(
                "date_visited", park["date_visited"]
            )
            park["username"] = request.form.get("username", park["username"])

            write_csv(CSV_FILE, parks, fieldnames=park.keys())
            return jsonify({"message": "Park updated successfully!"})

        else:
            return jsonify({"error": "Park not found."}), 404
    except Exception as e:
        logging.error(f"Error editing park: {e}")
        return jsonify({"error": "Failed to edit park."}), 500


@app.route("/set_home_point", methods=["POST"])
def set_home_point():
    try:
        latitude = request.form["latitude"]
        longitude = request.form["longitude"]
        logging.info(
            f"Received home point: Latitude = {latitude}, Longitude = {longitude}"
        )

        with open(HOME_POINT_FILE, "w") as f:
            f.write(f"{latitude},{longitude}\n")

        return jsonify({"message": "Home point saved successfully!"})

    except Exception as e:
        logging.error(f"Error setting home point: {e}")
        return (
            jsonify({"error": "Failed to save home point. Please try again."}),
            500,
        )


# --------------------------
# Routes: Feature Requests
# --------------------------
@app.route("/submit_feature_request", methods=["POST"])
def submit_feature_request():
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
        logging.error(f"Error submitting feature request: {e}")
        return jsonify({"error": "Failed to submit feature request."}), 500


@app.route("/view_feature_requests", methods=["GET"])
def view_feature_requests():
    try:
        feature_requests = read_csv(FEATURE_REQUESTS_FILE, fieldnames=None)
        return jsonify(feature_requests)
    except Exception as e:
        logging.error(f"Error retrieving feature requests: {e}")
        return jsonify({"error": "Failed to retrieve feature requests."}), 500


# --------------------------
# Routes: Utility Pages
# --------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/parks")
def parks_page():
    return render_template("parks.html")


@app.route("/feature_request")
def feature_request_page():
    return render_template("feature_request.html")


@app.route("/view_feature_requests_page")
def view_feature_requests_page():
    return render_template("view_feature_requests.html")


@app.route("/user_stats")
def user_stats():
    parks = read_csv(CSV_FILE, fieldnames=None)
    stats = {}
    for park in parks:
        username = park.get("username", "Unknown")
        if username not in stats:
            stats[username] = {
                "num_parks": 0,
                "total_ratings": 0,
                "average_rating": 0,
            }

        stats[username]["num_parks"] += 1
        ratings = [
            int(park.get("crowd_rating", 0)),
            int(park.get("obstacle_rating", 0)),
            int(park.get("size_rating", 0)),
            int(park.get("visibility_rating", 0)),
            int(park.get("diversity_rating", 0)),
        ]

        avg_rating = calculate_average_ratings(ratings)
        stats[username]["total_ratings"] += avg_rating

    # Calculate the final average rating for each user
    for username, stat in stats.items():
        stat["average_rating"] = (
            stat["total_ratings"] / stat["num_parks"]
            if stat["num_parks"]
            else 0
        )

    return render_template("user_stats.html", user_stats=stats)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# --------------------------
# Main Application
# --------------------------
if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8086, debug=debug_mode)
