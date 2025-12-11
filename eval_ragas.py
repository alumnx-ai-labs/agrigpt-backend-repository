"""
RAG Evaluation using RAGAS Framework Metrics
Metrics: Faithfulness, Answer Relevance, Context Relevance
"""

import asyncio
from services.rag_service import RAGService
from typing import List, Dict
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# Initialize services
rag_service = RAGService()
llm = None
embeddings = None


# Test cases with ground truth where available
TEST_CASES = [
    {
        "query": "What is the PM-KISAN scheme and what benefits does it provide?",
        "ground_truth": "PM-KISAN provides income support of Rs. 6000 per year to farmers in three equal installments",
        "category": "factual"
    },
    {
        "query": "What are the eligibility criteria for Pradhan Mantri Fasal Bima Yojana?",
        "ground_truth": "Farmers who are cultivating crops and want insurance coverage against natural calamities",
        "category": "factual"
    },
    {
        "query": "What is Kisan Credit Card scheme?",
        "ground_truth": "KCC provides credit to farmers for agricultural needs and working capital",
        "category": "factual"
    },
    {
        "query": "What is the subsidy for electric tractors?",
        "ground_truth": None,  # Not in documents - should refuse
        "category": "hallucination_check"
    },
    {
        "query": "Which state gives highest drip irrigation subsidy?",
        "ground_truth": None,  # Not in documents - should refuse
        "category": "hallucination_check"
    },
    {
        "query": "What is deadline for PM-KISAN 2025?",
        "ground_truth": None,  # Not in documents - should refuse
        "category": "hallucination_check"
    },
    {
        "query": "What is the capital of India?",
        "ground_truth": None,  # Out of scope
        "category": "scope_check"
    },
    {
        "query": "How to grow tomatoes?",
        "ground_truth": None,  # Out of scope
        "category": "scope_check"
    },
    {
        "query": "Tell me about Python programming",
        "ground_truth": None,  # Out of scope
        "category": "scope_check"
    }
]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


async def extract_statements(answer: str) -> List[str]:
    """Extract individual statements from answer (Step 1 of Faithfulness)"""
    prompt = f"""Given the answer below, break it down into individual statements or assertions. 
Each statement should represent a single claim or piece of information.
Return ONLY the statements, one per line, numbered.

Answer: {answer}

Statements:"""
    
    response = await llm.ainvoke(prompt)
    statements = [s.strip() for s in response.content.split('\n') if s.strip() and not s.strip().startswith('Statement')]
    # Clean up numbering
    statements = [s.split('.', 1)[-1].strip() if s[0].isdigit() else s for s in statements]
    return [s for s in statements if len(s) > 10]  # Filter very short statements


async def verify_statement(statement: str, context: str) -> bool:
    """Verify if statement is supported by context (Step 2 of Faithfulness)"""
    prompt = f"""Context: {context}

Statement: {statement}

Question: Can this statement be directly inferred or verified from the context above? 
Answer ONLY 'Yes' or 'No'.

Answer:"""
    
    response = await llm.ainvoke(prompt)
    return 'yes' in response.content.lower()


async def calculate_faithfulness(answer: str, context: List[Dict]) -> Dict:
    """
    Faithfulness: F = |V| / |S|
    Measures if answer is faithful to retrieved context
    """
    if not answer or not context:
        return {"score": 0.0, "details": "Empty answer or context"}
    
    # Combine context
    context_str = "\n\n".join([doc["page_content"] for doc in context])
    
    # Step 1: Extract statements
    statements = await extract_statements(answer)
    if not statements:
        return {"score": 1.0, "details": "No statements to verify"}
    
    # Step 2: Verify each statement
    verified = []
    for stmt in statements:
        is_verified = await verify_statement(stmt, context_str)
        verified.append(is_verified)
    
    # Step 3: Calculate score
    score = sum(verified) / len(verified) if verified else 0.0
    
    return {
        "score": score,
        "total_statements": len(statements),
        "verified_statements": sum(verified),
        "statements": statements,
        "verification": verified
    }


async def generate_proxy_questions(answer: str, n: int = 3) -> List[str]:
    """Generate proxy questions that this answer could address (Step 1 of Answer Relevance)"""
    prompt = f"""Given the answer below, generate {n} different questions that this answer could appropriately respond to.
Return ONLY the questions, one per line, numbered.

Answer: {answer}

Questions:"""
    
    response = await llm.ainvoke(prompt)
    questions = [q.strip() for q in response.content.split('\n') if q.strip() and '?' in q]
    # Clean up numbering
    questions = [q.split('.', 1)[-1].strip() if q[0].isdigit() else q for q in questions]
    return questions[:n]


async def calculate_answer_relevance(query: str, answer: str) -> Dict:
    """
    Answer Relevance: AR = (1/n) * Σ sim(q, qi)
    Measures if answer addresses the query
    """
    if not answer:
        return {"score": 0.0, "details": "Empty answer"}
    
    # Step 1: Generate proxy questions
    proxy_questions = await generate_proxy_questions(answer, n=3)
    if not proxy_questions:
        return {"score": 0.0, "details": "Could not generate proxy questions"}
    
    # Step 2: Calculate embeddings and similarities
    query_embedding = await embeddings.aembed_query(query)
    
    similarities = []
    for pq in proxy_questions:
        pq_embedding = await embeddings.aembed_query(pq)
        sim = cosine_similarity(query_embedding, pq_embedding)
        similarities.append(sim)
    
    # Average similarity
    score = sum(similarities) / len(similarities) if similarities else 0.0
    
    return {
        "score": score,
        "proxy_questions": proxy_questions,
        "similarities": similarities
    }


async def extract_relevant_sentences(query: str, context: List[Dict]) -> List[str]:
    """Extract sentences from context relevant to query (Step 1 of Context Relevance)"""
    context_str = "\n\n".join([doc["page_content"] for doc in context])
    
    prompt = f"""Extract relevant sentences from the context that can help answer the question.
If no relevant sentences found, return 'Insufficient Information'.
Do not modify the sentences from context.

Question: {query}

Context: {context_str}

Relevant sentences:"""
    
    response = await llm.ainvoke(prompt)
    
    if 'insufficient information' in response.content.lower():
        return []
    
    sentences = [s.strip() for s in response.content.split('\n') if s.strip() and len(s.strip()) > 20]
    return sentences


async def calculate_context_relevance(query: str, context: List[Dict]) -> Dict:
    """
    Context Relevance: CR = |Sext| / |S|
    Measures how much of retrieved context is relevant
    """
    if not context:
        return {"score": 0.0, "details": "No context retrieved"}
    
    # Count total sentences in context
    total_sentences = []
    for doc in context:
        sents = [s.strip() for s in doc["page_content"].split('.') if s.strip()]
        total_sentences.extend(sents)
    
    if not total_sentences:
        return {"score": 0.0, "details": "No sentences in context"}
    
    # Extract relevant sentences
    relevant_sentences = await extract_relevant_sentences(query, context)
    
    # Calculate score
    score = len(relevant_sentences) / len(total_sentences) if total_sentences else 0.0
    
    return {
        "score": score,
        "total_sentences": len(total_sentences),
        "relevant_sentences": len(relevant_sentences),
        "extracted": relevant_sentences[:3]  # Show first 3 for brevity
    }


async def evaluate_test_case(test: Dict) -> Dict:
    """Evaluate a single test case with RAGAS metrics"""
    query = test["query"]
    category = test["category"]
    
    print(f"  Query: {query}")
    
    # Get RAG response
    try:
        answer, sources = await rag_service.query(query, "schemes", chat_history=[])
        
        # Get retrieved context (we need to modify RAG service to return this)
        retrieved_docs = rag_service.retrieve_documents(query, "schemes")
        
    except Exception as e:
        return {
            "query": query,
            "category": category,
            "error": str(e),
            "passed": False
        }
    
    print(f"  Answer: {answer[:100]}...")
    
    # Calculate metrics based on category
    result = {
        "query": query,
        "answer": answer,
        "sources": sources,
        "category": category,
        "metrics": {}
    }
    
    if category == "factual":
        # Calculate all 3 metrics for factual questions
        print("    Calculating Faithfulness...")
        faithfulness = await calculate_faithfulness(answer, retrieved_docs)
        
        print("    Calculating Answer Relevance...")
        answer_relevance = await calculate_answer_relevance(query, answer)
        
        print("    Calculating Context Relevance...")
        context_relevance = await calculate_context_relevance(query, retrieved_docs)
        
        result["metrics"] = {
            "faithfulness": faithfulness,
            "answer_relevance": answer_relevance,
            "context_relevance": context_relevance
        }
        
        # Pass if all metrics > 0.6
        result["passed"] = (
            faithfulness["score"] >= 0.6 and
            answer_relevance["score"] >= 0.6 and
            context_relevance["score"] >= 0.6
        )
        
    elif category == "hallucination_check":
        # For hallucination: Faithfulness should be high (>0.7) OR answer should refuse
        print("    Calculating Faithfulness (hallucination check)...")
        faithfulness = await calculate_faithfulness(answer, retrieved_docs)
        
        # Check for refusal
        refusal_phrases = ["don't have", "insufficient", "cannot find", "not in my knowledge"]
        refused = any(phrase in answer.lower() for phrase in refusal_phrases)
        
        result["metrics"] = {
            "faithfulness": faithfulness,
            "refused": refused
        }
        
        # Pass if refused OR has high faithfulness (not making up info)
        result["passed"] = refused or faithfulness["score"] >= 0.7
        
    else:  # scope_check
        # For scope: Should reject (short answer with rejection)
        rejection_keywords = ["only answer", "government", "schemes"]
        rejected = any(kw in answer.lower() for kw in rejection_keywords)
        is_brief = len(answer) < 150
        
        result["metrics"] = {
            "rejected": rejected,
            "brief": is_brief,
            "length": len(answer)
        }
        
        result["passed"] = rejected and is_brief
    
    print(f"  Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
    return result


async def run_ragas_evaluation():
    """Run RAGAS-based evaluation"""
    global llm, embeddings
    
    print("=" * 80)
    print("RAGAS FRAMEWORK EVALUATION - Government Schemes RAG")
    print("=" * 80)
    print()
    
    # Initialize services
    print("Initializing services...")
    await rag_service.initialize()
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0
    )
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    print("✅ Services initialized\n")
    
    # Run evaluations
    results = []
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(TEST_CASES)} [{test['category'].upper()}]")
        print('='*80)
        
        result = await evaluate_test_case(test)
        results.append(result)
        print()
    
    # Summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    
    # By category
    categories = {}
    for result in results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0}
        categories[cat]["total"] += 1
        if result.get("passed", False):
            categories[cat]["passed"] += 1
    
    for cat, stats in categories.items():
        pass_rate = stats["passed"] / stats["total"] * 100
        print(f"\n{cat.upper().replace('_', ' ')}:")
        print(f"  Passed: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
    
    # Overall
    total_passed = sum(r.get("passed", False) for r in results)
    total_tests = len(results)
    overall_rate = total_passed / total_tests * 100
    
    print(f"\nOVERALL:")
    print(f"  Total: {total_passed}/{total_tests} ({overall_rate:.1f}%)")
    print(f"  Status: {'✅ SYSTEM READY' if overall_rate >= 70 else '⚠️ NEEDS IMPROVEMENT'}")
    
    # Calculate average RAGAS metrics for factual questions
    factual_results = [r for r in results if r["category"] == "factual"]
    if factual_results:
        avg_faithfulness = np.mean([r["metrics"]["faithfulness"]["score"] for r in factual_results])
        avg_answer_rel = np.mean([r["metrics"]["answer_relevance"]["score"] for r in factual_results])
        avg_context_rel = np.mean([r["metrics"]["context_relevance"]["score"] for r in factual_results])
        
        print(f"\nRAGAS METRICS (Factual Questions):")
        print(f"  Faithfulness:      {avg_faithfulness:.3f}")
        print(f"  Answer Relevance:  {avg_answer_rel:.3f}")
        print(f"  Context Relevance: {avg_context_rel:.3f}")
    
    # Save results
    output = {
        "summary": categories,
        "overall": {
            "total": total_tests,
            "passed": total_passed,
            "pass_rate": overall_rate / 100
        },
        "results": results
    }
    
    with open('/home/claude/ragas_evaluation_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📊 Results saved to: ragas_evaluation_results.json")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_ragas_evaluation())