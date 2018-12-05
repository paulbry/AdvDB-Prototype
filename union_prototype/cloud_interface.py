# 3rd party
from google.cloud import storage, exceptions


###############################################################################
# Cloud interface methods
#
# Google Cloud Storage
#   * https://cloud.google.com/storage/docs/how-to
#   We assume that the user has properly provided the required application
#   credentials (found defined on the EVN - GOOGLE_APPLICATION_CREDENTIALS)
#   The below links outline what is required to use the python library
#   along with the SDK (recommended to make setup easier)
#   * https://cloud.google.com/sdk/
#   * https://cloud.google.com/storage/docs/reference/libraries#client
#       -libraries-usage-python
###############################################################################


def gcloud_create_bucket(bucket_name):
    """Creates a new bucket (if not already present) """
    storage_client = storage.Client()
    try:
        bucket = storage_client.create_bucket(bucket_name)
        print('Bucket {} created'.format(bucket.name))
    except exceptions.Conflict:
        print('Bucket {} already exists'.format(bucket_name))


def gcloud_upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


def gcloud_download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))


def gcloud_delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

    print('Blob {} deleted.'.format(blob_name))
