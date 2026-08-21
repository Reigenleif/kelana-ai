import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
MODEL_ID = os.getenv("MODEL_ID", "amazon.nova-lite-v1:0")

# Instantiate Bedrock Runtime client
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

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
        raise RuntimeError(f"AWS Bedrock generation failed: {str(e)}")
