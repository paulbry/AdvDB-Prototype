# system
import argparse
import os
import sys
# 3rd party
from termcolor import cprint
# project
from union_prototype import api as api_pack
from union_prototype import db_interface


parser = argparse.ArgumentParser(description="Advance Database - System "
                                             "Prototype\nhttps://github."
                                             "com/paulbry/AdvDB-Prototype")

###############################################################################
# Un-organized arguments
#
# debug:    Enable flask debug mode
#           http://flask.pocoo.org/docs/1.0/quickstart/#debug-mode
# db-url:   Url for database (default = localhost)
# db-port:  Port for database (default = 27017)
###############################################################################
parser.add_argument("-d", "--debug",
                    dest='debug', action='store_true',
                    default=False,
                    help="Enable Flask's debug mode (default = False)")
# TODO: at this moment the database related args are not used, address if required
parser.add_argument("-u", "--db-url",
                    dest='db_url', nargs=1,
                    default='localhost',
                    help="URL for database service (default = localhost)")

parser.add_argument("-p", "--db-port",
                    dest='db_port', nargs=1,
                    default=27017,
                    help="Port for database service (default = 27017)")


def manage_args(args):
    tmp_db = db_interface.DatabaseCtl()
    if not os.path.isfile(tmp_db.db_loc):
        tmp_db.create_object_db()

    launch_verification()

    api_pack.main(debug=args.debug, db_url=args.db_url, db_port=args.db_port)


def launch_verification():
    """Verify some required launch parameters that could lead to failures"""
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        cprint('Unable to identify GOOGLE_APPLICATION_CREDENTIALS variable', 'red')
        sys.exit(os.EX_UNAVAILABLE)
    return True


def main():
    try:
        args = parser.parse_args()
        manage_args(args)
    except argparse.ArgumentError as e:
        cprint(e, 'red')
        exit(1)


if __name__ == '__main__':
    main()
