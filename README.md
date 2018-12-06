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
2. `$ cd AdvDB-Prototype`
3. `$ pip install . --user`
4. `export PATH=$HOME/.local/bin:$PATH`

### Prototype Demonstration
After completing the installation, starting the program is easy.

* `$ union-prototype`

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
           "cloudVendor":"gcloud"
        }
        ```
    3. `{"true": "Successfully POST object example"}`
* GET

    * Resource: `\meta\{objectID}`
    
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
           "cloudVendor": "gcloud"
         }
        }
        ```
* DELETE
    
    * Resource: `\meta\{objectID}`
    
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
* GET

    * Resource: `/parallel/{objectID}/{targetFileLocation}`
    
    * Arguments: `newObjID=<string>` & `removeAfter=<bool>`

    1. ?

* PUT

    * Resource: `/parallel/{objectID}/{targetFileLocation}`
    
    * Arguments: `split=<int>` & `join=<int>` & `newObjID=<string>` & `removeAfter=<bool>` 

    1. ?

#### Cloud
* GET

    * Resource: `/cloud/{objectID}`

    * Arguments: `removeAfter=<bool>` & `download=<bool>`

    1. GET can be used in a similar method that of other methods in order to obtain information on a file.
    2. `$ curl 127.0.0.1:5000/cloud -X GET`
    3. Returns list of current top level parentIDs
    4. `$ curl 127.0.0.1:5000/cloud/workingCode.tar.gz -X GET`
    5. Information regarding a specific file, in this case `workingCode.tar.gz`
    6. Can employee additional flags to `download` the ObjectID we specified
    7. `$ curl 127.0.0.1:5000/cloud/workingCode.tar.gz -X GET -d "download=true"`
    8. The file will download to the defined parallelLoc and since a verificationHash is present it will be checked
    9. `$ ls /var/tmp` --> `workingCode.tar.gz`
    10. `$ curl 127.0.0.1:5000/cloud/workingCode2.tar.gz -X GET -d "download=true"`
    11. `{"error": "hash does not match BADHASH  !=  2d5b4b3740a4312cd67ccc80c1503b55"}`
    12. Above you can see that the download will fail if that hash is present but does not match, the file will then be removed from the system.
    13. The final argument that can be used is `removeAfter`, it will remove from cloud after the process is complete.
    14. `$ curl 127.0.0.1:5000/cloud/remove1 -X GET -d "download=true" -d "removeAfter=true"`
    15. The above statement will download the file from the appropriate cloudLoc but then remove it from that same location (after successful download) then update the database to match.
    16. `{"success": "remove1 downloaded to /var/tmp and removed from Cloud"}`
    
* PUT

    * Resource: `/cloud/{objectID}/{cloudVendor}/{cloudLoc}/mpi/{nodes}`
    
    * Arguments: `newObjID=<string>` & `removeAfter=<bool>`

    1. `$ curl 127.0.0.1:5000/cloud/bad -X PUT`
    2. ObjectID is verified --> `{"error": "invalid original objectID"}`
    3. `$ curl 127.0.0.1:5000/cloud/putExample/dropbox -X PUT`
    4. CloudVendor is verified (supported only) --> `{"error": "unsupported cloud_vendor"}`
    5. `$ curl 127.0.0.1:5000/cloud/putExample/gcloud -X PUT`
    6. CloudLoc must be present (not necessarily existing) --> `{"error": "no cloud location can be established"}`
    7. `$ curl 127.0.0.1:5000/cloud/putExample/gcloud/my-test-bucket-987 -X PUT`
    8. If the `newObjID` argument is provided the system will use this ObjectID instead and create a new instance in the database. The old object will remain the same.
    9. `$ curl 127.0.0.1:5000/cloud/putExample/gcloud/my-test-bucket-987 -X PUT`
    10. The above will upload ("PUT") the file in the defined parallel location to the supplied bucket.
    11. `{"success": "uploaded file"}`
    12. The success message is minimal; however, if we examine the Google Cloud Storage platform we will see that 
    in the `my-test-bucket` that there is now the `putExample` file and the database looks as such:
    
    | objectID | parallelLoc | cloudLoc | cloudVendor | verificationHash | parentID | time |
    |----------|-------------|----------|-------------|------------------|----------|------|
    | putExample | /var/tmp | my-test-bucket-987 | gcloud | 52cd12842fecfe47b404c758773b913b | null | 2018-12-05 13:51:56 |
    
    13. Similar to the GET API, there is support for a `removeAfter` argument that will remove the local parallel instance of the object 
    after the upload has been completed.
    
    * MPI
        1. ?  