# Deploy Private or Public Terraform

Follow the steps in Set up for your project in Terraform deployment.

# When to chose which configuration of terraform?
Private Workspace using DNS/VNets and Private Endpoints in order to deploy the workspace. So if you are more security sensitive than most users, private_workspace will best suit your needs.

# SetUp
In order to run the terraform code go to the version you want to deploy. Change the directory to wither private_workspace or public_workspace. Then run the following commands in bash/powershell:
- Run ```bash terraform init```
- Run `terraform plan`
- Run `terraform apply --auto-approve`
