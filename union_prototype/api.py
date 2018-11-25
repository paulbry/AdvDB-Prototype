# 3rd party
from flask_restful import Resource
# project
from union_prototype import db_interface


class Parallel(Resource):
    def __init__(self):
        pass

    def get(self, obj_id=None, system=None):
        # GET /parallel
        if obj_id is None:
            return {'hello': 'world'}

        # GET /parallel/obj_id/
        if system is None:
            return {'hello': obj_id}
        # GET /parallel/obj_id/system
        else:
            return {'test': system}

    def put(self):
        pass

    def delete(self):
        pass

    def post(self):
        pass


class Cloud(Resource):
    def __init__(self):
        pass

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def post(self):
        pass
