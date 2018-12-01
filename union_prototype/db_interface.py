# system
import os
import sqlite3
# 3rd party
import mysql
from termcolor import cprint

###############################################################################
# At this time we are utilizing sqlite for the database functionality, this
# covers the core goals of the prototype but move us away from use a more
# industry acceptable tool. Long term this will need to change; however,
# for a temporary measure this is acceptable.
# When better solution identified we will restructure the module
###############################################################################


class DatabaseCtl(object):
    def __init__(self):
        # hardcoded paths (need to alter)
        self.db_loc = os.path.dirname(os.path.realpath(__file__)) + "\.protodb"

    def create_object_db(self):
        """
        Create both the database (.protodb) and reacted table (objectdata)
        in order to support prototype requirements
        :return: True is successful, False is not
        """
        try:
            db = sqlite3.connect(self.db_loc)
            cursor = db.cursor()
        except sqlite3.Error as e:
            cprint("Unexpected error during database creation/connection\n{}".format(
                e), 'red')
            return False

        cmd = "CREATE TABLE IF NOT EXISTS objectdata "\
              "(id INTEGER PRIMARY KEY, " \
              "objectID TEXT NOT NULL, " \
              "parallelLoc TEXT NOT NULL, " \
              "cloudLoc TEXT, " \
              "verificationHash TEXT, " \
              "parentID TEXT, " \
              "time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)"

        if self.__execute_query(cursor, cmd):
            db.commit()
            db.close()
            return True
        else:
            db.close()
            return False

    def api_get_object(self, object_id):
        pass

    def api_get_all_id(self, cloud=False):
        cmd = "SELECT objectID FROM objectdata WHERE parentID IS NULL"
        if cloud:
            cmd += " AND cloudLoc IS NOT NULL"

        db = sqlite3.connect(self.db_loc)
        cursor = db.cursor()
        id_list = []

        if self.__execute_query(cursor, cmd):
            for line in cursor.fetchall():
                id_list.append(line[0])

        db.close()
        return id_list

    # PRIVATE/SUPPORTING
    @staticmethod
    def __execute_query(cursor, cmd):
        """
        Execute supplied command (query) using the cursor
        :param cursor: sqlite3 cursor object
        :param cmd: String (no verification)
        :return: True is successful, False is not
        """
        try:
            cursor.execute(cmd)
            return True
        except sqlite3.Error as e:
            cprint("Unexpected error during {}\n{}".format(cmd, e), 'red')
            return False
        except sqlite3.OperationalError as e:
            cprint("Operational error during {}\n{}".format(cmd, e), 'red')
            return False

    def insert_test_data(self):
        db = sqlite3.connect(self.db_loc)
        cursor = db.cursor()

        self.__execute_query(cursor, "INSERT INTO objectdata (objectID, parallelLoc) VALUES ('1A', 'test')")
        self.__execute_query(cursor, "INSERT INTO objectdata (objectID, parallelLoc) VALUES ('1B', 'test')")
        self.__execute_query(cursor, "INSERT INTO objectdata (objectID, parallelLoc) VALUES ('1C', 'test')")

        db.commit()
        db.close()


dat = DatabaseCtl()
dat.create_object_db()
dat.insert_test_data()
dat.api_get_all_id()
