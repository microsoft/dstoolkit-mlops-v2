# Public Workspace
In order to use this code to deploy your Infrastructure as Code you need to have the following.

- subscription_id: sub id from your azure subscription
- tenent_id: id of the tenant you are using with the sub id.
- client id: the service priciple linked to your sub id
- client sercret: the service sercret linked with your id.

Then make sure you have the correct permissions to create said id and account.

## Step 1) Deploay with Terraform
- Make sure you have terraform installed on the machine if not. Install it here[https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli]
  1) Go into the directory of terraform public_workspace
  2) Run `terraform init` to initiate the terraform state
  3) Run `terraform plan` to varify you can create the resources from the state.
  4) Run `terraform apply --auto-approve` to create the resources.
