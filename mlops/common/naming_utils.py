"""This module contains a few utility methods that generate names for for experiments, runs, models."""

import subprocess
import os
import re


def generate_experiment_name(model_name: str):
    """
    Generate a unique experiment name based on the current branch name as well as an input parameter.

    Parameters:
     model_name (str): a prefix of the experiment name that usually contains the model name \
        that helps to generate own experiment name for each pipeline in the repository.

    Returns:
        string: experiment name according to the pattern
    """
    git_branch = os.environ.get("BUILD_SOURCEBRANCHNAME")

    if git_branch is None:
        git_branch = subprocess.check_output(
            "git rev-parse --abbrev-ref HEAD", shell=True, universal_newlines=True
        ).strip()

    git_branch = git_branch.split("/")[-1]
    git_branch = re.sub(r"[^a-zA-Z0-9_-]+", "", git_branch)
    return f"{model_name}_{git_branch}"


def generate_model_name(model_name: str):
    """
    Generate a unique model name based on the current branch name as well as an input parameter.

    Parameters:
     model_name (str): a prefix of the experiment name that usually contains the model base name \
        that helps to generate own model name for each pipeline in the repository.

    Returns:
        string: experiment name according to the pattern
    """
    git_branch = os.environ.get("BUILD_SOURCEBRANCHNAME")

    if git_branch is None:
        git_branch = subprocess.check_output(
            "git rev-parse --abbrev-ref HEAD", shell=True, universal_newlines=True
        ).strip()

    git_branch = git_branch.split("/")[-1]
    return f"{model_name}_model_{git_branch}"


def generate_run_name(build_id: str):
    """
    Generate a run name using build_id from the environment or autogenerated guid and run_ as a prefix.

    Parameters:
        build_id (str): the current build id

    Returns:
        string: a unique run name
    """
    build = os.environ.get("BUILD_BUILDID")

    return f"run_{build}"


def generate_environment_name(environment_name, environment_version):
    """
    Generate a unique experiment name based on the environment object.

    Parameters:
        environment_name (str): the name of the environment
        environment_version (str): the version of the environment
    
    Returns:
        string: experiment name according to the pattern
    """

    print(f"Environment: {environment_name}, version: {environment_version}")

    return f"azureml:{environment_name}:{environment_version}"