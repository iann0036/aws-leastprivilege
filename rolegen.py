import boto3
import yaml
import json


class RoleGen:
    def __init__(self, args):
        self.input_file = args.input_file
        self.stack_name = args.stack_name
        self.region = args.region

        self.cfnclient = boto3.client(
            'cloudformation', region_name=self.region)
        self.simple_permissions = []
        self.skipped_types = []

    def generate(self):
        if self.input_file:
            with open(self.input_file, "r", encoding="utf-8") as f:
                template = yaml.safe_load(f.read())
        else:
            raise Exception("No template provided")

        if "Resources" not in template:
            raise Exception("Resources not in template")

        for resname, res in template["Resources"].items():
            self.get_permissions_for_type(res["Type"])

        policy = {
            "PolicyName": "root",
            "PolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": list(set(self.simple_permissions)),
                        "Resource": "*"
                    }
                ]
            }
        }

        if len(self.skipped_types) > 0:
            print("WARNING: Skipped the following types: {}\n".format(", ".join(list(set(self.skipped_types)))))

        print(json.dumps(policy, indent=4, separators=(',', ': ')))

        list(set(self.simple_permissions))

    def get_permissions_for_type(self, restype):
        remote_type_def = self.cfnclient.describe_type(
            Type='RESOURCE',
            TypeName=restype
        )

        if remote_type_def['DeprecatedStatus'] != "LIVE":
            self.skipped_types.append(restype)
            return

        type_schema = json.loads(remote_type_def['Schema'])
        if "handlers" not in type_schema:
            self.skipped_types.append(restype)
            return

        for handler in ["create", "delete", "list", "read", "update"]:
            if handler in type_schema["handlers"] and "permissions" in type_schema["handlers"][handler]:
                self.simple_permissions += type_schema["handlers"][handler]["permissions"]
