# system
import os
import sqlite3
# 3rd party
from termcolor import cprint

###############################################################################
# At this time we are utilizing sqlite for the database functionality, this
# covers the core goals of the prototype but move us away from use a more
# industry acceptable tool. Long term this will need to change; however,
# for a temporary measure this is acceptable.
# When better solution identified we will restructure the module
# Current checklist (12/1/2018)
# TODO: decide database type
# TODO: change error handling after finalizing DB type
###############################################################################


class DatabaseCtl(object):
    def __init__(self):
        # hardcoded paths (need to alter)
        self.db_name = '.protodb'
        self.db_loc = "{0}/{1}".format(
            os.path.dirname(os.path.realpath(__file__)), self.db_name
        )
        self.table = "objectdata"

    def create_object_db(self):
        """
        Create both the database (.protodb) and reacted table (objectdata)
        in order to support prototype requirements
        :return: True is successful, False is not
        """
        mydb = self.__connect_db()
        cursor = mydb.cursor()

        cmd = "CREATE TABLE IF NOT EXISTS objectdata "\
              "(id INTEGER PRIMARY KEY, " \
              "objectID TEXT NOT NULL, " \
              "parallelLoc TEXT NOT NULL, " \
              "cloudLoc TEXT, " \
              "verificationHash TEXT, " \
              "parentID TEXT, " \
              "time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, " \
              "cloudVendor TEXT)"

        if self.__execute_query(cursor, cmd):
            self.__close_db(mydb, True)
            return True
        else:
            self.__close_db(mydb, False)
            return False

    def api_get_object(self, object_id):
        """
        :param object_id: Valid object ID
        :return: Dictionary with all details from parent and all possible
        child/sub object
        """
        cmd_p = "SELECT * FROM objectdata WHERE objectID = " \
                "'{}'".format(object_id)
        cmd_c = "SELECT * FROM objectdata WHERE parentID = " \
                "'{}'".format(object_id)
        obj_dict = {}

        mydb = self.__connect_db()
        cursor = mydb.cursor()

        if self.__execute_query(cursor, cmd_p):
            obj_dict.update({'main': self.__dict_format(cursor.fetchone())})

        if self.__execute_query(cursor, cmd_c):
            num = 0
            for line in cursor.fetchall():
                obj_dict.update(
                    {'sub{}'.format(num): self.__dict_format(line)})
                num += 1

        self.__close_db(mydb, False)
        return obj_dict

    def api_insert_event(self, object_id, parallel_loc, cloud_loc,
                         verification_hash, parent_id, cloud_vendor):
        mydb = self.__connect_db()
        cursor = mydb.cursor()

        try:
            cursor.execute("INSERT INTO  objectdata (objectID, parallelLoc, cloudLoc, "
                           "verificationHash, parentID, cloudVendor) VALUES(?, ?, ?, ?, ?, ?)",
                           (object_id, parallel_loc, cloud_loc, verification_hash, parent_id,
                            cloud_vendor))
            self.__close_db(mydb, True)
            return True
        except sqlite3.Error as e:
            cprint("Error during: insert_launch_event\n" + repr(e), 'red')
            return False
        except sqlite3.OperationalError as e:
            cprint("Error during: insert_launch_event\n" + repr(e), 'red')
            return False

    def api_get_all_id(self, cloud=False):
        """
        Get list of all possible top level (parent) objects
        :param cloud: Boolean, if searching for objects stored in Cloud system
        :return: List of objectID
        """
        id_list = []
        cmd = "SELECT objectID FROM {0} WHERE parentID IS NULL".format(
            self.table)
        if cloud:
            cmd += " AND cloudLoc IS NOT NULL"

        mydb = self.__connect_db()
        cursor = mydb.cursor()

        if self.__execute_query(cursor, cmd):
            for line in cursor.fetchall():
                id_list.append(line[0])

        self.__close_db(mydb, False)

        return id_list

    def safe_query_value(self, index, value, result):
        """
        SELECT <result> FROM DB WHERE <index>=<value>
        :param index:
        :param value:
        :param result:
        :return: Tuple Success boolean,
        """
        cmd = "SELECT {0} FROM {1} WHERE {2}='{3}'".format(
            result,  self.table, index, str(value)
        )

        mydb = self.__connect_db()
        cursor = mydb.cursor()

        try:
            if self.__execute_query(cursor, cmd):
                val = True, cursor.fetchone()[0]
            else:
                val = False, None
        except TypeError:
            return False, None

        self.__close_db(mydb, False)

        return val

    def safe_delete_entry(self, index, value):
        """
        DELETE FROM DB WHERE <index>=<value>
        :param index:
        :param value:
        :return: Boolean, True is success
        """
        cmd = "DELETE FROM {0} WHERE {1}='{2}'".format(
            self.table, index, value)

        mydb = self.__connect_db()
        cursor = mydb.cursor()

        if self.__execute_query(cursor, cmd):
            self.__close_db(mydb, True)
            return True

        self.__close_db(mydb, False)
        return False

    # PRIVATE/SUPPORTING
    def __connect_db(self):
        """
        Open connection to database, exit(1) if error encountered
        :return: connection to database (sqlite3.connect() object)
        """
        try:
            return sqlite3.connect(self.db_loc)
        except sqlite3.Error as e:
            cprint("Unexpected error during database connection\n{}".format(
                e), 'red')
            exit(1)

    @staticmethod
    def __close_db(mydb, commit):
        """
        Close connection to database, exit(1) if error encountered
        :param mydb: connection to database (sqlite3.connect() object)
        :param commit: Boolean, commit all changes (True)
        """
        try:
            if commit:
                mydb.commit()
            mydb.close()
        except sqlite3.Error as e:
            cprint("Unexpected error during database close\n{}".format(
                e), 'red')
            exit(1)

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

    @staticmethod
    def __dict_format(line):
        tmp = {'objectID': line[1], 'parallelLoc': line[2], 'cloudLoc': line[3], 'verificationHash': line[4],
               'parentID': line[5], 'time': line[6], 'cloudVendor': line[7]}
        return tmp
