#!/bin/env bash

# List of AWS Regions
AWSREGIONS=(
	"us-east-1"
	"us-east-2"
	"us-west-1"
	"us-west-2"
	"ca-central-1"
	"eu-central-1"
	"eu-west-1"
	"eu-west-2"
	"eu-west-3"
	"eu-north-1"
	"ap-northeast-1"
	"ap-northeast-2"
	"ap-southeast-1"
	"ap-southeast-2"
	"ap-south-1"
	"sa-east-1"
)

TOOL=$1

# Check if tool is "cluster-list" or "find-region"
if [ "$TOOL" = "cluster-list" ]; then
	# List all clusters
	for REGION in "${AWSREGIONS[@]}"; do
		echo "Region: $REGION"
		aws ecs list-clusters --region $REGION
	done
elif [ "$TOOL" = "find-region" ]; then
	# Find the region of a cluster
	CLUSTER=$2
	# Check if cluster is provided
	if [ -z "$CLUSTER" ]; then
		echo "Cluster name is required"
		echo "Usage: $0 <cluster-list|find-region> <cluster-name>"
		exit 1
	fi
	for REGION in "${AWSREGIONS[@]}"; do
		if [ -n "$(aws eks describe-cluster --region $REGION --name $CLUSTER --query cluster.arn --output text)" ]; then
			echo "$REGION"
			break
		fi
	done
else
	echo "Usage: $0 <cluster-list|find-region> <cluster-name>"
fi


