#!/bin/bash

if [ ! -d "AWS-Lambda-Function" ]; then
    echo "You must run this script from within the tests/ directory"
    exit
fi

TEMPLATES=`find * -maxdepth 1 -type d | sed 's/.\///'`
ACCOUNT=`aws sts get-caller-identity | jq -r '.Account'`

for f in $TEMPLATES
do
    if test -f "$f/support.yaml"; then
        aws cloudformation deploy --template-file $f/support.yaml --stack-name $f-support --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-2
    fi
    aws cloudformation deploy --template-file $f/role.yaml --stack-name $f-role --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-2
    aws cloudformation deploy --template-file $f/create.yaml --stack-name $f --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-2 --role-arn arn:aws:iam::$ACCOUNT:role/$f-cfnservicerole
    aws cloudformation deploy --template-file $f/update.yaml --stack-name $f --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-2 --role-arn arn:aws:iam::$ACCOUNT:role/$f-cfnservicerole
    echo "Deleting stack: $f"
    aws cloudformation delete-stack --stack-name $f --region ap-southeast-2
    aws cloudformation wait stack-delete-complete --stack-name $f --region ap-southeast-2
    echo "Deleting stack: $f-role"
    aws cloudformation delete-stack --stack-name $f-role --region ap-southeast-2
    aws cloudformation wait stack-delete-complete --stack-name $f-role --region ap-southeast-2
    if test -f "$f/support.yaml"; then
        echo "Deleting stack: $f-support"
        aws cloudformation delete-stack --stack-name $f-support --region ap-southeast-2
        aws cloudformation wait stack-delete-complete --stack-name $f-support --region ap-southeast-2
    fi
done
