import sys
import json
import time
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.routing.jev_router import JevRouter
from app.services.retrieval.embeddings import embedding_service
from app.services.retrieval.vector_store import vector_store
from app.services.retrieval.reranker import reranker_service

async def run_ab_evaluation():
    benchmark_file = Path(__file__).parent / "benchmark_dataset.json"
    with open(benchmark_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print("=" * 60)
    print(" BharatSetu A/B Evaluation: System A (Direct) vs System B (Jev)")
    print("=" * 60)

    total_time_a = 0.0
    total_time_b = 0.0
    correct_domains_jev = 0

    available_domains = ["HR Policies", "IT Security", "Compliance & Ethics", "Physics", "Chemistry"]

    for idx, case in enumerate(cases, start=1):
        q = case["question"]
        expected_dom = case["expected_domain"]
        print(f"\n[Case {idx}] ({case['language']}) \"{q[:40]}...\"")
        print(f"Expected Domain: {expected_dom}")

        # --- System A: Direct Vector Search (No Jev) ---
        t0 = time.time()
        q_vec_a = embedding_service.embed_query(q)
        cands_a = vector_store.search(q_vec_a, top_k=25, domain_filter=None)
        reranked_a = reranker_service.rerank(q, cands_a, top_n=5)
        lat_a = (time.time() - t0) * 1000
        total_time_a += lat_a

        # --- System B: Jev-Routed Vector Search ---
        t1 = time.time()
        jev_res = await JevRouter.route(q, available_domains=available_domains)
        routed = jev_res.get("domains", [])
        q_vec_b = embedding_service.embed_query(q)
        cands_b = vector_store.search(q_vec_b, top_k=25, domain_filter=routed if routed else None)
        reranked_b = reranker_service.rerank(q, cands_b, top_n=5)
        lat_b = (time.time() - t1) * 1000
        total_time_b += lat_b

        is_correct = expected_dom in routed
        if is_correct:
            correct_domains_jev += 1

        print(f"  System A (Unfiltered) Latency: {lat_a:.1f}ms | Candidates Scanned: {len(cands_a)}")
        print(f"  System B (Jev Routed) Latency: {lat_b:.1f}ms | Jev Routed: {routed} (Match: {is_correct})")

    avg_a = total_time_a / len(cases)
    avg_b = total_time_b / len(cases)
    accuracy = (correct_domains_jev / len(cases)) * 100

    print("\n" + "=" * 60)
    print(" SUMMARY RESULTS")
    print("=" * 60)
    print(f"Total Test Cases:            {len(cases)}")
    print(f"Jev Domain Routing Accuracy: {accuracy:.1f}%")
    print(f"Average Latency System A:    {avg_a:.1f} ms")
    print(f"Average Latency System B:    {avg_b:.1f} ms")
    print("=" * 60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_ab_evaluation())
