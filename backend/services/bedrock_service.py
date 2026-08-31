import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
MODEL_ID = os.getenv("MODEL_ID", "amazon.nova-lite-v1:0")

# Instantiate Bedrock Runtime client
try:
    bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
except Exception:
    bedrock_client = None

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

CHAT_SYSTEM_PROMPT = """You are Kelana AI, an intelligent, friendly, and highly knowledgeable AI Travel Assistant.
You assist travelers with destination ideas, travel itineraries, budgeting advice, local cuisines, weather, packing tips, and transportation guidance.
Be concise, helpful, structured, and use Markdown formatting where appropriate.
"""


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

    # High quality fallback recommendation if bedrock credentials or quota fail
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
    Generates conversational response for the AI Travel Assistant.
    """
    formatted_messages = []
    # Take history ensuring alternate roles and starting with user
    recent_history = history[-6:] if history else []
    
    # Filter so it starts with user if any history is included
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

    formatted_messages.append({
        "role": "user",
        "content": [{"text": user_message}]
    })

    system_prompts = [{"text": CHAT_SYSTEM_PROMPT}]

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

    # Smart conversational fallback
    lower_msg = user_message.lower()
    if "kyoto" in lower_msg or "japan" in lower_msg:
        return "Kyoto is fantastic! For autumn or spring, I highly recommend visiting Fushimi Inari at sunrise, exploring the Arashiyama Bamboo Grove, and having matcha desserts in Gion. Would you like a detailed daily schedule or budget recommendation for Japan?"
    elif "bali" in lower_msg or "indonesia" in lower_msg:
        return "Bali has something for every style! In Ubud, you'll love the Tegallalang rice terraces and yoga retreats. If you like beaches and surfing, Uluwatu and Canggu are top picks. Are you planning a backpacker or luxury trip?"
    elif "budget" in lower_msg or "cost" in lower_msg:
        return "To optimize your travel budget, I suggest booking rail passes in advance, eating at authentic local warungs/bistros, and staying in well-reviewed boutique guesthouses. Where are you planning to go next?"
    else:
        return f"Hello! As your Kelana AI Travel Assistant, I'm here to help you plan trips, optimize itineraries, find hidden spots, and organize daily activities. What destination are you considering?"
