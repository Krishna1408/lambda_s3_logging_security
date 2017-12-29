# lambda_s3_logging_security

This python code is use to create two lambda functions for S3. This lambda functions when run:
1. Finds all the public ACL buckets
2. Enable S3 logging for the buckets name specified.

## Usage:

A. The first lambda "find_public_acl.py"  will find all the public ACL buckets and output their permissions.

B. The second lambda "s3_logging.py" will:
1. Create a S3 bucket to store the logs. If you rerun the code the s3 bucket will not be re-created.
2. Enable logging for the s3 bucket list provided in "ideal_policy.json":
```YAML
   "account_number" : "your aws account ID",
   "s3_bucket_log_name" : "prefix to be used for new s3 bucket to be created",
   "region_name_store_s3_logs" : "Region where you want to create new s3 buket",
   "s3_bucket_log_enable_list":["list of s3 buckets where logging should be enabled"]
  ```
   ## Resources Created:
 
     S3 bucket is created by name: bucket_prefix-account_number-region_name
     
