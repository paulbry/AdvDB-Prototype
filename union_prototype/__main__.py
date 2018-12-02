# system
import argparse
# 3rd party
from flask import Flask
from flask_restful import Api
from termcolor import cprint
# project
from union_prototype import api as api_pack


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

    # Parallel (e.g. Lustre) resources
    api.add_resource(api_pack.Parallel, '/parallel',
                     '/parallel/<string:obj_id>',
                     '/parallel/<string:obj_id>/<string:file_sys>')

    # Cloud (e.g. Google Cloud Storage, Amazon S3) resources
    api.add_resource(api_pack.Cloud, '/cloud',
                     '/cloud/<string:obj_id>',
                     '/cloud/<string:obj_id>/<string:file_sys>')

    # MetaData (PUT/DELETE entries in DB only!) resource
    api.add_resource(api_pack.MetaData, '/meta',
                     '/meta/<string:obj_id>')

    app.run(debug=args.debug)


def main():
    try:
        args = parser.parse_args()
        manage_args(args)
    except argparse.ArgumentError as e:
        cprint(e, 'red')
        exit(1)


if __name__ == '__main__':
    main()
