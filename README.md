# Setup FLuentBit in an EKS Cluster

## Tooling
 * `kubectl` is installed
 * `node` is installed and at version 16.16
 * `python` is installed and at version 3.10 (should include `pip`)
 * `aws` CLI is installed
 * `pipenv` is installed

### `pipenv` installation
If you're using bash as your shell:
`pip install --user pipenv`

If your using zsh as your shell:
`pip install --user "pipenv"`

And make sure to run `pipenv install` ;)

## Most important Configuration
In `cdk.json`, you will find all of the relevant cdk "context".
Make sure to edit this accordingly. Idk if it was a good idea,
but this shapes a lot of this project.

```
{
...

    "stackName": "DESIRED NAME OF STACK", 
    "eksConfig": {
        "clusterName": "NAME OF CLUSTER",
        "region": "AWS REGION"

...
}
```
You're gonna want a different `stackName` for each IAM Stack made. (I.E.
for each Cluster)


### Additional Relevant Configuration
 * Make sure that you AWS CLI creds are for the correct account (i.e. The account the targeted cluster is in)
 * For kubectl to work, make sure that your current context is the correct cluster

#### `kubectl` side note
Use `aws eks update-kubeconfig --region <region> --name <cluster name>` to add the desired cluster to your kube config

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
 * `pipenv install`  installs dependencies to virtual environment
 * `bin/clusterTool.sh <cluster-list|find-region> <cluster-name>` list clusters by region or find region of `<cluster-name>`

Enjoy!
