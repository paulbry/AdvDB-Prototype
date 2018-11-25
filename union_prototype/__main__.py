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
###############################################################################
parser.add_argument("-d", "--debug",
                    dest='debug', action='store_true',
                    default=False,
                    help="Enable Flask's debug mode (default = False)")


# noinspection PyTypeChecker
def manage_args(args):
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(api_pack.Parallel, '/parallel',
                     '/parallel/<string:obj_id>',
                     '/parallel/<string:obj_id>/<string:test>')

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
