# Recommended Architecture

For teams who are starting with MLOps, we suggest to have at least two Azure Machine Learning instances. ![Dev and Prod](../media/devprd.png)
For teams with more familiarity with MLOps and Azure, we recommend to have three environments. ![Dev, Test and Prod](../media/devtestprd.png)

**Note**: In the current version of Model Factory, the infrastructure is provisioned in a public network configuration. Support for provisioning the infrastructure in a Private networking configuration is forthcoming in a future release.

If you want to learn more about best practices, you can visit [Azure CloudFramework Best Practices](https://docs.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/ai-machine-learning-resource-organization)
