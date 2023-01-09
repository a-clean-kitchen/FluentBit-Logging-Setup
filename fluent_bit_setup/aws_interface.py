#!/usr/bin/env python3

import boto3

class AWSInterface():
    def __init__(self, region: str, cluster_name: str):
        self.region = str(region)
        self.cluster_name = cluster_name
        print("Connecting to EKS cluster: " + cluster_name)
        print("Region: " + region)
        self.eks = boto3.client('eks', region_name = self.region)
        self.iam = boto3.client('iam', region_name = self.region)
        self.sts = boto3.client('sts', region_name = self.region)
        self.cluster_info = self.get_cluster_info()

    def get_cluster_info(self):
        response = self.eks.describe_cluster(name=self.cluster_name)
        return response['cluster']

    # Test for an existing OIDC Provider
    def test_oidc_provider(self, OIDCUrl: str):
        response = self.iam.list_open_id_connect_providers()
        for provider in response['OpenIDConnectProviderList']:
            OIDC_Obj = self.iam.get_open_id_connect_provider(OpenIDConnectProviderArn=provider['Arn'])
            if OIDC_Obj['Url'] == OIDCUrl.split("https://")[-1]:
                return True
        return False

    def oidc_provider_arn(self, OIDCUrl: str):
        response = self.iam.list_open_id_connect_providers()
        for provider in response['OpenIDConnectProviderList']:
            OIDC_Obj = self.iam.get_open_id_connect_provider(OpenIDConnectProviderArn=provider['Arn'])
            if OIDC_Obj['Url'] == OIDCUrl.split("https://")[-1]:
                return provider['Arn']
        return None

    def get_account_id(self):
        response = self.sts.get_caller_identity()
        return response["Account"]


if __name__ == "__main__":

    print(EKS.cluster_info)

