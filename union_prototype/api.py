# system
import os
# 3rd party
from flask import request, Flask
from flask_restful import Resource, Api, reqparse
# project
from union_prototype import cloud_interface as up_ci
from union_prototype import db_interface

###########################################################################
# Flask-Restful API
# https://flask-restful.readthedocs.io
###########################################################################
app = Flask(__name__)
# noinspection PyTypeChecker
api = Api(app)

# TODO: clearly document in a forward facing way
# At this moment the newObjID is more or less required for a number of interactions
# This can/should be corrected after we have finalized the hash & split functionality
# as these directly play into the naming conventions
parser = reqparse.RequestParser()
parser.add_argument('removeAfter', type=bool, default=False)
parser.add_argument('newObjID', default=None)
parser.add_argument('download', type=bool, default=False)


class MetaData(Resource):
    def __init__(self, **kwargs):
        self.db_url = kwargs['db_url']
        self.db_port = kwargs['db_port']

        self.meta_db = db_interface.DatabaseCtl()

    ###########################################################################
    # REST API
    #
    # GET - Return metadata (JSON) based upon objectID provided
    # DELETE - Delete metadata based upon objectID provided
    # POST - Post metadata
    ###########################################################################
    def get(self, obj_id=None):
        # GET /parallel
        if obj_id is None:
            # TODO: general TODO across api.py is add error code to return tuple
            return {'valid_parent_ids': self.par_db.api_get_all_id()}
        # GET /parallel/obj_id/
        else:
            return self.par_db.api_get_object(str(obj_id))

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
    def __init__(self, **kwargs):
        self.db_url = kwargs['db_url']
        self.db_port = kwargs['db_port']

        self.par_db = db_interface.DatabaseCtl()

    ###########################################################################
    # REST API
    #
    # GET - Copy file from mounted files system to mounted system and
    #       query the DB for information related to objects
    # PUT - Upload file from cloud to file system
    ###########################################################################
    def get(self, obj_id=None):
        # GET /parallel
        if obj_id is None:
            return {'valid_parent_ids': self.par_db.api_get_all_id()}
        # GET /parallel/obj_id/
        else:
            # TODO: complete copy step (integrate support for split)
            return self.par_db.api_get_object(str(obj_id))

    def put(self):
        args = parser.parse_args()
        # TODO: complete (Upload file from cloud to file system)
        pass


class Cloud(Resource):
    def __init__(self, **kwargs):
        self.db_url = kwargs['db_url']
        self.db_port = kwargs['db_port']

        self.cld_db = db_interface.DatabaseCtl()

    ###########################################################################
    # REST API
    #
    # GET - Download file from cloud system to local file system as well as
    #       query the DB for information related to objects
    # PUT - Upload file from mounted files system to cloud
    ###########################################################################
    def get(self, obj_id=None):
        args = parser.parse_args()

        # GET /cloud
        if obj_id is None:
            return {'valid_parent_ids': self.cld_db.api_get_all_id(True)}
        # GET /cloud/obj_id/
        else:
            if args.Download:
                tar_par_loc = (self.cld_db.safe_query_value('objectID', obj_id, 'parallelLoc'))[0]
                og_cloud_vendor = (self.cld_db.safe_query_value('objectID', obj_id, 'cloudVendor'))[0]
                og_cloud_loc = (self.cld_db.safe_query_value('objectID', obj_id, 'cloudLoc'))[0]
                execute_cloud_get(obj_id, og_cloud_vendor, og_cloud_loc, tar_par_loc, obj_id,
                                  args.removeAfter)
            return self.par_db.api_get_object(str(obj_id))

    def put(self, obj_id=None, cloud_vendor=None, cloud_loc=None):
        args = parser.parse_args()

        # PUT /cloud
        if obj_id is None:
            return {'unsupported': 'A valid objectID must be provided'}
        else:
            vend = cloud_vendor
            if cloud_vendor is None:
                # PUT /cloud/obj_id
                return {'error': 'no cloud vendor can be established'}

            cloc = cloud_loc
            if cloud_loc is None:
                # PUT /cloud/obj_id/cloud_vendor
                return {'error': 'no cloud location can be established'}

            new_obj_id = args.newObjID
            if args.newObjID is None:
                # TODO: determine plan for creating obj_id
                pass

            # TODO: integrate support for split

            og_par_loc = (self.cld_db.safe_query_value('objectID', obj_id, 'parallelLoc'))[0]
            file_hash = "TEST"   # TODO: implement has support
            parent = None  # TODO: implement concept of parent? (maybe if split)

            b, id = execute_cloud_put(og_obj_id=obj_id, og_par_loc=og_par_loc,
                                      tar_obj_id=new_obj_id, tar_cloud_vendor=vend,
                                      tar_cloud_loc=cloc, remove_after=args.removeAfter)
            if b:
                if args.removeAfter:
                    self.cld_db.safe_delete_entry('objectID', obj_id)
                self.cld_db.api_insert_event(new_obj_id, og_par_loc, cloc, file_hash,
                                             parent, vend)
                return id  # Success
            else:
                return id  # Failure


def execute_cloud_get(og_obj_id, og_cloud_vendor, og_cloud_loc,
                      tar_par_loc, tar_obj_id, remove_after):
    """ Download file from cloud system to local file system """
    if og_cloud_vendor == 'gcloud':
        up_ci.gcloud_download_blob(og_cloud_loc, og_obj_id, tar_par_loc + "/" + tar_obj_id)
        if remove_after:
            up_ci.gcloud_delete_blob(og_cloud_loc, og_obj_id)
    elif og_cloud_vendor == 'aws':
        # TODO: add aws support and potentially reformat via adapter pattern?
        return False, {'error': 'AWS is currently unsupported'}
    else:
        return False, {'error': 'Unsupported cloud vendor {0} provided'.format(
            og_cloud_vendor
        )}

    return False, {'error': 'Unable to run execute_cloud_get'}


def execute_cloud_put(og_obj_id, og_par_loc,
                      tar_obj_id, tar_cloud_vendor, tar_cloud_loc,
                      remove_after):
    """ Upload file from mounted files system to cloud """

    if tar_cloud_vendor == 'gcloud':
        up_ci.gcloud_create_bucket(tar_cloud_loc)
        up_ci.gcloud_upload_blob(tar_cloud_loc, og_par_loc + "/" + og_obj_id,
                                 tar_obj_id)
        if remove_after:
            os.remove(og_par_loc + "/" + og_obj_id)
    elif tar_cloud_vendor == 'aws':
        # TODO: add aws support and potentially reformat via adapter pattern?
        return False, {'error': 'AWS is currently unsupported'}
    else:
        return False, {'error': 'Unsupported cloud vendor {0} provided'.format(
            tar_cloud_vendor
        )}

    return False, {'error': 'Unable to run execute_cloud_put'}


def execute_parallel_get(og_obj_id, tar_par_loc, remove_after):
    """ Copy file from mounted files system to mounted system """
    # TODO: download file from PARALLEL
    pass


def execute_parallel_put(og_obj_id, og_cloud_vendor, og_cloud_loc,
                         tar_obj_id, tar_par_loc, remove_after):
    """ Upload file from cloud to file system """
    # TODO: upload file to PARALLEL
    pass


# noinspection PyTypeChecker
def main(debug, db_url, db_port):
    # Parallel (e.g. Lustre) resources
    api.add_resource(Parallel, '/parallel',
                     '/parallel/<string:obj_id>',
                     '/parallel/<string:obj_id>/<string:file_sys>',
                     resource_class_kwargs={
                         'db_url': db_url,
                         'db_port': db_port
                     })

    # Cloud (e.g. Google Cloud Storage, Amazon S3) resources
    api.add_resource(Cloud, '/cloud',
                     '/cloud/<string:obj_id>',
                     '/cloud/<string:obj_id>/<string:cloud_vendor>',
                     '/cloud/<string:obj_id>/<string:cloud_vendor>/<string:cloud_loc>',
                     resource_class_kwargs={
                         'db_url': db_url,
                         'db_port': db_port
                     })

    # MetaData (PUT/DELETE entries in DB only!) resource
    api.add_resource(MetaData, '/meta',
                     '/meta/<string:obj_id>',
                     resource_class_kwargs={
                         'db_url': db_url,
                         'db_port': db_port
                     })

    app.run(debug=debug)
# TODO: create demo and update README
