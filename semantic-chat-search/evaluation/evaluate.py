import os
import json
import sys

# Ensure root project directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.search_engine import SearchEngine

def run_evaluation(
    eval_dataset_path: str = "dataset/evaluation.json",
    results_output_path: str = "evaluation/results.json"
):
    if not os.path.exists(eval_dataset_path):
        alt_path = os.path.join("..", eval_dataset_path)
        if os.path.exists(alt_path):
            eval_dataset_path = alt_path
        else:
            raise FileNotFoundError(f"Evaluation dataset not found at {eval_dataset_path}")

    print("Loading evaluation dataset...")
    with open(eval_dataset_path, "r", encoding="utf-8") as f:
        queries = json.load(f)

    print("Initializing Search Engine...")
    search_engine = SearchEngine(
        data_path=os.path.join("dataset", "chat.json"),
        vector_store_dir=os.path.join("vector_store")
    )

    top1_hits = 0
    top3_hits = 0
    top5_hits = 0
    reciprocal_ranks = []

    evaluated_query_details = []

    print(f"\nRunning evaluation on {len(queries)} test queries...\n" + "=" * 60)

    for idx, q_item in enumerate(queries, 1):
        query_text = q_item["query"]
        target_id = q_item["correct_message_id"]
        q_type = q_item.get("type", "semantic")

        res = search_engine.search(query_text, top_k=5)
        retrieved_results = res["results"]
        retrieved_ids = [r["message_id"] for r in retrieved_results]

        top1 = (retrieved_ids[0] == target_id) if len(retrieved_ids) > 0 else False
        top3 = target_id in retrieved_ids[:3]
        top5 = target_id in retrieved_ids[:5]

        rank = None
        reciprocal_rank = 0.0

        if target_id in retrieved_ids:
            rank = retrieved_ids.index(target_id) + 1
            reciprocal_rank = 1.0 / rank

        if top1:
            top1_hits += 1
        if top3:
            top3_hits += 1
        if top5:
            top5_hits += 1

        reciprocal_ranks.append(reciprocal_rank)

        query_eval_detail = {
            "query": query_text,
            "correct_message_id": target_id,
            "type": q_type,
            "retrieved_top1_id": retrieved_ids[0] if retrieved_ids else None,
            "rank": rank,
            "found_in_top1": top1,
            "found_in_top3": top3,
            "found_in_top5": top5,
            "reciprocal_rank": round(reciprocal_rank, 4)
        }
        evaluated_query_details.append(query_eval_detail)

        status_str = f"Rank {rank}" if rank else "FAIL (Not in Top 5)"
        print(f"[{idx:02d}/40] [{q_type.upper():10s}] Query: \"{query_text}\" -> {status_str}")

    total_queries = len(queries)
    top1_acc = round(top1_hits / total_queries, 4)
    top3_acc = round(top3_hits / total_queries, 4)
    top5_acc = round(top5_hits / total_queries, 4)
    mrr = round(sum(reciprocal_ranks) / total_queries, 4)

    results_summary = {
        "total_queries": total_queries,
        "top1_accuracy": top1_acc,
        "top3_accuracy": top3_acc,
        "top5_accuracy": top5_acc,
        "mrr": mrr,
        "queries": evaluated_query_details
    }

    os.makedirs(os.path.dirname(results_output_path), exist_ok=True)
    with open(results_output_path, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("EVALUATION RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Queries : {total_queries}")
    print(f"Top-1 Accuracy: {top1_acc * 100:.2f}%  ({top1_hits}/{total_queries})")
    print(f"Top-3 Accuracy: {top3_acc * 100:.2f}%  ({top3_hits}/{total_queries})")
    print(f"Top-5 Accuracy: {top5_acc * 100:.2f}%  ({top5_hits}/{total_queries})")
    print(f"MRR           : {mrr:.4f}")
    print(f"Saved evaluation results to {results_output_path}")

    return results_summary

if __name__ == "__main__":
    run_evaluation()
