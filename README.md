# CloudFormation Service Role Generator

> :construction: **WORK IN PROGRESS**

Generates an IAM policy for the CloudFormation service role that adheres to least privilege.

Policies will be created with data following the below preference:
1. Per-type mappings created by incrementally increasing required permissions
2. Permissions retrieved from the [CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html)
3. No data available (a warning will be shown for missed types)

## Usage

### Basic Examples

```
$ python3 index.py -i test.yaml

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
$ python3 index.py --stack-name mystack

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
