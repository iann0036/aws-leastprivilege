# CloudFormation Service Role Generator

> **WORK IN PROGRESS**

Generates an IAM policy with the permissions

```
$ python3 index.py -i test.yml

WARNING: Skipped the following types: AWS::S3::Bucket

{
    "PolicyName": "root",
    "PolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "access-analyzer:CreateArchiveRule",
                    "access-analyzer:ListArchiveRules",
                    "access-analyzer:ListAnalyzers",
                    "access-analyzer:UpdateArchiveRule",
                    "access-analyzer:DeleteArchiveRule",
                    "access-analyzer:CreateAnalyzer",
                    "access-analyzer:UntagResource",
                    "access-analyzer:DeleteAnalyzer",
                    "access-analyzer:TagResource"
                ],
                "Resource": "*"
            }
        ]
    }
}
```
