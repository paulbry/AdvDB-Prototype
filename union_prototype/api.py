# 3rd party
from flask_restful import Resource
# project
from union_prototype import db_interface


class Parallel(Resource):
    def __init__(self):
        self.par_db = db_interface.DatabaseCtl()

    def get(self, obj_id=None):
        # GET /parallel
        if obj_id is None:
            return {'valid_parent_ids': self.cld_db.api_get_all_id()}
        # GET /parallel/obj_id/
        else:
            return self.par_db.api_get_object(obj_id)

    def put(self):
        pass

    def delete(self):
        pass

    def post(self):
        pass


class Cloud(Resource):
    def __init__(self):
        self.cld_db = db_interface.DatabaseCtl()

    def get(self, obj_id=None):
        # GET /parallel
        if obj_id is None:
            return {'valid_parent_ids': self.cld_db.api_get_all_id(True)}
        # GET /parallel/obj_id/
        else:
            return self.par_db.api_get_object(obj_id)

    def put(self):
        pass

    def delete(self):
        pass

    def post(self):
        pass
