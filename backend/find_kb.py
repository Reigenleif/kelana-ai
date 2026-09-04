import os

import boto3
from dotenv import load_dotenv

load_dotenv()

ak = os.getenv("AWS_ACCESS_KEY_ID")
sk = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_REGION", "ap-southeast-2")

print(f"Connecting to AWS Bedrock in region {region} with access key {ak[:4] if ak else 'None'}...")
agent_client = boto3.client("bedrock-agent", region_name=region, aws_access_key_id=ak, aws_secret_access_key=sk)

try:
    resp = agent_client.list_knowledge_bases()
    kbs = resp.get("knowledgeBaseSummaries", [])
    print(f"Found {len(kbs)} Knowledge Base(s):")
    for kb in kbs:
        name = kb.get("name")
        kb_id = kb.get("knowledgeBaseId")
        status = kb.get("status")
        updated = kb.get("updatedAt")
        print(f"  - Name: {name}")
        print(f"    Knowledge Base ID: {kb_id}")
        print(f"    Status: {status}")
        print(f"    Updated: {updated}\n")
except Exception as e:
    print(f"Error listing knowledge bases: {e}")
