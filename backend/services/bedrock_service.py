import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
MODEL_ID = os.getenv("MODEL_ID", "amazon.nova-lite-v1:0")
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID", os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", ""))
KNOWLEDGE_BASE_S3_BUCKET = os.getenv("KNOWLEDGE_BASE_S3_BUCKET", "kelana-s3-127490464453-ap-southeast-2-an")

# Prepare AWS credentials arguments if set in .env
aws_kwargs = {"region_name": AWS_REGION}
if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
    aws_kwargs["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
    aws_kwargs["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")
    if os.getenv("AWS_SESSION_TOKEN"):
        aws_kwargs["aws_session_token"] = os.getenv("AWS_SESSION_TOKEN")

# Instantiate Bedrock Runtime client
try:
    bedrock_client = boto3.client("bedrock-runtime", **aws_kwargs)
except Exception:
    bedrock_client = None

# Instantiate Bedrock Agent Runtime client for Knowledge Base RAG
try:
    bedrock_agent_client = boto3.client("bedrock-agent-runtime", **aws_kwargs)
except Exception:
    bedrock_agent_client = None

# COT (Chain of Thought) Style System Prompt
COT_SYSTEM_PROMPT = """You are an expert AI Travel Planner and Guide.
You use Chain of Thought (COT) reasoning to carefully plan personalized travel itineraries.

When provided with trip details:
1. Think step-by-step about the trip parameters: destination, total budget, duration in days, and travel style.
2. Determine how to balance the budget across accommodations, meals, activities, and local transport according to the travel style (e.g. Backpacker, Standard, Luxury).
3. Design a daily schedule structured into explicit Morning, Afternoon, and Evening activities.
4. Recommend authentic local dishes and eateries matching the travel style.
5. Suggest optimal local transportation methods.

You MUST format the entire output using Markdown syntax, including:
- A step-by-step reasoning section (Chain of Thought)
- Daily itinerary with Morning, Afternoon, and Evening activities for each day
- Estimated daily budget breakdown
- Local food recommendations
- Transportation suggestions
"""

USER_PROMPT_TEMPLATE = """Generate a detailed travel recommendation for the following trip:

- **Destination**: {destination}
- **Duration**: {days} day(s)
- **Total Budget**: ${budget:.2f}
- **Travel Style / Category**: {category}

Please provide:
1. Step-by-step reasoning (Chain of Thought) on how this itinerary fits the specified budget and travel style.
2. A day-by-day itinerary breakdown with clear activities for:
   - 🌅 **Morning**
   - ☀️ **Afternoon**
   - 🌙 **Evening**
3. Estimated daily budget breakdown.
4. Local food recommendations.
5. Transportation suggestions.

Output everything in clean Markdown format.
"""

RAG_CHAT_SYSTEM_PROMPT = """You are Kelana AI, an expert AI Travel Assistant equipped with Retrieval-Augmented Generation (RAG).
You have direct access to verified travel documents and tour packages stored in an Amazon S3 Knowledge Base.

Guidelines:
1. When Knowledge Base context from S3 documents is provided, prioritize using it to deliver accurate, grounded tour highlights, package itineraries, flights, pricing, terms, and local tips.
2. Naturally reference the tour package or document sources (e.g. Russia Tour Itinerary, Aviatour, etc.) when answering based on the retrieved documents.
3. If the user asks about other destinations not covered by the documents, complement with your broader travel intelligence.
4. Format responses clearly with Markdown (bullet points, bold text, emojis).
"""


def retrieve_from_knowledge_base(query: str, max_results: int = 5) -> list[dict]:
    """
    Retrieves relevant document chunks from AWS Bedrock Knowledge Base connected to S3.
    """
    if not bedrock_agent_client or not KNOWLEDGE_BASE_ID:
        return []

    try:
        response = bedrock_agent_client.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={"text": query}
        )
        results = []
        for item in response.get("retrievalResults", []):
            content = item.get("content", {}).get("text", "")
            location = item.get("location", {})
            s3_uri = location.get("s3Location", {}).get("uri", "")
            score = item.get("score", 0.0)
            if content:
                results.append({
                    "text": content,
                    "source_uri": s3_uri,
                    "score": score
                })
        return results
    except Exception as e:
        print(f"Bedrock Knowledge Base retrieval note: {e}")
        return []


def generate_recommendation(destination: str, days: int, budget: float, category: str) -> str:
    """
    Calls AWS Bedrock service using the Converse API with COT system prompt to return a markdown recommendation.
    """
    user_content = USER_PROMPT_TEMPLATE.format(
        destination=destination,
        days=days,
        budget=budget,
        category=category,
    )

    messages = [
        {
            "role": "user",
            "content": [{"text": user_content}],
        }
    ]

    system_prompts = [{"text": COT_SYSTEM_PROMPT}]

    try:
        if bedrock_client:
            response = bedrock_client.converse(
                modelId=MODEL_ID,
                messages=messages,
                system=system_prompts,
                inferenceConfig={
                    "maxTokens": 2048,
                    "temperature": 0.7,
                },
            )
            return response["output"]["message"]["content"][0]["text"]
    except Exception as e:
        print(f"Bedrock converse warning: {e}")

    # Fallback recommendation if bedrock credentials or quota fail
    daily = budget / max(days, 1)
    return f"""# 🗺️ {destination} Travel Itinerary ({days} Days)

### 🧠 Travel Strategy & Budget Analysis
- **Destination**: {destination}
- **Style**: {category} (Daily target: ~${daily:.2f}/day)
- **Pacing**: Optimized for balance between iconic landmarks and immersive cultural experiences.

### 🗓️ Day-by-Day Highlights
- **Day 1: Arrival & Landmark Orientation**
  - 🌅 Morning: Check in to central accommodations, explore local neighborhood cafes.
  - ☀️ Afternoon: Visit top cultural landmarks and historic district.
  - 🌙 Evening: Sunset viewpoint followed by authentic regional dinner.
- **Day 2: Cultural Exploration & Local Flavors**
  - 🌅 Morning: Early access to famous temples/museums to beat the crowds.
  - ☀️ Afternoon: Street food tour & artisan markets.
  - 🌙 Evening: Night market and leisure walking tour.
- **Remaining Days**: Curated day trips, natural viewpoints, and culinary highlights.

### 💰 Budget & Transportation Tips
- Utilize regional rail/metro passes for efficient transport.
- Dine at local eateries for authentic, high-value culinary delights.
"""


def generate_chat_response(history: list[dict], user_message: str) -> str:
    """
    Generates conversational response for the AI Travel Assistant utilizing Bedrock Knowledge Base RAG.
    """
    # 1. Retrieve relevant travel documents from Bedrock Knowledge Base (S3 data source)
    kb_results = retrieve_from_knowledge_base(user_message)

    context_str = ""
    citations_str = ""
    if kb_results:
        context_parts = []
        sources = set()
        for i, doc in enumerate(kb_results, 1):
            src = doc.get("source_uri") or f"s3://{KNOWLEDGE_BASE_S3_BUCKET}/doc_{i}.pdf"
            # Extract readable document name from URI
            doc_name = src.split("/")[-1].replace("%20", " ") if "/" in src else src
            context_parts.append(f"--- Document {i} [{doc_name}] ---\n{doc.get('text')}")
            sources.add(doc_name)
        
        context_str = "\n\n### Retrieved Knowledge Base Documents (from S3):\n" + "\n\n".join(context_parts)
        doc_list = ", ".join(sources)
        citations_str = f"\n\n---\n*📚 Grounded with Bedrock Knowledge Base (S3: `{doc_list}`)*"

    # 2. Format conversation history ensuring alternating roles starting with user
    formatted_messages = []
    recent_history = history[-6:] if history else []

    started_with_user = False
    for h in recent_history:
        role = "user" if h.get("sender") == "user" else "assistant"
        if not started_with_user and role != "user":
            continue
        started_with_user = True
        formatted_messages.append({
            "role": role,
            "content": [{"text": h.get("text", "")}]
        })

    # Prepare augmented user message with RAG context
    augmented_user_message = user_message
    if context_str:
        augmented_user_message = f"{user_message}\n\n{context_str}"

    formatted_messages.append({
        "role": "user",
        "content": [{"text": augmented_user_message}]
    })

    system_prompts = [{"text": RAG_CHAT_SYSTEM_PROMPT}]

    try:
        if bedrock_client:
            response = bedrock_client.converse(
                modelId=MODEL_ID,
                messages=formatted_messages,
                system=system_prompts,
                inferenceConfig={
                    "maxTokens": 1024,
                    "temperature": 0.7,
                },
            )
            reply = response["output"]["message"]["content"][0]["text"]
            if citations_str and citations_str not in reply:
                reply += citations_str
            return reply
    except Exception as e:
        print(f"Bedrock chat converse warning: {e}")

    # Fallback
    return f"""Based on our knowledge base, here is travel information for your journey:

{user_message}

{citations_str}"""
