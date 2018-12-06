# AdvDB-Prototype
Parallel to Luster (and back again) file system support prototype.


### Installation
Before proceeding with the install verify the the 

* Linux OS (tested on Linux, other systems may not function)
    * Mounted Lustre filesystem
* Google Cloud
    * Account with access to Google Cloud Storage (Storage Admin)
    * Cloud SDK - https://cloud.google.com/sdk
    * Service account and local credentials (json)
        * https://cloud.google.com/storage/docs/reference/libraries#client-libraries-usage-python
        * Use "Command Line"

1. `$ git clone https://github.com/paulbry/AdvDB-Prototype`
2. `$ cd AdvDB-Prototype/union_prototype`
3. `$ pip install .`

### Prototype Demonstration
TODO: outline currently support functionality with demonstration

`$ ???`

#### Meta-Data
* POST

    * Resource: `\meta`
    
    * Argument: `{json: ?}`
    
    * Notes: There is very little in the way of error checking, insure that keys match up with database.

    1. ```bash
        $ curl 127.0.0.1:5000/meta -X POST -d '{"objectID":"example","parallelLoc":"/var/tmp","cloudLoc":"test","verificationHast":"a12b","cloudVendor":"gcloud"}'
        ```
    2. This will attempt to post the following information to the supporting database:
        ```json
        {
           "objectID":"example",
           "parallelLoc":"/var/tmp",
           "cloudLoc":"test",
           "verificationHast":"a12b",
           "cloudVendor":"gcloud",
        }
        ```
    3. `{"true": "Successfully POST object example"}`
* GET

    * Resource: `\meta\<objectID>`
    
    * Arguments: `None`

    1. `$ curl 127.0.0.1:5000/meta`
    2. This will provide a list of all available parents
    3. `{"valid_parent_ids": ["example"]}`
    4.  `curl 127.0.01:5000/meta/example`
    5. Will return information relating specifically to that objectID
    6. ```json
        {
         "main": {
           "objectID": "example", 
           "parallelLoc": "/var/tmp", 
           "cloudLoc": "test", 
           "verificationHash": null, 
           "parentID": null, 
           "time": "2018-12-06 02:01:32", 
           "cloudVendor": "gcloud",
         },
        }
        ```
* DELETE
    
    * Resource: `\meta\<objectID>`
    
    * Arguments: `None`

    1. `$ curl 127.0.0.1:5000/meta -X DELETE`
    2. Calling DELETE for metadata without supplying a objectID
    3. `{"ERROR": "No objectID supplied"}`
    4. `$ curl 127.0.0.1:5000/meta/invalid -X DELETE`
    5. Attempting to DELETE a non-existent object results in an error.
    6. `{"False": "Error: Unable to identify invalid"}`
    7. `$ curl 127.0.01:5000/meta/example -X DELETE`
    8. This will remove the object from the database but **NOT** the data, this will only affect the meta data database.
    9. `{"True": "Success: Removed example"}`

* PUT

    * Resource: `\meta`
    
    * Argument: `backup=<bool>` & `restore=<bool>`
    
    1. `$ curl 127.0.01:5000/meta -X PUT`
    2. `{"error": "backup or restore must be declared"}`
    3. The process requires use of the associate boolean arguments, for instance.
    4. `$ curl 127.0.01:5000/meta -X PUT -d "backup=True"`
    5. `{"success": "database backup"}`
    6. You will then find the database under the (default) `db_backup_advdb18` bucket

#### Parallel
?

#### Cloud
?