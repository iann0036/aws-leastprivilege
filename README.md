# CloudFormation Service Role Generator

> :construction: **WORK IN PROGRESS**

Generates an IAM policy for the CloudFormation service role that adheres to least privilege.

## Installation

```
pip3 install cfnlp
```

## Usage

### Basic Examples

```
$ cfnlp -i test.yaml

{
    "PolicyName": "root",
    "PolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AccessAnalyzer-Create1-reg",
                "Effect": "Allow",
                "Action": [
                    "access-analyzer:TagResource",
                    "access-analyzer:CreateAnalyzer"
                ],
                "Resource": "*"
            },
            {
                "Sid": "AccessAnalyzer-Delete1-reg",
                "Effect": "Allow",
                "Action": "access-analyzer:DeleteAnalyzer",
                "Resource": "*"
            },
            {
                "Sid": "LambdaFunction-Create1",
                "Effect": "Allow",
                "Action": "lambda:CreateFunction",
                "Resource": "arn:aws:lambda:us-east-1:123456789012:function:*"
            },
            {
                "Sid": "LambdaFunction-Create2",
                "Effect": "Allow",
                "Action": "iam:PassRole",
                "Resource": "arn:aws:iam::123456789012:role/S3Access",
                "Condition": {
                    "StringEquals": {
                        "iam:PassedToService": "lambda.amazonaws.com"
                    }
                }
            },
            ...
        ]
    }
}
```

```
$ cfnlp --stack-name mystack

{
    "PolicyName": "root",
    "PolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "myresource-Create1-reg",
                "Effect": "Allow",
                "Action": "ec2:ImportKeyPair",
                "Resource": "*"
            }
            ...
        ]
    }
}
```

### Options

The following command line arguments are available:

#### -i, --input-filename <filename>

The filename of a local CloudFormation template file to analyze. You must specify either this option or `--stack-name`.

#### --stack-name <stackname>

The stack name or stack ID of a deployed CloudFormation stack to analyze. You must specify either this option or `-i, --input-filename`.

#### --include-update-actions

When specified, actions relating to stack updates (that don't trigger a resource replacement) will be included in the output if a value for its property has been set. The default behaviour will not include the actions for stack updates.

#### --consolidate-policy

When specified, the `Sid` fields will be removed and statements sharing the same attributes except `Action` will be combined.

#### --region <name>

Overrides the region to specify in policy outputs and when retrieving deployed templates. By default, the region will be retrieved using the [default precedence](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#configuring-credentials) for Boto3.

#### --profile <name>

When specified, the specified named profile credentials will be used for all data gathering AWS actions. The `AWS_PROFILE` environmental variable would also be respected if this property is not set.

## Policy Generation Logic

Policies will be created with data following the below preference:
1. Per-type mappings created by incrementally increasing required permissions
2. Permissions retrieved from the [CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html)
3. No data available (a warning will be shown for missed types)

### For supported per-type mapping resources

The generated policy will be as specific as possible when specifying actions, resources and conditions. Wildcard actions are never used and all conditions that are available will be populated unless:

* The condition would take no effect or there is not enough information to specify the condition, or
* The condition is a [global condition](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html), or
* The condition applies to an update statement and would prevent the field from being freely changed, or
* The condition relates to the tag keys/values

Resources may be fully or partially wildcarded however will be as specific as possible.

Update statements are disabled by default. If enabled with the `--include-update-actions` option, only properties that have a value specified in the template will have an associated update statement that allows that value to be changed. Permissions required to add new properties may not have the permissions included in the policy.

### For permissions retrieved from the CloudFormation Registry

The generated policy will only include the actions specified in the resource type specification provided by the registry. All resources will be wildcarded and no conditions will apply.

## Supported Resource Types

The following resource types are supported with a per-type mapping:

* AWS::CloudWatch::Alarm
* AWS::EC2::Instance
* AWS::EC2::SecurityGroup
* AWS::IAM::Role
* AWS::Lambda::Function
* AWS::Lambda::Version
* AWS::S3::Bucket
* AWS::SNS::Topic
* AWS::SQS::Queue
