# Purpose of this document
This document describes the process needed to setup a hosting environment on Azure for one or more machine leaning models.
**Note:**These instructions assume that the reader is using github as their version control system for this project.

**Step 1.** Create a service connection in Azure DevOps. You can use [this document](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml) as a reference. Use Azure Resource Manager as a type of the service connection.

**Step 2.** Clone the repository to a local folder on your machine. Create a branch at the discretion of the user.

**Step 3.** Open the file, /dstoolkit-mlops-v2/infra/bicep/configuration/configuration-infra-DEV.variables.yml, and unless otherwise indicated, accept the existing vaules or set values specific to your environment for the list of properties below:

  >> RESOURCE_GROUP: Set to the name of the resource group that will host the Azure Machine Learning environment 
  >> LOCATION: eastus
  >> NAMESPACE: mlops
  >> PROJECTCODE: dstk
  >> VERSION: Set any string containing only number. For example, 0500
  >> SERVICECONNECTION_RG: dstoolkit-mlops-v2-svc
  >> AMLWORKSPACE: mlw-$(NAMESPACE)-$(PROJECTCODE)-$(VERSION)
  >> STORAGEACCOUNT: staccaml$(NAMESPACE)$(PROJECTCODE)$(VERSION)
  >> KEYVAULT: akvaml$(NAMESPACE)$(PROJECTCODE)$(VERSION)
  >> APPINSIGHTS: aml-ai-$(NAMESPACE)-$(PROJECTCODE)-$(VERSION)
  >> CONTAINERREGISTRY: cr$(NAMESPACE)$(PROJECTCODE)$(VERSION)
  >> VIRTUALNETWORK: aml-vnet-$(NAMESPACE)
  >> PRIVATEDNSZONE: dnszone.api.azureml.ms
  >> PRIVATEDNSZONELINK: dnszonelink.api.azureml.ms
  >> PRIVATEDNSZONEGROUP: dzg$(NAMESPACE)$(PROJECTCODE)$(VERSION)
  >> PRIVATEENDPOINT: aml-pe-$(NAMESPACE)
  >> REQUIRESPRIVATEWORKSPACE: Set to true or false, depending on whether the Azure Machine Learning workspace needs to be configured with a private endpoint.
  
**Step 4.** Commit the changes made above, and synch to the remote repository.

**Step 5.** Create an azure pipeline based on the existing pipeline definition in the repository, PIPELINE-0-setup.yml. 
>> **Step 5a.** In Pipelines in Azure DevOps, click "New Pipeline"
>> **Step 5b.** On the "Select a repository" page, switch to the native Azure DevOps Experience, and select GitHub.
>> **Step 5c.** After selecting "GitHub", select the repository containing code for this project.
>> **Step 5d.** On the "Configure" tab, select  "Existing Azure Pipeline YAML file."
>> **Step 5e.** On the dialog that opens from the right edge of the screen, select the Branch containing the code for this project.
>> **Step 5f.** In the path text box, paste the following relative path, /infra/bicep/PIPELINE-0-setup.yml (OR locate PIPELINE-0-setup.yml and select it in the drop down), and click "Continue".
>> **Step 5g.** On the Review page, using the drop down on the "Run" button, select Save.
>> **Step 5h.** After saving the pipeline, click "Run" to deploy the infrastructure.

