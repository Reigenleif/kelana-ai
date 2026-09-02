import os
import sys
from dotenv import load_dotenv

# Ensure utf-8 output encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

print("Testing Bedrock Knowledge Base RAG Connection...")
region = os.getenv("AWS_REGION", "ap-southeast-2")
kb_id = os.getenv("KNOWLEDGE_BASE_ID")
ak = os.getenv("AWS_ACCESS_KEY_ID")
print("Region:", region)
print("KB ID:", kb_id)
print("Access Key present:", bool(ak))

from services.bedrock_service import retrieve_from_knowledge_base, generate_chat_response

print("\n--- 1. Testing KB Retrieval ---")
chunks = retrieve_from_knowledge_base("travel guide and destinations", max_results=3)
print(f"Retrieved {len(chunks)} chunks from Knowledge Base:")
for i, c in enumerate(chunks, 1):
    src = c.get("source_uri")
    score = c.get("score")
    preview = c.get("text", "")[:200]
    print(f"Chunk {i} [Source: {src}, Score: {score}]")
    print(f"Content:\n{preview}...\n")

print("\n--- 2. Testing AI Chat Response with RAG & Bedrock Converse ---")
history = [{"sender": "user", "text": "Hello"}]
reply = generate_chat_response(history, "Give me a summary of travel recommendations and places to visit from our documents")
print("AI Response:\n")
print(reply)
