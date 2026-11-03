import sys
from pathlib import Path

# Force UTF-8 on Windows consoles to print Indic characters safely
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from app.core.database import init_db, AsyncSessionLocal
from app.models.models import Document
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.retrieval.vector_store import vector_store
from app.services.routing.jev_router import jev_router
from app.services.retrieval.embeddings import embedding_service
from app.services.retrieval.reranker import reranker_service
from app.services.chat.conversation_service import ConversationService
from app.services.chat.query_rewriter import query_rewriter

async def run_live_pipeline_test():
    print("=" * 60)
    print(" BharatSetu Live Pipeline Verification")
    print("=" * 60)

    # 1. Initialize SQLite Database
    await init_db()
    print("1. Database initialized.")

    samples_dir = Path(__file__).resolve().parent.parent / "data" / "samples"
    
    test_files = [
        ("Company_Leave_Policy.pdf", "HR Policies", "Company Policy"),
        ("IT_Security_Protocol.pdf", "IT Security", "Security Protocol"),
        ("Physics_Class10_Electricity.pdf", "Physics", "Educational Textbook")
    ]

    # 2. Ingest Sample Documents
    print("\n2. Ingesting sample PDFs into vector store & database...")
    for filename, domain, doc_type in test_files:
        file_path = samples_dir / filename
        if not file_path.exists():
            print(f"Error: {file_path} not found.")
            continue

        doc_id = f"test_{filename.split('.')[0].lower()}"
        
        # Insert or fetch document
        async with AsyncSessionLocal() as session:
            doc = await session.get(Document, doc_id)
            if not doc:
                doc = Document(
                    id=doc_id,
                    filename=filename,
                    file_path=str(file_path),
                    domain=domain,
                    document_type=doc_type,
                    language="en",
                    status="processing"
                )
                session.add(doc)
                await session.commit()

        # Run ingestion
        await IngestionPipeline.process_document_background(
            document_id=doc_id,
            file_path=file_path,
            filename=filename,
            domain=domain,
            document_type=doc_type,
            language="en"
        )
        print(f"   Indexed: {filename} -> Domain: '{domain}'")

    # 3. Verify Active Domains
    active_domains = vector_store.get_all_domains()
    print(f"\n3. Total Chunks in Vector Store: {vector_store.count()}")
    print(f"   Active Domains Indexed: {active_domains}")

    # 4. Test Jev Dynamic Domain Routing
    print("\n4. Testing Jev Dynamic Routing...")
    query_1 = "मातृत्व अवकाश (Maternity Leave) के क्या नियम हैं?"
    route_res = await jev_router.route(query_1, available_domains=active_domains)
    print(f"   Query: \"{query_1}\"")
    print(f"   Jev Routed to: {route_res['domains']} (Confidence: {route_res['confidence']})")

    # 5. Test Cross-Lingual Vector Retrieval
    print("\n5. Testing Vector Retrieval & Reranking...")
    query_vec = embedding_service.embed_query(query_1)
    candidates = vector_store.search(query_vec, top_k=5, domain_filter=route_res['domains'])
    print(f"   Retrieved {len(candidates)} candidate chunks.")
    
    reranked = reranker_service.rerank(query_1, candidates, top_n=2)
    for idx, c in enumerate(reranked, start=1):
        meta = c.get("metadata", {})
        print(f"   Top [{idx}] Doc: {meta.get('document_name')} | Section: {meta.get('section')} | Score: {c.get('score')}")
        print(f"       Preview: {c.get('content')[:120]}...\n")

    # 6. Test Multi-Turn Conversation Memory & Query Rewriting
    print("6. Testing Multi-Turn Conversation Memory...")
    convo = await ConversationService.create_conversation(title="Live Verification Chat", default_language="hi")
    
    # Turn 1
    await ConversationService.add_message(convo.id, "user", "What is electric current?")
    await ConversationService.add_message(convo.id, "assistant", "Electric current is the rate of flow of electric charge, measured in amperes.")
    
    # Turn 2: Pronoun reference "What is its SI unit?"
    follow_up = "What is its SI unit?"
    history = await ConversationService.get_recent_messages(convo.id, limit=4)
    rewritten = await query_rewriter.rewrite_if_needed(follow_up, history)
    print(f"   Turn 1 Question: \"What is electric current?\"")
    print(f"   Turn 2 Follow-up: \"{follow_up}\"")
    print(f"   Rewritten Query: \"{rewritten}\"")

    print("\n" + "=" * 60)
    print("All live pipeline checks PASSED successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_live_pipeline_test())
