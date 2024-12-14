import csv
import os
from datetime import datetime

def read_csv(file_path, fieldnames=None):
    """Reads a CSV file and returns the data."""
    data = []
    if os.path.exists(file_path):
        with open(file_path, mode="r") as file:
            reader = csv.DictReader(file, fieldnames=fieldnames)
            for row in reader:
                data.append(row)
    return data

def write_csv(file_path, data, fieldnames):
    """Writes data to a CSV file."""
    with open(file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def append_csv(file_path, data, fieldnames):
    """Appends a row of data to a CSV file."""
    with open(file_path, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(data)

def calculate_average_ratings(ratings):
    """Calculate the average rating from multiple categories."""
    valid_ratings = [r for r in ratings if isinstance(r, (int, float))]
    return round(sum(valid_ratings) / len(valid_ratings), 2) if valid_ratings else 0