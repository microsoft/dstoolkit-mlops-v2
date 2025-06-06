"""The script invokes prepare_and_execute to test it from a local computer."""
from mlops.invoice_processing.src import mlops_pipeline

if __name__ == "__main__":
    mlops_pipeline.prepare_and_execute("invoice_processing", "pr", "True", None, None)
