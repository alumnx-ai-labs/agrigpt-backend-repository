"""
Simplified RAGAS Evaluation - Only 3 Core Metrics
Faithfulness, Answer Relevance, Context Relevance
"""

import asyncio
import json
import os
import sys
from typing import List, Dict
from dotenv import load_dotenv
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path is set
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

# Test cases matching Mosambi Schemes PDF content
TEST_CASES = [
    {
        "query": "What is PM-KISAN scheme for mosambi farmers and what benefits does it provide?",
        "expected_keywords": ["PM-KISAN", "6000", "annual", "income", "mosambi"]
    },
    {
        "query": "What is PMFBY crop insurance for mosambi and what is the premium?",
        "expected_keywords": ["PMFBY", "insurance", "crop", "premium", "5%", "mosambi"]
    },
    {
        "query": "What is MIDH scheme for mosambi plantation and what subsidy is available?",
        "expected_keywords": ["MIDH", "mosambi", "subsidy", "plantation", "hectare"]
    }
]

# Global services
llm = None
embeddings = None
rag_service = None


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


async def extract_statements(answer: str) -> List[str]:
    """Extract statements from answer for Faithfulness"""
    prompt = f"""Break down this answer into individual statements (one per line):

Answer: {answer}

Statements:"""
    
    response = await llm.ainvoke(prompt)
    statements = [s.strip() for s in response.content.split('\n') if s.strip()]
    # Remove numbering
    statements = [s.split('.', 1)[-1].strip() if s[0].isdigit() else s for s in statements]
    return [s for s in statements if len(s) > 15]


async def verify_statement(statement: str, context: str) -> bool:
    """Verify statement against context"""
    prompt = f"""Context: {context}

Statement: {statement}

Can this statement be verified from the context? Answer only Yes or No.

Answer:"""
    
    response = await llm.ainvoke(prompt)
    return 'yes' in response.content.lower()


async def calculate_faithfulness(answer: str, context: List[Dict]) -> float:
    """
    Faithfulness = |Verified| / |Total Statements|
    """
    if not answer or not context:
        return 0.0
    
    context_str = "\n\n".join([doc["page_content"] for doc in context])
    
    # Extract statements
    statements = await extract_statements(answer)
    if not statements:
        return 1.0
    
    # Verify each
    verified_count = 0
    for stmt in statements:
        if await verify_statement(stmt, context_str):
            verified_count += 1
    
    score = verified_count / len(statements)
    print(f"    Faithfulness: {verified_count}/{len(statements)} verified = {score:.3f}")
    return score


async def generate_proxy_questions(answer: str) -> List[str]:
    """Generate questions from answer"""
    prompt = f"""Generate 3 questions that this answer could respond to:

Answer: {answer}

Questions (one per line):"""
    
    response = await llm.ainvoke(prompt)
    questions = [q.strip() for q in response.content.split('\n') if '?' in q]
    questions = [q.split('.', 1)[-1].strip() if q[0].isdigit() else q for q in questions]
    return questions[:3]


async def calculate_answer_relevance(query: str, answer: str) -> float:
    """
    Answer Relevance = Average similarity between query and proxy questions
    """
    if not answer:
        return 0.0
    
    # Generate proxy questions
    proxy_qs = await generate_proxy_questions(answer)
    if not proxy_qs:
        return 0.0
    
    # Get embeddings
    query_emb = await embeddings.aembed_query(query)
    
    similarities = []
    for pq in proxy_qs:
        pq_emb = await embeddings.aembed_query(pq)
        sim = cosine_similarity(query_emb, pq_emb)
        similarities.append(sim)
    
    score = sum(similarities) / len(similarities)
    print(f"    Answer Relevance: avg similarity = {score:.3f}")
    return score


async def extract_relevant_sentences(query: str, context: List[Dict]) -> int:
    """Extract relevant sentences count"""
    context_str = "\n\n".join([doc["page_content"] for doc in context])
    
    prompt = f"""Extract sentences from context relevant to the question.
Return ONLY the relevant sentences (or say "None" if nothing relevant).

Question: {query}

Context: {context_str}

Relevant sentences:"""
    
    response = await llm.ainvoke(prompt)
    
    if 'none' in response.content.lower():
        return 0
    
    sentences = [s.strip() for s in response.content.split('.') if s.strip() and len(s.strip()) > 20]
    return len(sentences)


async def calculate_context_relevance(query: str, context: List[Dict]) -> float:
    """
    Context Relevance = |Relevant Sentences| / |Total Sentences|
    """
    if not context:
        return 0.0
    
    # Count total sentences
    total_sents = 0
    for doc in context:
        sents = [s for s in doc["page_content"].split('.') if s.strip()]
        total_sents += len(sents)
    
    if total_sents == 0:
        return 0.0
    
    # Extract relevant
    relevant_count = await extract_relevant_sentences(query, context)
    
    score = relevant_count / total_sents
    print(f"    Context Relevance: {relevant_count}/{total_sents} relevant = {score:.3f}")
    return score


async def evaluate_single_query(query: str, keywords: List[str]) -> Dict:
    """Evaluate one query with all 3 metrics"""
    print(f"\n  Query: {query}")
    
    try:
        # Get RAG response
        answer, sources = await rag_service.query(query, "schemes", chat_history=[])
        retrieved_docs = rag_service.retrieve_documents(query, "schemes")
        
        print(f"  Answer: {answer[:80]}...")
        print(f"  Sources: {len(sources)}")
        
        # Calculate 3 metrics
        faithfulness = await calculate_faithfulness(answer, retrieved_docs)
        answer_rel = await calculate_answer_relevance(query, answer)
        context_rel = await calculate_context_relevance(query, retrieved_docs)
        
        # Check if keywords present (sanity check)
        answer_lower = answer.lower()
        keywords_found = sum(1 for kw in keywords if kw.lower() in answer_lower)
        
        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "metrics": {
                "faithfulness": round(faithfulness, 3),
                "answer_relevance": round(answer_rel, 3),
                "context_relevance": round(context_rel, 3)
            },
            "keywords_found": f"{keywords_found}/{len(keywords)}",
            "passed": faithfulness >= 0.6 and answer_rel >= 0.6 and context_rel >= 0.6
        }
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return {
            "query": query,
            "error": str(e),
            "passed": False
        }


async def run_evaluation():
    """Main evaluation"""
    global llm, embeddings, rag_service
    
    print("=" * 80)
    print("RAGAS EVALUATION - 3 Core Metrics Only")
    print("Faithfulness | Answer Relevance | Context Relevance")
    print("=" * 80)
    
    # Initialize
    print("\n1. Initializing services...")
    
    try:
        from services.rag_service import RAGService
        rag_service = RAGService()
        await rag_service.initialize()
        print("   ✅ RAG service initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize RAG service: {e}")
        return
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0
        )
        print("   ✅ LLM initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize LLM: {e}")
        return
    
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        print("   ✅ Embeddings initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize embeddings: {e}")
        return
    
    # Run tests
    print(f"\n2. Running {len(TEST_CASES)} test cases...")
    print("=" * 80)
    
    results = []
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\nTest {i}/{len(TEST_CASES)}")
        print("-" * 80)
        result = await evaluate_single_query(test["query"], test["expected_keywords"])
        results.append(result)
        print(f"  Status: {'✅ PASSED' if result.get('passed') else '❌ FAILED'}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r.get("passed", False))
    total = len(results)
    
    # Average metrics
    valid_results = [r for r in results if "metrics" in r]
    if valid_results:
        avg_faith = np.mean([r["metrics"]["faithfulness"] for r in valid_results])
        avg_ans_rel = np.mean([r["metrics"]["answer_relevance"] for r in valid_results])
        avg_ctx_rel = np.mean([r["metrics"]["context_relevance"] for r in valid_results])
        
        print(f"\nAverage RAGAS Metrics:")
        print(f"  Faithfulness:      {avg_faith:.3f} {'✅' if avg_faith >= 0.6 else '❌'}")
        print(f"  Answer Relevance:  {avg_ans_rel:.3f} {'✅' if avg_ans_rel >= 0.6 else '❌'}")
        print(f"  Context Relevance: {avg_ctx_rel:.3f} {'✅' if avg_ctx_rel >= 0.6 else '❌'}")
    
    print(f"\nTests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"Status: {'✅ PRODUCTION READY' if passed/total >= 0.67 else '⚠️ NEEDS IMPROVEMENT'}")
    
    # Save
    output = {
        "summary": {
            "total_tests": total,
            "passed": passed,
            "pass_rate": passed / total,
            "avg_metrics": {
                "faithfulness": float(avg_faith),
                "answer_relevance": float(avg_ans_rel),
                "context_relevance": float(avg_ctx_rel)
            } if valid_results else {}
        },
        "results": results
    }
    
    with open('ragas_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📊 Detailed results saved to: ragas_results.json")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_evaluation())