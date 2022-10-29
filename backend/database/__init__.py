# import sqlite3 as sql
# from backend.config import Settings

# def dbConnection():
#     conn = sql.connect(Settings.DATABASE_NAME)
#     conn.row_factory = sql.Row
#     # conn.set_trace_callback(print)
#     return conn

# class DBMain:
#     def __init__(self, id=None, created_at=None, updated_at=None):
#         self.id = id
#         self.created_at = created_at
#         self.updated_at = updated_at