import re
import time
from typing import Generator

import boto3

try:
    from config import settings
except ImportError:
    from backend.config import settings

AWS_REGION = settings.aws_region
MODEL_ID = settings.model_id
KNOWLEDGE_BASE_ID = settings.knowledge_base_id
KNOWLEDGE_BASE_S3_BUCKET = settings.knowledge_base_s3_bucket

# Prepare AWS credentials arguments if set in settings/.env
aws_kwargs = {"region_name": AWS_REGION}
if settings.aws_access_key_id and settings.aws_secret_access_key:
    aws_kwargs["aws_access_key_id"] = settings.aws_access_key_id
    aws_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    if settings.aws_session_token:
        aws_kwargs["aws_session_token"] = settings.aws_session_token

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

CASUAL_GREETINGS = {
    "hi", "say hi", "hello", "hey", "hello there", "good morning",
    "good afternoon", "good evening", "how are you", "who are you",
    "what can you do", "help", "thanks", "thank you", "bye", "test",
}


def is_casual_query(text: str) -> bool:
    cleaned = re.sub(r"[^\w\s]", "", text.strip().lower())
    return cleaned in CASUAL_GREETINGS or (len(cleaned.split()) <= 1 and cleaned in {"hi", "hello", "hey", "hola"})


RAG_CHAT_SYSTEM_PROMPT = """You are Kelana AI, an intelligent, helpful, and friendly AI Travel Assistant.
You assist travelers with destination ideas, custom itineraries, sightseeing recommendations, travel tips, and budgeting.

Guidelines:
1. If the user greets you or makes casual conversation (e.g. "hi", "say hi", "hello"), reply warmly, naturally, and concisely without unprompted itinerary or package dumps.
2. Directly answer what the user asked.
3. Only incorporate Knowledge Base tour details if they directly match the specific destination or question the user asked about. Never mention unrelated destinations or tour packages.
4. Format your responses with clean Markdown (bullet points, clear sections, bold text).
"""


def retrieve_from_knowledge_base(query: str, max_results: int = 5) -> list[dict]:
    """
    Retrieves relevant document chunks from AWS Bedrock Knowledge Base connected to S3.
    Filters out casual greetings and low-confidence matches.
    """
    if not bedrock_agent_client or not KNOWLEDGE_BASE_ID:
        return []

    if is_casual_query(query):
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
            # High confidence threshold so greetings/unrelated queries don't trigger tour package dumps
            if content and score >= 0.70:
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
    if kb_results:
        context_parts = []
        for i, doc in enumerate(kb_results, 1):
            src = doc.get("source_uri") or f"s3://{KNOWLEDGE_BASE_S3_BUCKET}/doc_{i}.pdf"
            doc_name = src.split("/")[-1].replace("%20", " ") if "/" in src else src
            context_parts.append(f"--- Document {i} [{doc_name}] ---\n{doc.get('text')}")
        context_str = "\n\n### Retrieved Knowledge Base Documents (from S3):\n" + "\n\n".join(context_parts)

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
            return response["output"]["message"]["content"][0]["text"]
    except Exception as e:
        print(f"Bedrock chat converse warning: {e}")

    # Fallback
    return f"Here are curated travel recommendations for your journey:\n\n{user_message}"


def infer_conversation_title(user_message: str) -> str:
    """
    Infers a concise conversation title (maximum 3 words) based on the user's message.
    Uses Bedrock Nova Lite if available, with a deterministic heuristic fallback.
    """
    cleaned = user_message.strip()
    if not cleaned or is_casual_query(cleaned):
        return "Travel Chat"

    # 1. Try Bedrock Nova Lite inference
    if bedrock_client:
        try:
            system_prompt = (
                "Generate a concise conversation title of at most 3 words based on the user's travel message. "
                "Output ONLY the title (maximum 3 words), nothing else. No punctuation, no quotes."
            )
            resp = bedrock_client.converse(
                modelId=MODEL_ID,
                messages=[{"role": "user", "content": [{"text": cleaned[:200]}]}],
                system=[{"text": system_prompt}],
                inferenceConfig={"maxTokens": 10, "temperature": 0.2},
            )
            raw_title = resp["output"]["message"]["content"][0]["text"].strip()
            # Clean punctuation and quotes
            raw_title = re.sub(r'[^\w\s]', '', raw_title).strip()
            words = raw_title.split()
            if words:
                return " ".join(words[:3]).title()
        except Exception as e:
            print(f"Bedrock title inference note: {e}")

    # 2. Heuristic fallback guaranteeing <= 3 words
    text = re.sub(r'[^\w\s]', ' ', cleaned).strip()
    filler_patterns = [
        r'^(can you|could you|please|help me|i want to|i would like to|i need to|im planning to|i am planning to)\s+',
        r'^(plan a trip to|plan an itinerary for|plan trip to|travel to|visit|go to|explore)\s+',
        r'^(recommend some|recommend top|recommend|what is the|what are the|where can i find|tell me about)\s+',
        r'^(best|top)\s+',
    ]
    lowered = text.lower()
    for pattern in filler_patterns:
        lowered = re.sub(pattern, '', lowered).strip()

    words = [w for w in lowered.split() if w]
    if words:
        return " ".join(words[:3]).title()

    return "Travel Plan"


def stream_chat_response(history: list[dict], user_message: str) -> Generator[str, None, None]:
    """
    Streams conversational response chunk-by-chunk using Bedrock converse_stream and RAG.
    """
    # 1. Retrieve knowledge base docs (RAG)
    kb_results = retrieve_from_knowledge_base(user_message)

    context_str = ""
    if kb_results:
        context_parts = []
        for i, doc in enumerate(kb_results, 1):
            src = doc.get("source_uri") or f"s3://{KNOWLEDGE_BASE_S3_BUCKET}/doc_{i}.pdf"
            doc_name = src.split("/")[-1].replace("%20", " ") if "/" in src else src
            context_parts.append(f"--- Document {i} [{doc_name}] ---\n{doc.get('text')}")
        context_str = "\n\n### Retrieved Knowledge Base Documents (from S3):\n" + "\n\n".join(context_parts)

    # 2. Format history
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

    augmented_user_message = user_message
    if context_str:
        augmented_user_message = f"{user_message}\n\n{context_str}"

    formatted_messages.append({
        "role": "user",
        "content": [{"text": augmented_user_message}]
    })

    system_prompts = [{"text": RAG_CHAT_SYSTEM_PROMPT}]

    stream_success = False
    if bedrock_client:
        try:
            response = bedrock_client.converse_stream(
                modelId=MODEL_ID,
                messages=formatted_messages,
                system=system_prompts,
                inferenceConfig={
                    "maxTokens": 1024,
                    "temperature": 0.7,
                },
            )
            stream = response.get("stream")
            if stream:
                for event in stream:
                    if "contentBlockDelta" in event:
                        delta = event["contentBlockDelta"]["delta"].get("text", "")
                        if delta:
                            yield delta
                stream_success = True
        except Exception as e:
            print(f"Bedrock converse_stream error: {e}")

    if not stream_success:
        fallback_text = f"Here are curated travel recommendations for your journey:\n\n{user_message}"
        words = fallback_text.split(" ")
        for i, w in enumerate(words):
            yield w + (" " if i < len(words) - 1 else "")
            time.sleep(0.03)

