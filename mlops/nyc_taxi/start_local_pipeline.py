"""The script invokes prepare_and_execute to test it from a local computer."""
from mlops.nyc_taxi.src import mlops_pipeline

if __name__ == "__main__":
    mlops_pipeline.prepare_and_execute("pr", "True", None)
