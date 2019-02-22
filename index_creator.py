from pymongo import MongoClient
import config


def main():
    # Connect to database
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]

    result = db['courses'].create_index(
        [
            ('desc', 'text'),
            ('name', 'text')
        ],
        default_language='english',
        weights={
            'desc': 1,
            'name': 5,
        }
    )
    print(result)
    result = db['meetings'].create_index([
        ('instructors', 'text')
    ])
    print(result)
