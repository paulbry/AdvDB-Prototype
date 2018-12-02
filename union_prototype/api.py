# 3rd party
from flask import request
from flask_restful import Resource
# project
from union_prototype import db_interface


class MetaData(Resource):
    def __init__(self):
        self.meta_db = db_interface.DatabaseCtl()

    ###########################################################################
    # REST API
    #
    # GET
    # DELETE
    # POST
    ###########################################################################
    def get(self):
        pass

    def delete(self, obj_id=None):
        # DELETE /meta
        if obj_id is None:
            return {'ERROR': 'No objectID supplied'}
        # DELETE /meta/obj_id/
        else:
            if self.meta_db.safe_query_value('objectID', obj_id, 'parallelLoc'):
                # TODO: implement support for removing ALL CHILDREN
                self.meta_db.safe_delete_entry('objectID', obj_id)
                return {'True': 'Success: Removed {0}'.format(obj_id)}
            return {'False': 'Error: Unable to identify {0}'.format(obj_id)}

    def post(self):
        json_data = request.get_json(force=True)
        # TODO: support nested or large posts (here or elsewhere)?
        b, m = self.__process_obj_input(json_data)
        return {b: m}

    def __process_obj_input(self, single_obj):
        """
        Process a single object (built in accordance with documented API requirements)
        Check for supported values and then INSERT into database
        NOTE: there is very little in the way to verification and no pre-processing
        being accomplished. We will (at this time) need to rely on correct usage of the API
        :param single_obj: single object (dict/json)
        :return: Tuple: Boolean (successful?) and message (regarding possible failure)
        """
        object_id = single_obj.get('objectID')
        if object_id is None:
            return False, 'No objectID found'
        parallel_loc = single_obj.get('parallelLoc')
        if parallel_loc is None:
            return False, 'No parallelLoc found'
        cloud_loc = single_obj.get('cloudLoc')
        cloud_vendor = single_obj.get('cloudVendor')
        verification_hash = single_obj.get('verificationHash')
        parent_id = single_obj.get('parentID')

        if self.meta_db.api_insert_event(object_id, parallel_loc, cloud_loc,
                                         verification_hash, parent_id,
                                         cloud_vendor):
            return True, 'Successfully POST object {0}'.format(object_id)

        return False, 'Unexpected error during INSERT'


class Parallel(Resource):
    def __init__(self):
        self.par_db = db_interface.DatabaseCtl()

    ###########################################################################
    # REST API
    #
    # GET
    # PUT
    ###########################################################################
    def get(self, obj_id=None):
        # GET /parallel
        if obj_id is None:
            return {'valid_parent_ids': self.par_db.api_get_all_id()}
        # GET /parallel/obj_id/
        else:
            return self.par_db.api_get_object(str(obj_id))

    def put(self):
        pass


class Cloud(Resource):
    def __init__(self):
        self.cld_db = db_interface.DatabaseCtl()

    ###########################################################################
    # REST API
    #
    # GET
    # PUT
    ###########################################################################
    def get(self, obj_id=None):
        # GET /cloud
        if obj_id is None:
            return {'valid_parent_ids': self.cld_db.api_get_all_id(True)}
        # GET /cloud/obj_id/
        else:
            return self.par_db.api_get_object(str(obj_id))

    def put(self):
        pass
