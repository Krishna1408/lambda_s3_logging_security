import boto3
import json
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    print("### Enable S3 Bucket Logging ###")
    LoggingEnable = Boto3BucketLogging()
    LoggingEnable.enable_logging()
    print("\n\n\n")
    
    print("### Check for buckets with Public ACL & Policies")
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


    def check_policy_bucket(self):
        for bucket in self.s3_resource.buckets.all():
            bucket_policy = self.s3_resource.BucketPolicy(bucket.name)
            try:
                policy_obj = bucket_policy.policy
            except Exception as e:
                continue
            policy = json.loads(policy_obj)
            print("\nThe Policy for the bucket \"", bucket.name, "\" is:")

            if 'Statement' in policy:
                for p in policy['Statement']:
                    if p['Principal'] == '*':  # any public anonymous users!
                        print(p['Action'])


class Boto3BucketLogging:
    def __init__(self):
        self.policy_file = self.load_default_policy()
        self.bucket_prefix = self.policy_file["s3_bucket_log_name"]
        self.region_name = self.policy_file["region_name_store_s3_logs"]
        self.account_number = self.policy_file["account_number"]
        self.list_buckets = self.policy_file["s3_bucket_log_enable_list"]
        self.s3_client = boto3.client('s3',
                                      region_name=self.region_name)
        self.s3_resource = boto3.resource('s3',
                                          region_name=self.region_name)


    @classmethod
    def load_default_policy(cls):
        with open('ideal_policy.json') as json_data:
            data = json.load(json_data)
        return data

    def get_buckets(self):
        get_buckets = self.s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in get_buckets['Buckets']]
        return buckets

    def create_s3_bucket(self):
        existing_buckets = self.get_buckets()
        new_bucket_name = self.bucket_prefix+"-"+self.account_number+"-"+self.region_name
        canonical_id = self.s3_client.list_buckets()['Owner']['ID']
        if new_bucket_name in existing_buckets:
            pass
        else:
            bucket_created= self.s3_client.create_bucket(Bucket=new_bucket_name, ACL='private', CreateBucketConfiguration ={'LocationConstraint': self.region_name})
            create_acl = self.s3_client.put_bucket_acl(AccessControlPolicy={
                'Grants': [
                    {
                        'Grantee': {

                            'Type': 'Group',
                            'URI': 'http://acs.amazonaws.com/groups/s3/LogDelivery'
                        },
                        'Permission': 'READ_ACP'
                    },
                    {
                        'Grantee': {

                            'Type': 'Group',
                            'URI': 'http://acs.amazonaws.com/groups/s3/LogDelivery'
                        },
                        'Permission': 'WRITE'
                    },
                    {
                        'Grantee': {

                            'Type': 'CanonicalUser',
                            'ID': canonical_id
                        },
                        'Permission': 'FULL_CONTROL'
                    }
                ],
                'Owner': {
                    'DisplayName': 'Owner',
                    'ID': canonical_id
                },

            },
                Bucket=new_bucket_name,
            )

        return new_bucket_name

    def enable_logging(self):
        log_bucket_name = self.create_s3_bucket()

        for buckets in self.list_buckets:
            bucket_logging = self.s3_resource.BucketLogging(buckets)
            if not 'LoggingEnabled' in self.s3_client.get_bucket_logging(Bucket=buckets):
                prefix = "log4"+"-"+buckets+"-"
                enable_logging = bucket_logging.put(BucketLoggingStatus={
        'LoggingEnabled': {
            'TargetBucket': log_bucket_name,
            'TargetPrefix': prefix
        }

    }
                )
                print("logging is enabled for ", buckets)
            else:
                print("Bucket logging is already enabled for ", buckets)

#
# CheckACLs= CheckACL()
# CheckACLs.check_grant_buckets()
# CheckACLs.check_policy_bucket()