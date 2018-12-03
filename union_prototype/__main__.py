# system
import argparse
import os
import sys
# 3rd party
from flask import Flask
from flask_restful import Api
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

parser.add_argument("-u", "--db-url",
                    dest='db_url', nargs=1,
                    default='localhost',
                    help="URL for database service (default = localhost)")

parser.add_argument("-p", "--db-port",
                    dest='db_port', nargs=1,
                    default=27017,
                    help="Port for database service (default = 27017)")


# noinspection PyTypeChecker
def manage_args(args):
    app = Flask(__name__)
    api = Api(app)

    tmp_db = db_interface.DatabaseCtl()
    if not os.path.isfile(tmp_db.db_loc):
        tmp_db.create_object_db()

        # Parallel (e.g. Lustre) resources
    api.add_resource(api_pack.Parallel, '/parallel',
                     '/parallel/<string:obj_id>',
                     '/parallel/<string:obj_id>/<string:file_sys>')

    # Cloud (e.g. Google Cloud Storage, Amazon S3) resources
    api.add_resource(api_pack.Cloud, '/cloud',
                     '/cloud/<string:obj_id>',
                     '/cloud/<string:obj_id>/<string:cloud_vendor>',
                     '/cloud/<string:obj_id>/<string:cloud_vendor>/<string:cloud_loc>')

    # MetaData (PUT/DELETE entries in DB only!) resource
    api.add_resource(api_pack.MetaData, '/meta',
                     '/meta/<string:obj_id>')

    app.run(debug=args.debug)


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
