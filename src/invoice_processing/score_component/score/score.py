"""
This module runs the evaluation step of the experimentation framework.
First, the ground truth data and the predictions data are read.
Next, each line item in the ground truth data is compared against
line items from the prediction data to find the best match for
each line item in the ground truth. Finally, the accuracy is
calculated per field and a general accuracy is calculated
for all fields combined.
The score results are logged into AML.
"""

import os
import argparse

import mlflow
import ast
import pandas as pd
import numpy as np
from tqdm import tqdm
from typing import Dict
import logging

from .extraction_evaluator import ExtractionEvaluator
from .utils import load_json_file

log = logging.getLogger(__name__)


def get_score_config(score_config_str):
    """
    Load score config from dict loaded as str.
    Args:
        components_config: Dictionary loaded as string with configuration
    Returns:
        score_config_dict: Dict with score configuration
    """
    log.info(f"score_config from get_score_config in score.py: {score_config_str}")
    score_config = ast.literal_eval(score_config_str)
    # Parse the line_items dict into a list of line item fields to compare (same for the rest)
    fuzzy_match_config = score_config["fuzzy_match_config"]
    exact_match_fields = [k for k, v in score_config["exact_match_fields"].items() if v]
    matchers_dict = score_config["matchers_dict"]
    find_best_matches_strategy = score_config["find_best_matches_strategy"]
    score_config_dict = {
        "fuzzy_match_config": fuzzy_match_config,
        "exact_match_fields": exact_match_fields,
        "matchers_dict": matchers_dict,
        "find_best_matches_strategy": find_best_matches_strategy,
    }
    return score_config_dict


def create_extraction_evaluator(components_config):
    """
    Initialize evaluator object
    Args:
        components_config: Dictionary loaded as string with configuration
    Returns:
        evaluator: Performs data evaluation
    """
    score_config_dict = get_score_config(components_config)
    log.info(f"score config dict from: {score_config_dict}")
    fuzzy_match_config = score_config_dict.get("fuzzy_match_config")
    exact_match_fields = score_config_dict.get("exact_match_fields")
    matchers_dict = score_config_dict.get("matchers_dict")
    find_best_matches_strategy = score_config_dict.get("find_best_matches_strategy")
    evaluator = ExtractionEvaluator(
        fuzzy_match_config=fuzzy_match_config,
        exact_match_fields=exact_match_fields,
        matchers_dict=matchers_dict,
        find_best_matches_strategy=find_best_matches_strategy,
    )
    return evaluator


def get_gt_and_pred_data_for_evaluation(ground_truth, predictions):
    """
    Parse current JSON input to DataFrames
        Args:
            ground_truth: Ground truth JSON object
            predictions: Predictions JSON object
        Returns:
            gt_data: DataFrame of the line items of the ground truth data
            pred_data: DataFrame of the line items of the predictions data
    """
    # normalize ground truth and predictions structure
    ground_truth_invoice = ground_truth["lineItems"]

    predicted_invoice = list(predictions.values())[0]
    gt_data = pd.DataFrame.from_records(ground_truth_invoice)
    pred_data = pd.DataFrame.from_records(predicted_invoice["lineItems"]).rename(
        columns={"text": "description", "transactionType": "TransactionType"}
    )
    # If one of the dataframes is empty, create a dataframe with empty strings instead
    if gt_data.shape[0] == 0:
        gt_data = pd.DataFrame(
            {
                "serviceStartDate": "",
                "serviceEndDate": "",
                "amount": "",
                "description": "",
            },
            index=[0],
        )
    if pred_data.shape[0] == 0:
        pred_data = pd.DataFrame(
            {
                "serviceStartDate": "",
                "serviceEndDate": "",
                "amount": "",
                "description": "",
                "miles": "",
            },
            index=[0],
        )
    pred_data.drop("miles", axis=1, inplace=True)
    pred_data.replace(to_replace=["NA", "N/A"], value="", inplace=True)
    return gt_data, pred_data


def get_corresponding_prediction_path(
    gt_path: str, pred_path: str, all_pred_data: Dict
):
    """
    Get the file path of the predictions that correspond to a given ground truth file.
    Args:
        gt_path (str): File path to the currently evaluated ground truth data.
        pred_path (str): path to the predictions directory or file path
        all_pred_data (Dict): The predictions parsed data.
        key: value -> prediction_file_path: prediction_parsed_data
    Returns:
        corresponding_pred_path (str): The path of the corresponding predictions to
        provided the ground truth file.
    """
    corresponding_pred_path = ""
    if os.path.isdir(pred_path):
        temp_file_name = gt_path.split("/")[-1].split(".")[0]
        file_name = f"{temp_file_name}_gpt-4o_result.json"
        corresponding_pred_path = f"{pred_path}/{file_name}"
    else:
        corresponding_pred_path = pred_path
    return corresponding_pred_path


def add_ref_ids_to_result_dfs(
    best_matches_df: pd.DataFrame(),
    unmatched_gt: pd.DataFrame(),
    unmatched_pred: pd.DataFrame(),
    curr_gt_ref_id: str,
    pred_path: str,
):
    """
    Add reference ids or predicted data path to the reported results dataframes.
    Args:
        best_matches_df: Dataframe with the line items that were matched.
        unmatched_gt: Dataframe with line items from the ground truth that were not matched.
        unmatched_pred: Dataframe with line items from the prediction that were not matched.
        curr_gt_ref_id: string of the image reference id.
        pred_path: string of the path of the current prediction
    Returns:
        Dataframes with reference ids or paths to predicted data.
    """
    best_matches_df["gt_ref"] = curr_gt_ref_id
    best_matches_df["matched_to"] = pred_path
    if unmatched_gt.shape[0] > 0:
        unmatched_gt["gt_ref"] = curr_gt_ref_id
        unmatched_gt["matched_to"] = pred_path
    else:
        unmatched_gt["gt_ref"] = []
        unmatched_gt["matched_to"] = []
    if unmatched_pred.shape[0] > 0:
        unmatched_pred["pred_path"] = pred_path
        unmatched_pred["matched_to"] = curr_gt_ref_id
    else:
        unmatched_pred["pred_path"] = []
        unmatched_pred["matched_to"] = []
    return best_matches_df, unmatched_gt, unmatched_pred


def evaluate(all_invoices_pred, all_invoices_gt, components_config):
    """
    Evaluates the quality of data extraction from images by comparing
    the extracted data to ground truth. This function calculates the
    accuracy, precision and recall to assess the correctness of the extraction.
    Args:
        predictions_file_path (str): Path of the predictions
        file (the extracted data)
        ground_truth_path (str): Path of the ground truth file
        (The true field values based on the invoice image)
        components_config: Dictionary loaded as string with configuration
    """
    # Create evaluator
    evaluator = create_extraction_evaluator(components_config)
    # we want to know which ground truth files did not have predictions
    missing_predictions_paths = []
    results_list = []
    comparison_dfs_list = []
    best_matches_dfs_list = []
    all_matches_dfs_list = []
    unmatched_gt_list = []
    unmatched_pred_list = []
    precisions_list = []
    recalls_list = []
    for raw_gt_invoice in tqdm(all_invoices_gt, desc="Invoices evaluated"):
        gt_file_name = raw_gt_invoice["reference_id"]
        log.debug(f"gt_file_name: {gt_file_name}")
        curr_gt_ref_id = gt_file_name.split(".")[0]
        pred_path_list = [
            x for x in list(all_invoices_pred.keys()) if curr_gt_ref_id in x
        ]
        if len(pred_path_list) == 0:
            pred_path = ""
        else:
            pred_path = pred_path_list[0]
        raw_pred_invoice = all_invoices_pred.get(pred_path)
        # if there is no prediction for this ground truth invoice
        if raw_pred_invoice is None:
            missing_predictions_paths.append(gt_file_name)
            continue
        gt_invoice, pred_invoice = get_gt_and_pred_data_for_evaluation(
            raw_gt_invoice, raw_pred_invoice
        )
        # In the future, we might want to return the matches and best_matches for further analysis
        comparison_df = evaluator.compare_line_item_values_per_invoice(
            ground_truth_df=gt_invoice, predictions_df=pred_invoice
        )
        comparison_df["gt_ref"] = curr_gt_ref_id
        comparison_df["matched_to"] = pred_path
        match_results_df, unmatched_gt, unmatched_pred, best_matches_df = (
            evaluator.get_match_results(comparison_df=comparison_df)
        )
        results_df = evaluator.calculate_evaluation_metrics_per_field_in_invoice(
            match_results_df=match_results_df
        )
        best_matches_df, unmatched_gt, unmatched_pred = add_ref_ids_to_result_dfs(
            best_matches_df, unmatched_gt, unmatched_pred, curr_gt_ref_id, pred_path
        )
        precision_per_invoice = evaluator.calculate_precision_per_record(
            unmatched_pred, best_matches_df
        )
        recall_per_invoice = evaluator.calculate_recall_per_record(
            unmatched_gt, best_matches_df
        )
        results_list.append(results_df)
        comparison_dfs_list.append(comparison_df)
        best_matches_dfs_list.append(best_matches_df)
        all_matches_dfs_list.append(match_results_df)
        unmatched_gt_list.append(unmatched_gt)
        unmatched_pred_list.append(unmatched_pred)
        precisions_list.append(precision_per_invoice)
        recalls_list.append(recall_per_invoice)
    all_invoices_results = pd.concat(results_list)
    all_unmatched_gt = pd.concat(unmatched_gt_list)
    all_unmatched_pred = pd.concat(unmatched_pred_list)
    overall_accuracy, final_results_df = evaluator.calculate_mean_accuracy_per_batch(
        all_invoices_results
    )
    comparison_df_all = pd.concat(comparison_dfs_list).sort_values(
        by="similarity_score"
    )
    best_matches_all = pd.concat(best_matches_dfs_list)
    all_matches_results_total = pd.concat(all_matches_dfs_list)
    gt_invoices_number = len(all_invoices_gt)
    pred_invoices_number = len(all_invoices_pred)
    overall_precision = round(np.mean(precisions_list), 3)
    overall_recall = round(np.mean(recalls_list), 3)
    return (
        final_results_df,
        overall_accuracy,
        gt_invoices_number,
        pred_invoices_number,
        all_unmatched_gt,
        all_unmatched_pred,
        comparison_df_all,
        best_matches_all,
        all_matches_results_total,
        overall_precision,
        overall_recall,
    )


def log_results(
    score_results_output_path: str,
    final_results_df: pd.DataFrame,
    all_unmatched_gt: pd.DataFrame,
    all_unmatched_pred: pd.DataFrame,
    overall_accuracy: float,
    gt_invoices_number: int,
    pred_invoices_number: int,
    comparison_df_all: pd.DataFrame,
    best_matches_all: pd.DataFrame,
    all_matches_results: pd.DataFrame,
    overall_precision: float,
    overall_recall: float,
):
    """
    Log score results to AML
    """
    score_results_output_path = "score_results.csv"
    all_unmatched_gt_path = "all_unmatched_gt.csv"
    all_unmatched_pred_path = "all_unmatched_pred.csv"
    comparison_df_path = "comparison_df.csv"
    best_matches_path = "best_matches.csv"
    all_matches_path = "all_match_results.csv"
    final_results_df.to_csv(f"{score_results_output_path}", index=False)
    mlflow.log_artifact(f"{score_results_output_path}")
    all_unmatched_gt.to_csv(f"{all_unmatched_gt_path}", index=False)
    mlflow.log_artifact(f"{all_unmatched_gt_path}")
    all_unmatched_pred.to_csv(f"{all_unmatched_pred_path}", index=False)
    mlflow.log_artifact(f"{all_unmatched_pred_path}")
    comparison_df_all.to_csv(f"{comparison_df_path}", index=False)
    mlflow.log_artifact(f"{comparison_df_path}")
    best_matches_all.to_csv(f"{best_matches_path}", index=False)
    mlflow.log_artifact(f"{best_matches_path}")
    all_matches_results.to_csv(f"{all_matches_path}", index=False)
    mlflow.log_artifact(f"{all_matches_path}")
    results_dict = {
        "overall_accuracy": overall_accuracy,
        "number_of_ground_truth_invoices": gt_invoices_number,
        "number_of_prediction_invoices": pred_invoices_number,
        "number_of_ground_truth_invoices_with_partial_prediction": all_unmatched_gt[
            "gt_ref"
        ].nunique(),
        "overall_precision": overall_precision,
        "overall_recall": overall_recall,
    }
    mlflow.log_metrics(results_dict)


def main(
    predictions_path,
    ground_truth_path,
    score_results_path,
    missing_refs_path,
    all_unmatched_gt_path,
    all_unmatched_pred_path,
    components_config,
):
    """Load ground truth and predictions data, call score function.

    Args:
        predictions_path (string): path to predictions data
        ground_truth_path (string): path to ground truth data
        score_results_path (string): output path to which to write score results
        missing_refs (string): path to which to write ground truth ref id if no
        prediction for this ground truth item was found
        all_unmatched_gt_path (string): output path to ground truth data without
        a match in the predictions
        all_unmatched_pred_path (string): output path to predictions which
        were not matched to any ground truth
        components_config: score config from experiment config
    """
    lines = [
        f"predictions_file_path: {predictions_path}",
        f"ground_truth_path: {ground_truth_path}",
        f"score_results_path: {score_results_path}",
        f"all_unmatched_gt_path: {all_unmatched_gt_path}",
        f"all_unmatched_pred_path: {all_unmatched_pred_path}",
    ]

    for line in lines:
        log.info(line)

    all_invoices_gt = load_json_file(ground_truth_path)
    all_invoices_pred = load_json_file(predictions_path)
    (
        final_results_df,
        overall_accuracy,
        gt_invoices_number,
        pred_invoices_number,
        all_unmatched_gt,
        all_unmatched_pred,
        comparison_df,
        best_matches,
        all_matches_results,
        overall_precision,
        overall_recall,
    ) = evaluate(all_invoices_pred, all_invoices_gt, components_config)

    log_results(
        score_results_path,
        final_results_df,
        all_unmatched_gt,
        all_unmatched_pred,
        overall_accuracy,
        gt_invoices_number,
        pred_invoices_number,
        comparison_df,
        best_matches,
        all_matches_results,
        overall_precision,
        overall_recall,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("evaluate")
    parser.add_argument("--predictions", type=str, help="Path of predictions")
    parser.add_argument("--ground_truth", type=str, help="Path of ground truth")
    parser.add_argument(
        "--missing_refs",
        type=str,
        help="Output path of ground truth file names without predictions",
    )
    parser.add_argument(
        "--score_report", type=str, help="Output path of evaluation results"
    )
    parser.add_argument(
        "--all_unmatched_gt_path",
        type=str,
        help="Output path of unmatched ground truth line items for all invoices",
    )
    parser.add_argument(
        "--all_unmatched_pred_path",
        type=str,
        help="Output path of unmatched predictions line items for all invoices",
    )
    parser.add_argument("--score_config", type=str, help="Config dictionary")

    args = parser.parse_args()

    log.debug("Scoring started... arguments parsed successfully.")

    predictions_file_path = args.predictions
    ground_truth_path = args.ground_truth
    score_report = args.score_report
    missing_refs = args.missing_refs
    all_unmatched_gt_path = args.all_unmatched_gt_path
    all_unmatched_pred_path = args.all_unmatched_pred_path
    score_config = args.score_config
    main(
        predictions_file_path,
        ground_truth_path,
        score_report,
        missing_refs,
        all_unmatched_gt_path,
        all_unmatched_pred_path,
        score_config,
    )
