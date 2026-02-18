import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY,
    title TEXT,
    price INTEGER,
    location TEXT,
    amenities TEXT
)
""")

sample_data = [
    ("Furnished room near campus", 700, "Waterloo", "wifi,laundry,furnished"),
    ("Studio downtown", 950, "Kitchener", "wifi,gym"),
    ("Shared apartment close to UW", 650, "Waterloo", "wifi,laundry"),
    ("Luxury condo", 1200, "Waterloo", "wifi,gym,furnished")
]

c.executemany(
    "INSERT INTO listings (title, price, location, amenities) VALUES (?, ?, ?, ?)",
    sample_data
)

conn.commit()
conn.close()

print("Database created!")

