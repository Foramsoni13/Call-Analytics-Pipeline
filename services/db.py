"""
MongoDB connection helper.
Everything saved here (users, calls) will show up live in MongoDB Compass
under the database name set in .env (default: call_analytics).
"""
from pymongo import MongoClient
from config import Config

_client = None
_db = None


def get_db():
    """Returns a singleton database handle so we don't reconnect on every call."""
    global _client, _db
    if _db is None:
        _client = MongoClient(Config.MONGO_URI)
        _db = _client[Config.MONGO_DB_NAME]
    return _db


def get_users_collection():
    return get_db()["users"]


def get_calls_collection():
    return get_db()["calls"]
