# CloudFormation Service Role Generator

> **WORK IN PROGRESS**

Generates an IAM policy for the CloudFormation service role that adheres to least privilege.

Policies will be created with data following the below preference:
1. Per-type mappings created by incrementally increasing required permissions
2. Permissions retrieved from the [CloudFormation Registry](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/registry.html)
3. No data available (a warning will be shown for missed types)

## Usage

```
$ python3 index.py -i test.yml

WARNING: Skipped the following types: AWS::S3::Bucket

{
    "PolicyName": "root",
    "PolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AccessAnalyzer-create1-reg",
                "Effect": "Allow",
                "Action": [
                    "access-analyzer:TagResource",
                    "access-analyzer:CreateAnalyzer"
                ],
                "Resource": "*"
            },
            {
                "Sid": "AccessAnalyzer-update1-reg",
                "Effect": "Allow",
                "Action": [
                    "access-analyzer:TagResource",
                    "access-analyzer:UntagResource",
                    "access-analyzer:ListAnalyzers",
                    "access-analyzer:UpdateArchiveRule",
                    "access-analyzer:DeleteArchiveRule",
                    "access-analyzer:CreateArchiveRule"
                ],
                "Resource": "*"
            },
            {
                "Sid": "AccessAnalyzer-delete1-reg",
                "Effect": "Allow",
                "Action": [
                    "access-analyzer:DeleteAnalyzer"
                ],
                "Resource": "*"
            },
            {
                "Sid": "LambdaFunction-create1",
                "Effect": "Allow",
                "Action": [
                    "lambda:CreateFunction"
                ],
                "Resource": "arn:aws:lambda:us-east-1:123456789012:function:*"
            },
            {
                "Sid": "LambdaFunction-create2",
                "Effect": "Allow",
                "Action": [
                    "iam:PassRole"
                ],
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
