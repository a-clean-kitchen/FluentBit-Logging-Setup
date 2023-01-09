from aws_cdk import (
    aws_iam as iam,
    Stack,
    aws_eks as eks
)
from constructs import Construct

import hashlib
import base64
import json
import re

from fluent_bit_setup.aws_interface import AWSInterface


class FluentBitSetupStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.clusterRegion = self.node.try_get_context("eksConfig")["region"]
        self.clusterName = self.node.try_get_context("eksConfig")["clusterName"]
        
        # Create the EKSInterface object
        aws_interface = AWSInterface(
                            self.clusterRegion,
                            self.clusterName
                        )

        self.OIDCUrl = aws_interface.cluster_info["identity"]["oidc"]["issuer"]

        # Get CA Thumbprint for EKS Cluster
        ClusterCA = aws_interface.cluster_info['certificateAuthority']['data']
        public_bytes = base64.b64decode(ClusterCA)
        sha1digest = hashlib.sha1(public_bytes).hexdigest()
        ClusterThumbprint = "".join(sha1digest[i : i + 2] for i in range(0, len(sha1digest), 2))
       
        if not aws_interface.test_oidc_provider(self.OIDCUrl):
            IAMOIDCProvider = iam.OpenIdConnectProvider(self, "OIDCProvider",
                url = self.OIDCUrl,
                client_ids = ["sts.amazonaws.com"],
                thumbprints = [ClusterThumbprint]
            )

        else:
            print("Referencing existing OIDC Provider")
            IAMOIDCProvider =   iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(self,
                                    "OIDCProvider",
                                    open_id_connect_provider_arn = aws_interface.oidc_provider_arn(self.OIDCUrl)
                                )
        
        # Create OIDC Provider Principal
        Principal = iam.OpenIdConnectPrincipal(IAMOIDCProvider,
                        conditions={
                            "StringEquals": {
                                f"""{aws_interface.cluster_info['identity']['oidc']['issuer'].split("https://")[-1]}:aud""": "sts.amazonaws.com",
                                f"""{aws_interface.cluster_info['identity']['oidc']['issuer'].split("https://")[-1]}:sub""": "system:serviceaccount:amazon-cloudwatch:fluent-bit"
                            }
                        }
                    )

        # Create IAM Role for Fluent Bit
        FluentBitRole = iam.Role(self, "FluentBitRole",
                                 assumed_by = Principal,
                                 description = "A Role for the Fluent Bit Service Account running in EKS",
                                 role_name = f"{self.clusterName.split('StaEksCluster')[-1]}-FluentBitRole"
                        )
        
        # Load up the IAM Policy in iam_resources/policy
        with open("./fluent_bit_setup/iam_resources/policy/FluentBitCloudWatchLogs.json") as f:
            p = json.load(f)

        def nested_replace( structure, original, new ):
            if type(structure) == list:
                return [nested_replace( item, original, new) for item in structure]

            if type(structure) == dict:
                return {key : nested_replace(value, original, new)
                            for key, value in structure.items() }

            if structure == original:
                return new
            else:
                return structure

        # Update policy with correct Account Number
        statementCount = 0
        for statement in p["Statement"]:
            resourceCount = 0
            for resource in statement["Resource"]:
                if resource == "*":
                    continue
                update = re.sub(":[0-9]{12}:", f":{aws_interface.get_account_id()}:", resource)
                p = nested_replace(p, resource, update)
                resourceCount += 1
            statementCount += 1

        # Attach the IAM Policy to the Role
        FluentBitPermsPolicy =  iam.Policy(self, "FluentBitPermsPolicy",
                                          document = iam.PolicyDocument().from_json(p)
                                )

        FluentBitPermsPolicy.attach_to_role(FluentBitRole)

#! TODO: Clean up this cursed mess of code
