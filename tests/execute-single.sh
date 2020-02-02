#!/bin/bash

if [ ! -d $1 ]; then
    echo "You must run this script from within the tests/ directory"
    exit
fi

ACCOUNT=`aws sts get-caller-identity | jq -r '.Account'`

if test -f "$1/support.yaml"; then
    aws cloudformation deploy --template-file $1/support.yaml --stack-name $1-support --capabilities CAPABILITY_NAMED_IAM --region us-east-1
fi
aws cloudformation deploy --template-file $1/role.yaml --stack-name $1-role --capabilities CAPABILITY_NAMED_IAM --region us-east-1
aws cloudformation deploy --template-file $1/create.yaml --stack-name $1 --capabilities CAPABILITY_NAMED_IAM --region us-east-1 --role-arn arn:aws:iam::$ACCOUNT:role/$1-cfnservicerole
if test -f "$1/support2.yaml"; then
    aws cloudformation deploy --template-file $1/support2.yaml --stack-name $1-support --capabilities CAPABILITY_NAMED_IAM --region us-east-1
fi
if test -f "$1/update.yaml"; then
aws cloudformation deploy --template-file $1/update.yaml --stack-name $1 --capabilities CAPABILITY_NAMED_IAM --region us-east-1 --role-arn arn:aws:iam::$ACCOUNT:role/$1-cfnservicerole
fi
if test -f "$1/support2.yaml"; then
    echo "Rolling back dependency chain: $1"
    aws cloudformation deploy --template-file $1/create.yaml --stack-name $1 --capabilities CAPABILITY_NAMED_IAM --region us-east-1 --role-arn arn:aws:iam::$ACCOUNT:role/$1-cfnservicerole
    aws cloudformation deploy --template-file $1/support.yaml --stack-name $1-support --capabilities CAPABILITY_NAMED_IAM --region us-east-1
fi
exit
echo "Deleting stack: $1"
aws cloudformation delete-stack --stack-name $1 --region us-east-1
aws cloudformation wait stack-delete-complete --stack-name $1 --region us-east-1
echo "Deleting stack: $1-role"
aws cloudformation delete-stack --stack-name $1-role --region us-east-1
aws cloudformation wait stack-delete-complete --stack-name $1-role --region us-east-1
if test -f "$1/support.yaml"; then
    echo "Deleting stack: $1-support"
    aws cloudformation delete-stack --stack-name $1-support --region us-east-1
    aws cloudformation wait stack-delete-complete --stack-name $1-support --region us-east-1
fi
