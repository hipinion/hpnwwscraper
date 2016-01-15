"""
utilities for connecting to a sql database
"""
from psycopg2.extras import DictCursor
import psycopg2
import os

def get_connection():
    """
    get the global connection object. Stored to prevent nested transactions
    """
    return Connection.global_connection

def transactional(func):
    """
    annotation for making sure a connection is open for a function.
    commits if this is the last reference to the connection and the function
    exited with no errors. Rolls back if the function raised an exception.
    """
    def inner(*args, **kwargs):
        """
        wrap the function in a with Connection
        """
        with Connection():
            return func(*args, **kwargs)
    return inner

class Connection(object):
    """
    Provides with interface to a database connection.
    Unique-ifies connections so we don't get nested connections.
    Handles committing/rolling back if this is the owner of the
    global connection
    """
    global_connection = None

    def __init__(self):
        """
        initializes connection using peer based authentication as is
        default for postgres. This assumes you'd like to load everything into
        the database that is under whatever username you provide in the
        DBUSER environment variable. If you'd rather use password authentication
        switch to the commented out db_conf block
        """
        self.conn = None
        """
        self.db_conf = "dbname={dbname}, user={user}, password={pw}".format(
            dbname=os.getenv('DBNAME'),
            user=os.getenv('DBUSER'),
            pw=os.getenv('DBPW'))
            """
        self.db_conf = "user={user}".format(
            user=os.getenv('DBUSER'))

    def __enter__(self):
        if not Connection.global_connection:
            Connection.global_connection = psycopg2.connect(
                self.db_conf,
                cursor_factory=DictCursor)
            self.conn = Connection.global_connection
        return Connection.global_connection

    def __exit__(self, ex_type, value, traceback):
        if ex_type:
            if self.conn:
                self.conn.rollback()
                Connection.global_connection = None
            return False
        else:
            if self.conn:
                self.conn.commit()
                Connection.global_connection = None
            return True
