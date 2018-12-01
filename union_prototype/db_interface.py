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
###############################################################################

# hardcoded paths (need to alter)
db_loc = os.path.dirname(os.path.realpath(__file__)) + "\.protodb"


def create_object_db():
    """
    Create both the database (.protodb) and reacted table (objectdata)
    in order to support prototype requirements
    :return: True is successful, False is not
    """
    try:
        db = sqlite3.connect(db_loc)
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

    if execute_query(cursor, cmd):
        db.commit()
        db.close()
        return True
    else:
        db.close()
        return False


def execute_query(cursor, cmd):
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
