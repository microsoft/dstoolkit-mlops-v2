import mlflow
import argparse
import json
from pathlib import Path


def main(model_metadata, model_name, score_report, build_reference):
    try:
        run_file = open(args.model_metadata)
        model_metadata = json.load(run_file)
        run_uri = model_metadata["run_uri"]

        score_file = open(Path(args.score_report) / "score.txt")
        score_data = json.load(score_file)
        accuracy = score_data["accuracy"]
        precision = score_data["precision"]
        recall = score_data["recall"]
        f1 = score_data["f1"]

        model_version = mlflow.register_model(run_uri, model_name)

        client = mlflow.MlflowClient()
        client.set_model_version_tag(
            name=model_name, version=model_version.version, key="precision", value=precision
        )
        client.set_model_version_tag(
            name=model_name, version=model_version.version, key="recall", value=recall
        )
        client.set_model_version_tag(
            name=model_name, version=model_version.version, key="accuracy", value=accuracy
        )
        client.set_model_version_tag(
            name=model_name, version=model_version.version, key="f1", value=f1
        )

        client.set_model_version_tag(
            name=model_name,
            version=model_version.version,
            key="build_id",
            value=build_reference,
        )

        print(model_version)
    except Exception as ex:
        print(ex)
        raise
    finally:
        run_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("register_model")
    parser.add_argument(
        "--model_metadata",
        type=str,
        help="model metadata on Machine Learning Workspace",
    )
    parser.add_argument("--model_name", type=str, help="model name to be registered")
    parser.add_argument("--score_report", type=str, help="score report for the model")
    parser.add_argument(
        "--build_reference",
        type=str,
        help="Original AzDo build id that initiated experiment",
    )

    args = parser.parse_args()

    print(args.model_metadata)
    print(args.model_name)
    print(args.score_report)
    print(args.build_reference)

    main(args.model_metadata, args.model_name, args.score_report, args.build_reference)
