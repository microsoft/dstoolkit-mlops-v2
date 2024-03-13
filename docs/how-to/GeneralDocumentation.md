# General Documentation

## Data Science Lifecycle Base Repo

The base project structure was inspired by the following [dslp repo](https://github.com/dslp/dslp-repo-template). We readapted it to support minimal MLOps principles.


## MLOps template guidelines

There exist many different MLOps templates and implementation examples. The main challenge facing most of them is that they either follow a structure fine-tuned to a reduced set of use cases or they constrain  experimentation too much. As a rule of thumb, there are two questions to ask when assessing the quality of your template.

1. How easy is it to debug the code when the CD pipeline fails ?
2. How easy is it to add new functionality or adapt your code when environments (stage/prod/...) or use cases change?

In essence, the first question that arises is around the extent to which the data scientist's experimentation code differs from the deployment process. The second question deals with managing the risk of "overfitting" to the use case. Thus, keeping these two questions in mind, we can try defining a "common denominator" folder structure and process to generalize a solution to both.

Next, we need to acknowledge that there are different levels of MLOps implementation as with any framework. For instance, take for example _Scrum_. When a team or an organization is moving from an _Waterfall_ approach to _Scrum_ approach, the change is implemented in a step-wise manner. It is rarely the case that a team successfully implements all the _Scrum_ guidelines at once. On the other hand, it is worth noting that applying only a few principles will not bring the expected benefits. For instance, only doing "standup meetings" and having a "sprints" will not create a successful scrum team. Hence, we see that there are different levels when it comes to applying a new framework but it is necessary to define the minimum principles to follow in order to create value. 

Here is an example of a set of minimum (Level 1) MLOps requirements and the full (level 3,4,...) requirements

| Aspects     | Minimum Requirement                                                                                                        | Full Requirement                                                                                                                  |
| ----------- | -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Environment |  dev: for experimentation and coding<br> prod (or stage or whatever you fancy): the environment hosting the whole solution | dev/stage/prod and others if required                                                                                             |
|             |                                                                                                                            |                                                                                                                                   |
| Code        | CD integration pipeline for automated training pipeline and scoring service                                                | CI pipeline on Master branch (or other branch)<br>CD pipeline for integration of all parts: training,                             |
|             |                                                                                                                            |                                                                                                                                   |
| Data        | Raw data are centralised and updated automatically                                                                         | Data validation<br>Data drifts detection<br>Feature store for reusability                                                         |
|             |                                                                                                                            |                                                                                                                                   |
| Model       | Model performance logged during training                                                                                   | Automated model validation against holdout set<br>trigger for automated training<br>scored data and results logged<br>A/B Testing |

This template will provide the basic elements to quickly setup a minimal MLOps processes so that the team can move quickly from the basic level to the most advanced MLops implementation.

## Azure Machine Learning

Azure machine learning provides a range of different APIs and tools to create an optimal MLOps infrastructure. We will review the different tools and provide some recommendation on how to best leverage the latter. We will focus the review on managing data, and training and scoring processes.

### Training in Azure

It is important to understand how training is performed in Azure. In essence, one writes normal core machine learning scripts like train.py, score.py, etc and another set of separate scripts that will perform environment configuration and execute the core scripts on a remote machine such as a VM or AKS cluster as explained [here](https://docs.microsoft.com/en-us/azure/machine-learning/concept-environments). One can choose to either use python scripts (or R) to execute the remote run or Azure CLI. We do not recommend the latter as it constrains experimentation too much.

For simplicity, I will call refer to a set of important scripts as "Core Scripts" that you can find in the **src folder**, and the other set as "Ops Scripts", saved in the **mlops folder**. Why is this distinction so important ? Azure has different ways for handling credentials and each set of scripts use different approaches to handle access to the workspace and datasets. We discuss this point in the next section.

### Workspace/Secrets

The central piece of Azure ML is the Workspace. Every process is executed or linked to it Workspace, as for instance when retrieving datasets, uploading models to the registry, running automl, etc. There are 3 main way to retrieve the values:

1. The most straight forward is through the Azure Portal. You can download the _config.json_ from your aml resource page. This method is used for Core and Ops scripts when developing on the local machine.
2. Through the _run_ object. This is used in Core Scripts to access the workspace when run on remote compute. An example can be [found here](https://github.com/Azure/MachineLearningNotebooks/blob/71861278041bfc37557293adb94d844e5e36e60e/how-to-use-azureml/automated-machine-learning/regression-explanation-featurization/train_explainer.py). 

```
run = Run.get_context() 
ws = run.experiment.workspace
```

3. Through a service principal stored as environment variable. This method is used in devops pipelines when performing integration. To generate and use service principals follow [this link](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-setup-authentication)

In the **src** and **mlops** folder, one can find the _utils.py_ scripts that shows how the credentials are retrieved.

Now that we know how to get the workspace credentials we can show how to train a model, handle the data, and define a scoring script.

### Variable Handling

**!DO NOT ADD ANY SECRETS OR KEYS IN CONFIGURATION FILES!**

There are many constants and variables to handle in a data science project, as for instance the dataset names, the model names, model variables, etc. It is important to distinguish between configuration variables and environment variables. Indeed, environment variables only depend on the environment in which a script is run, i.e dev/stage/prod (or whatever the convention). Hence, we recommend to understand what needs to be stored in a config/settings file and what should come from the os environment. It is not necessary to define a specific _.ENV_ files as the variables will be added in the CI/CD pipelines in Azure DevOps (or whatever DevOps tool one uses). When developing in dev, we can simply use the default function ```os.getenv('ENV_VARIABLE', 'your-dev-env-variable')```.

For standard configuration variables, there is **one main guideline to follow**: Core Scripts should not contain any hardcoded variables in the code! All variables must come from the scripts argument and may be hardcoded in the argument as a default value as follows ``args.add_argument('--model_name',default='mymodel.pkl', type=str, help='')``. You might ask yourself now: 'why this strange rule?'. Well, all variables ought to be in configuration files in a single place. This helps with quickly adding/removing/updating variables - 'Ok, but we could still have added them to our Core Scripts'. Again, you must remember that these scripts will eventually be run by our Op Scripts. These Op Scripts can easily handle the arguments from a config file to forward them to the Core Scripts. Indeed, the Op Scripts are commonly run in a virtual agent which contains all the project files. Thus, the path to the configuration will always be constant and there is no need to use ``sys.path`` or other cumbersome tricks to find the correct path.

We recommend using _yaml_ files for general variables. The reason is that it gives more flexibility when operationalising the solution in that one can choose whether to use the python SDK or CLI, which is preferred respectively by Data Scientist and DevOps Engineers. Loading variables from a _yaml_ into another one is straightforward as documented in [this page](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/templates?view=azure-devops#variable-reuse)

### Training

There are 4 different ways in AML to run a training script. The full explanation can be [found here](https://docs.microsoft.com/en-us/azure/machine-learning/concept-train-machine-learning-model)

1. **Run_config**: this approach is useful if you want either quickly setup your environment or spend time fine tuning it. Also, it can be used to execute pyspark job on hdinsights.
2. **Estimator**: this is probably the most straightforward method. Azure has a setup of pre-configured environments that are very useful when using deep learning frameworks like TensorFlow, Pytorch, etc. Of course, it also accepts your conda environment or pip requirements file.
3. **AutoMl**: very simple way to generate automated model training. It doesn't need any Core Scripts. As a side note, if one doesn't like using this service, we recommend testing it as a baseline to your custom model.
4. **Machine Learning Pipeline**: very useful when one needs to run a sequence of scripts or uses a "multi-model" approach as for instance in demand forecasting where one model is trained per product.

All the approaches can handle the data inputs by either passing them as arguments from the Ops Scripts to the Core Scripts or inside the latter. We discuss how to manage the data in the next section.

### Data

As stated before, we assume that all the data assets are stored in a single source. With AML, there are 3 different way to upload,download,load,save data :

1. Using Data Asset objects directly from the AML SDK
2. Using Data Asset objects passed as arguments to a script and extracted via the _run_ object
3. Using Azure Storage SDK as in [the blob library](https://pypi.org/project/azure-storage-blob/)

**Case (1)**, the datasets are registered in the workspace and thus we need to retrieve the workspace credentials. We already described how to perform that step in the _workspace_ section. Basically, when developing on a local machine, the credentials are retrieved from the portal and stored in a config.json file. When run on a remote machine, the workspace credentials are retrieved from the _run context_.

**Case (2)** is more common when using AML Pipelines as shown in [this example](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-move-data-in-out-of-pipelines)

**Case (3)** is less common but can be leveraged when clients do not wish to use the datastore/dataset functionalities due to security concerns. The main difference is that the access credentials to the data location are handled either directly through keyvault or through the AML workspace (which uses keyvault under the hood).

### Score/Infer

The scoring part is probably the least trivial to generalize. Indeed, it does not only depend on the training approach but also on the customer's constraints. AML proposes different methods to package the code and model, and also diverse deployment targets. Even though there are multiple ways to deploy a script, the core scoring script keeps the same structure most of the time. You can find an example in the _src_ folder.

For the deployment targets, you can find an exhaustive list of targets under [Choose a compute target](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-and-where?tabs=azcli). It is worth noting that all the targets leverage Docker.

We will list the different approaches to packaging your service:

1. If the data science team manages a production target (AKS, VM, etc), the team can use the **Model Deploy** functionality and all the configuration is taken care of, as explained here [under deploy model](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-and-where?tabs=python).

2. In most organizations, the production environment is managed by a dedicated team. For this scenario, one can choose to use the [**aml package**](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-package-models) approach or create a _Flask_ app hosted in a docker. In both cases, the production team receives a docker file to deploy.  
   - **Warning!** when using the aml package functionality, the docker file retrieves a base image from an azure container registry (ACR). This means that the production team has to have access to the ACR.
  
   - In the second case, you have two options: either create your fully custom docker file with flask and download the model from the registry, or download the script from within the scoring script which means docker/aks has to have access to the workspace.

## How to use

See [Testing the Intial Setup](./TestInitialSetup.md)

For guidance on adding your models to the Model Factory see [Onboarding a new model](./OnboardingNewModel.md)

**Note** This solution does not provide any concrete implementation of MLOps, but, rather, it provides a proposed folder structure and some examples to get teams started with Model Factory. Naming conventions and the logical flows adopted by teams in the field are highly dependent on the use cases and models being implemented.
