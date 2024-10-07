"""
A module to define the Pipeline class for setting up and managing pipeline job properties.
"""

class PipelineJobConfig:
    """
    A class to set up the common properties of a pipeline job.
    """

    def __init__(
        self,
        environment_name: str,
        build_reference: str,
        published_model_name: str,
        dataset_name: str,
        build_environment: str,
        wait_for_completion: str,
        output_file: str,
        model_name: str,
    ):
        """
        Initialize the pipeline job components.

        Args:
            environment_name (str): The name of the environment to use for pipeline execution.
            build_reference (str): The build reference for the pipeline job.
            published_model_name (str): The name of the published model.
            dataset_name (str): The name of the dataset.
            build_environment (str): The build environment configuration.
            wait_for_completion (str): Whether to wait for the pipeline job to complete.
            output_file (str): A file to save the run ID.
            model_name (str): The name of the model.
        """
        self.environment_name = environment_name
        self.build_reference = build_reference
        self.published_model_name = published_model_name
        self.dataset_name = dataset_name
        self.build_environment = build_environment
        self.wait_for_completion = wait_for_completion
        self.output_file = output_file
        self.model_name = model_name