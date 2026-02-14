class BaseRepository:
    def __init__(self, database):
        self.database = database

    def execute(self, query: str, params=None):
        return self.database.execute(query, params)

    def fetch_one(self, query: str, params=None):
        return self.database.fetch_one(query, params)

    def fetch_all(self, query: str, params=None):
        return self.database.fetch_all(query, params)
