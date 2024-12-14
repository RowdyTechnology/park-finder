from flask import Blueprint, render_template
import csv
from .utils import read_csv, calculate_average_ratings

user_stats_bp = Blueprint("user_stats", __name__)

CSV_FILE = "./data/parks.csv"

@user_stats_bp.route("/")
def user_stats():
    """Display user statistics."""
    parks = read_csv(CSV_FILE, fieldnames=None)
    stats = {}

    for park in parks:
        username = park.get("username", "Unknown")
        if username not in stats:
            stats[username] = {"num_parks": 0, "average_rating": 0}
        stats[username]["num_parks"] += 1

        ratings = [
            int(park.get("crowd_rating", 0)),
            int(park.get("obstacle_rating", 0)),
            int(park.get("size_rating", 0)),
            int(park.get("visibility_rating", 0)),
            int(park.get("diversity_rating", 0)),
        ]
        stats[username]["average_rating"] += calculate_average_ratings(ratings)

    # Calculate average rating per user
    for user, data in stats.items():
        num_parks = data["num_parks"]
        data["average_rating"] /= num_parks if num_parks else 1  # Avoid division by zero

    return render_template("user_stats.html", user_stats=stats)