import boto3
import json
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    CheckACLs = CheckACL()
    CheckACLs.check_grant_buckets()
    CheckACLs.check_policy_bucket()

class CheckACL:
    def __init__(self):
        self.s3_client = boto3.client('s3'
                                      )
        self.s3_resource = boto3.resource('s3'
                                          )

    def check_grant_buckets(self):
        public_bucket_list = list()
        for bucket in self.s3_resource.buckets.all():
            acl = bucket.Acl()
            for grant in acl.grants:
                if grant['Grantee']['Type'].lower() == 'group' \
                        and grant['Grantee']['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers':
                    grant_permission = grant['Permission'].lower()
                    print("\nThe bucket \"", bucket.name, "\"is having public access and below are permissions:")
                    public_bucket_list.append(bucket.name)

                    if grant_permission == 'read':
                        print('Read - Public Access: List Objects')

                    elif grant_permission == 'write':
                        print('Write - Public Access: Write Objects')

                    elif grant_permission == 'read_acp':
                        print('Write - Public Access: Read Bucket Permissions')

                    elif grant_permission == 'write_acp':
                        print('Write - Public Access: Write Bucket Permissions')

                    elif grant_permission == 'full_control':
                        print('Public Access: Full Control')
        return public_bucket_list

    def check_policy_bucket(self):
        for bucket in self.s3_resource.buckets.all():
            bucket_policy = self.s3_resource.BucketPolicy(bucket.name)
            try:
                policy_obj = bucket_policy.policy
            except Exception as e:
                continue
            policy = json.loads(policy_obj)
            #print("\nThe Policy for the bucket \"", bucket.name, "\" is:")

            if 'Statement' in policy:
                for p in policy['Statement']:
                    if p['Principal'] == '*':  # any public anonymous users!
                        print(p['Action'])




# CheckACLs= CheckACL()
# CheckACLs.check_grant_buckets()
# CheckACLs.check_policy_bucket()
