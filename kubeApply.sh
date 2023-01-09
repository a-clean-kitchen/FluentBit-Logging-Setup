#!/bin/env sh

# This is a script to properly apply FluentBit from
# manifests.

# Check for kubectl, cdk, aws
command -v kubectl >/dev/null 2>&1 || { echo >&2 "kubectl is required but it's not installed.  Aborting."; exit 1; }
command -v cdk >/dev/null 2>&1 || { echo >&2 "cdk is required but it's not installed.  Aborting."; exit 1; }
command -v aws >/dev/null 2>&1 || { echo >&2 "aws is required but it's not installed.  Aborting."; exit 1; }

# Check if using Node 16.16
if [ -z "$(node --version | grep 'v16.16')" ]; then
	echo "Node version is not 16.16. Please update Node to 16.16 or higher."
	exit 1
fi

# Set cluster name and region
# Check if they want to use cluster from current kubectl context
if [ "$1" = "cdk" ]; then
	cluster_name=$(cdk context -j | jq .eksConfig.clusterName | tr -d '"')
	cluster_region=$(cdk context -j | jq .eksConfig.region | tr -d '"')
else
	if [ -z "$1" ] || [ -z "$2" ]; then
	  	echo "Usage: $0 <cluster-name/\"cdk\"> <aws-region>"
  		exit 1
	fi

	cluster_region=$2
	cluster_name=$1
fi

# Check if kubectl is in the right context
if [ -z "$(kubectl config current-context | grep $cluster_name)" ]; then
	echo "kubectl is not in the right context. Please switch to the right context."
	exit 1
fi

# Read out current config and ask if they want to continue
echo "Cluster name: $cluster_name"
echo "Cluster region: $cluster_region"
echo "Continue? (y/n)"
read continue
if [ "$continue" != "y" ]; then
	echo "Exiting..."
	exit 1
fi

kubectl apply -f ./fluent_bit_setup/kube/01-amazon-cloudwatch-namespace.yaml

FluentBitHttpPort='2020'
FluentBitReadFromHead='Off'
[ ${FluentBitReadFromHead} = 'On' ] && FluentBitReadFromTail='Off'|| FluentBitReadFromTail='On'
[ -z ${FluentBitHttpPort} ] && FluentBitHttpServer='Off' || FluentBitHttpServer='On'
kubectl create configmap fluent-bit-cluster-info \
--from-literal=cluster.name=${cluster_name} \
--from-literal=http.server=${FluentBitHttpServer} \
--from-literal=http.port=${FluentBitHttpPort} \
--from-literal=read.head=${FluentBitReadFromHead} \
--from-literal=read.tail=${FluentBitReadFromTail} \
--from-literal=logs.region=${cluster_region} -n amazon-cloudwatch

kubectl apply -f ./fluent_bit_setup/kube

kubectl annotate serviceaccounts -n amazon-cloudwatch fluent-bit eks.amazonaws.com/role-arn=arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/$(echo $cluster_name | sed s/StaEksCluster//)-FluentBitRole --overwrite

kubectl rollout restart daemonset fluent-bit-compatible -n amazon-cloudwatch
