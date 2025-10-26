import csv

def load_county_data():
    with open("data/county_demographics.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
    return data