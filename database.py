from tinydb import TinyDB

db = TinyDB("data/aircraft_db.json")

def update_database(data):
    db.truncate()
    for ac in data.get("aircraft", []):
        db.insert(ac)

def get_all_aircraft():
    return db.all()
