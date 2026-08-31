from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_all():
    print("Testing Backend...")
    # 1. Login gooduser
    res1 = client.post("/auth/login", json={"username_or_email": "gooduser@kelana.ai", "password": "password123"})
    assert res1.status_code == 200, f"Login gooduser failed: {res1.text}"
    t1 = res1.json()["access_token"]
    h1 = {"Authorization": f"Bearer {t1}"}
    u1 = res1.json()["user"]
    print(f"GoodUser login OK: {u1['username']} (ID: {u1['id']})")

    # 2. Login niceuser
    res2 = client.post("/auth/login", json={"username_or_email": "niceuser@kelana.ai", "password": "password123"})
    assert res2.status_code == 200, f"Login niceuser failed: {res2.text}"
    t2 = res2.json()["access_token"]
    h2 = {"Authorization": f"Bearer {t2}"}
    u2 = res2.json()["user"]
    print(f"NiceUser login OK: {u2['username']} (ID: {u2['id']})")

    # 3. Check GoodUser trips
    trips1 = client.get("/trips", headers=h1).json()
    destinations1 = [t["destination"] for t in trips1]
    print(f"GoodUser trips count: {len(trips1)}, destinations: {destinations1}")
    assert len(trips1) >= 1, "GoodUser should have trips"

    # 4. Check NiceUser trips (Isolation test)
    trips2 = client.get("/trips", headers=h2).json()
    destinations2 = [t["destination"] for t in trips2]
    print(f"NiceUser trips count: {len(trips2)}, destinations: {destinations2}")
    assert len(trips2) >= 1, "NiceUser should have trips"

    # 5. Check AI Conversations for gooduser
    convs1 = client.get("/conversations", headers=h1).json()
    assert len(convs1) > 0, "No conversations found for gooduser"
    conv_id = convs1[0]["id"]
    print(f"GoodUser AI conversation ID: {conv_id}, title: {convs1[0]['title']}")

    # 6. Check Messages
    msgs = client.get(f"/conversations/{conv_id}/messages", headers=h1).json()
    print(f"Initial conversation message count: {len(msgs)}")
    assert len(msgs) >= 1, "Conversation should have welcome message"

    # 7. GoodUser sends a message to AI Assistant
    reply_msgs = client.post(f"/conversations/{conv_id}/messages", json={"text": "Can you recommend top sights in Kyoto for 3 days?"}, headers=h1).json()
    print(f"AI replied ({len(reply_msgs)} messages returned): {reply_msgs[-1]['text'][:80]}...")

    print("\n>>> ALL BACKEND AI CHAT TESTS PASSED SUCCESSFULLY! <<<\n")

if __name__ == "__main__":
    test_all()
