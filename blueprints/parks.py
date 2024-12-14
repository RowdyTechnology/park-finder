from flask import Blueprint, request, jsonify
import os
import csv
from datetime import datetime
from werkzeug.utils import secure_filename
from .utils import read_csv, write_csv, calculate_average_ratings

parks_bp = Blueprint("parks", __name__)

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/mnt/user/appdata/parks/uploads") # Updated default
CSV_FILE = os.getenv("CSV_FILE", "/mnt/user/appdata/parks/data.csv") # Updated default
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
HOME_POINT_FILE = os.getenv("HOME_POINT_FILE", "/mnt/user/appdata/parks/home_point.csv") # Updated default

# Ensure necessary folders and files exist
# No need to create UPLOAD_FOLDER here as it is handled in app.py
os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
os.makedirs(os.path.dirname(HOME_POINT_FILE), exist_ok=True)
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "name", "latitude", "longitude", "crowd_rating", "obstacle_rating", 
            "size_rating", "visibility_rating", "diversity_rating", "photo", "date_visited", "username"
        ])
        writer.writeheader()
if not os.path.exists(HOME_POINT_FILE):
    with open(HOME_POINT_FILE, mode="w", newline="") as file:
        file.write("latitude,longitude\n")

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@parks_bp.route("/add", methods=["POST"])
def add_park():
    """Add a new park."""
    try:
        file = request.files.get("photo")
        filename = ""
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Use os.path.join for saving the file
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        ratings = {
            key: int(request.form[key]) for key in [
                "crowd_rating", "obstacle_rating", "size_rating", "visibility_rating", "diversity_rating"
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
            "date_visited": request.form.get("date_visited", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
            "username": request.form.get("username", "Unknown"),
        }

        parks = read_csv(CSV_FILE)
        parks.append(data)
        write_csv(CSV_FILE, parks, fieldnames=[
            "name", "latitude", "longitude", "crowd_rating", "obstacle_rating", 
            "size_rating", "visibility_rating", "diversity_rating", "photo", "date_visited", "username"
        ])
        return jsonify({"message": "Park added successfully!"})
    except ValueError as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to add park: {e}"}), 500

@parks_bp.route("/", methods=["GET"])
def view_parks():
    """View all parks."""
    try:
        parks = read_csv(CSV_FILE)
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
        return jsonify({"error": f"Failed to retrieve parks: {e}"}), 500

@parks_bp.route("/<int:index>", methods=["GET"])
def get_park(index):
    """Get a single park by its index."""
    try:
        parks = read_csv(CSV_FILE)
        if 0 <= index < len(parks):
            return jsonify(parks[index])
        else:
            return jsonify({"error": "Invalid park index"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve park: {e}"}), 500

@parks_bp.route("/edit/<int:index>", methods=["PUT"])
def edit_park(index):
    """Edit an existing park."""
    try:
        parks = read_csv(CSV_FILE)
        if 0 <= index < len(parks):
            edited_park = request.get_json()
            parks[index].update(edited_park)
            write_csv(CSV_FILE, parks, fieldnames=parks[0].keys())
            return jsonify({"message": "Park updated successfully!"})
        else:
            return jsonify({"error": "Invalid park index"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to update park: {e}"}), 500

@parks_bp.route("/delete/<int:index>", methods=["DELETE"])
def delete_park(index):
    """Delete a park by its index."""
    try:
        parks = read_csv(CSV_FILE)
        if 0 <= index < len(parks):
            parks.pop(index)
            write_csv(CSV_FILE, parks, fieldnames=parks[0].keys())
            return jsonify({"message": "Park deleted successfully!"})
        else:
            return jsonify({"error": "Invalid park index"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to delete park: {e}"}), 500

@parks_bp.route("/home_point", methods=["POST"])
def set_home_point():
    """Set the home point."""
    try:
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        with open(HOME_POINT_FILE, mode="w", newline="") as file:
            file.write(f"{latitude},{longitude}\n")
        return jsonify({"message": "Home point set successfully!"})
    except Exception as e:
        return jsonify({"error": f"Failed to set home point: {e}"}), 500