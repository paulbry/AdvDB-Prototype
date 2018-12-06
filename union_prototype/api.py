# system
import hashlib
import os
import subprocess
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

# At this moment the newObjID is more or less required for a number of interactions
# This can/should be corrected after we have finalized the hash & split functionality
# as these directly play into the naming conventions
parser = reqparse.RequestParser()
parser.add_argument('removeAfter', type=bool, default=False)
parser.add_argument('newObjID', default=None)
parser.add_argument('download', type=bool, default=False)
parser.add_argument('backup', type=bool, default=False)
parser.add_argument('restore', type=bool, default=False)
parser.add_argument('split', type=int, default=0)
parser.add_argument('join', type=int, default=0)


class MetaData(Resource):
    def __init__(self, **kwargs):
        self.db_url = kwargs['db_url']
        self.db_port = kwargs['db_port']

        self.meta_db = db_interface.DatabaseCtl()

        self.backup_bucket = "db_backup_advdb18"

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
            return {'valid_parent_ids': self.meta_db.api_get_all_id()}
        # GET /parallel/obj_id/
        else:
            return self.meta_db.api_get_object(str(obj_id))

    def put(self):
        args = parser.parse_args()
        if args.backup:
            up_ci.gcloud_create_bucket(self.backup_bucket)
            up_ci.gcloud_upload_blob(self.backup_bucket, self.meta_db.db_loc,
                                     self.meta_db.db_name)
            return {'success': 'database backup'}
        elif args.restore:
            up_ci.gcloud_download_blob(self.backup_bucket, self.meta_db.db_name,
                                       self.meta_db.db_loc)
            return {'success': 'database restore'}
        else:
            return {'error': 'backup or restore must be declared'}, 400

    def delete(self, obj_id=None):
        # DELETE /meta
        if obj_id is None:
            return {'ERROR': 'No objectID supplied'}
        # DELETE /meta/obj_id/
        else:
            if self.meta_db.safe_query_value('objectID', obj_id, 'parallelLoc'):
                self.meta_db.safe_delete_entry('objectID', obj_id)
                return {'True': 'Success: Removed {0}'.format(obj_id)}
            return {'False': 'Error: Unable to identify {0}'.format(obj_id)}, 400

    def post(self):
        json_data = request.get_json(force=True)
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
            if args.download:  # signify a download should occur of
                # the object to parallelLoc
                tar_par_loc = (self.cld_db.safe_query_value('objectID',
                                                            obj_id, 'parallelLoc'))[1]
                og_cloud_vendor = (self.cld_db.safe_query_value('objectID',
                                                                obj_id, 'cloudVendor'))[1]
                og_cloud_loc = (self.cld_db.safe_query_value('objectID',
                                                             obj_id, 'cloudLoc'))[1]
                execute_cloud_get(obj_id, og_cloud_vendor, og_cloud_loc, tar_par_loc,
                                  obj_id, args.removeAfter)

                # Check hash only if present
                check_hash = self.cld_db.safe_query_value('objectID', obj_id,
                                                          'verificationHash')[1]
                if check_hash is not None:
                    tmp_hash = hashlib.md5(
                        open('{0}/{1}'.format(tar_par_loc, obj_id), 'rb').read()).hexdigest()
                    if tmp_hash != check_hash:
                        os.remove(tar_par_loc + '/' + obj_id)
                        return {'error': 'hash does not match {0}  !=  {1}'.format(
                            check_hash, tmp_hash
                        )}, 400

                # Remove file from cloud after process completed
                if args.removeAfter:
                    self.cld_db.safe_delete_entry('objectID', obj_id)
                    self.cld_db.api_insert_event(obj_id, tar_par_loc, None,
                                                 check_hash, None,
                                                 None)
                    return {'success': '{0} downloaded to {1} and removed from Cloud'.format(
                        obj_id, tar_par_loc
                    )}

            return self.cld_db.api_get_object(str(obj_id))  # information relating to object DL

    def put(self, obj_id=None, cloud_vendor=None, cloud_loc=None, nodes=None):
        args = parser.parse_args()

        # PUT /cloud
        if obj_id is None:
            return {'unsupported': 'A valid objectID must be provided'}, 400
        else:
            valid, obj_id, par_loc = self.__put_verify_obj(obj_id)
            if not valid:
                return obj_id, par_loc

            valid, vend, cloc = self.__put_verify_cloud(cloud_vendor, cloud_loc)
            if not valid:
                return vend, cloc

            new_obj_id = args.newObjID
            if args.newObjID is None:
                # TODO: determine plan for creating obj_id
                pass

            if nodes is not None:
                # When nodes is present execute (.../mpi/:nodes)
                subprocess.check_output(['mpiexec', '-n', nodes, '-usize', '17', 'python',
                                         'split.py', obj_id, cloud_loc, 500])
                return {'success': 'mpiexec completed for {0} nodes'.format(nodes)}

            og_par_loc = (self.cld_db.safe_query_value('objectID', obj_id,
                                                       'parallelLoc'))[0]
            file_hash = hashlib.md5(
                        open('{0}/{1}'.format(og_par_loc, obj_id), 'rb').read()).hexdigest()
            parent = None

            b, i = execute_cloud_put(og_obj_id=obj_id, og_par_loc=og_par_loc,
                                     tar_obj_id=new_obj_id, tar_cloud_vendor=vend,
                                     tar_cloud_loc=cloc, remove_after=args.removeAfter)
            if b:
                if args.removeAfter:
                    self.cld_db.safe_delete_entry('objectID', obj_id)
                self.cld_db.api_insert_event(new_obj_id, og_par_loc, cloc, file_hash,
                                             parent, vend)
                return i  # Success
            else:
                return i, 400  # Failure

    def __put_verify_obj(self, obj_id):
        """ Verify objectID """
        b, pl = self.cld_db.safe_query_value('objectID', obj_id, 'parallelLoc')
        if b:
            return True, obj_id, pl
        else:
            return False, {'error': 'invalid original objectID'}, 400

    @staticmethod
    def __put_verify_cloud(cloud_vendor, cloud_loc):
        """ Check cloud parameters in PUT """
        if cloud_vendor is None:
            # PUT /cloud/obj_id
            return False, {'error': 'no cloud vendor can be established'}, 400

        if cloud_vendor != 'gcloud' and cloud_vendor != 'aws':
            return False, {'error': 'unsupported cloud_vendor'}, 400

        if cloud_loc is None:
            # PUT /cloud/obj_id/cloud_vendor
            return False, {'error': 'no cloud location can be established'}, 400

        return False, cloud_vendor, cloud_loc


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
    subprocess.check_output(['mpiexec', '-n', '1', '-usize', '17', 'python', 'getParallel.py', og_obj_id])
    pass


def execute_parallel_put(og_obj_id, og_cloud_vendor, og_cloud_loc,
                         tar_obj_id, tar_par_loc, remove_after):
    """ Upload file from cloud to file system """
    # TODO: upload file to PARALLEL
    subprocess.check_output(['mpiexec', '-n', '1', '-usize', '17', 'python', 'putParallel.py', tar_obj_id, og_cloud_vendor, tar_par_loc])
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
                     '/cloud/<string:obj_id>/<string:cloud_vendor>/<string:cloud_loc>/mpi/<int:nodes>',
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