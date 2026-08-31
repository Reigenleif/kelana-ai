from datetime import datetime
from sqlalchemy import text
from database import Base, SessionLocal, engine
from models.chat import Conversation, Message
from models.trip import Trip
from models.user import User
from services.auth_service import hash_password


def run_migration_and_seed():
    print("Running database tables creation / update...")

    with engine.connect() as conn:
        print("Applying table migrations...")
        try:
            # Check if conversations needs AI-only schema (drop old user2 schema if needed)
            conn.execute(text("""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='conversations' AND column_name='user1_id'
                    ) THEN
                        DROP TABLE IF EXISTS messages CASCADE;
                        DROP TABLE IF EXISTS conversations CASCADE;
                    END IF;
                END $$;
            """))
            conn.commit()
        except Exception as e:
            print(f"Migration check: {e}")

    # Import all models so metadata knows them
    Base.metadata.create_all(bind=engine)
    print("Base metadata created.")

    # Apply ALTER TABLE migrations for existing schemas
    with engine.connect() as conn:
        print("Applying column migrations if needed...")
        try:
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='trips' AND column_name='user_id'
                    ) THEN
                        ALTER TABLE trips ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='trips' AND column_name='created_at'
                    ) THEN
                        ALTER TABLE trips ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                    END IF;
                END $$;
            """))
            conn.commit()
        except Exception as e:
            print(f"Migration note: {e}")

    db = SessionLocal()
    try:
        # Check / Seed User 1 (gooduser)
        user1 = db.query(User).filter(User.username == "gooduser").first()
        if not user1:
            user1 = User(
                username="gooduser",
                email="gooduser@kelana.ai",
                password_hash=hash_password("password123"),
                full_name="Good User",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
                bio="Passionate explorer of mountain peaks and cultural heritage.",
            )
            db.add(user1)
            db.commit()
            db.refresh(user1)
            print(f"Created user: {user1.username} (id: {user1.id})")
        else:
            print(f"User {user1.username} already exists.")

        # Check / Seed User 2 (niceuser)
        user2 = db.query(User).filter(User.username == "niceuser").first()
        if not user2:
            user2 = User(
                username="niceuser",
                email="niceuser@kelana.ai",
                password_hash=hash_password("password123"),
                full_name="Nice User",
                avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
                bio="Backpacker, foodie, and beach lover wandering around Southeast Asia & Europe.",
            )
            db.add(user2)
            db.commit()
            db.refresh(user2)
            print(f"Created user: {user2.username} (id: {user2.id})")
        else:
            print(f"User {user2.username} already exists.")

        # Seed sample trips for gooduser if none
        trips_u1 = db.query(Trip).filter(Trip.user_id == user1.id).count()
        if trips_u1 == 0:
            db.add(Trip(
                user_id=user1.id,
                destination="Kyoto & Osaka, Japan",
                days=7,
                budget=2500.0,
                category="Culture & Food",
                daily_budget=357.14,
                ai_recommendation="# 🌸 7-Day Kansai Adventure (Kyoto & Osaka)\n\n### 🗓 Day 1-3: Ancient Kyoto\n- **Highlights**: Fushimi Inari Shrine at dawn, Arashiyama Bamboo Grove, Kinkaku-ji (Golden Pavilion).\n- **Food**: Kaiseki dinner in Gion, Matcha soft-serve at Uji.\n\n### 🗓 Day 4-7: Vibrant Osaka\n- **Highlights**: Dotonbori food crawl, Osaka Castle, Shinsekai retro district.\n- **Budget Tip**: Use Kansai Thru Pass for seamless transport.",
                created_at=datetime.utcnow(),
            ))
            db.add(Trip(
                user_id=user1.id,
                destination="Swiss Alps & Zermatt",
                days=5,
                budget=3400.0,
                category="Luxury",
                daily_budget=680.0,
                ai_recommendation="# 🏔️ 5-Day Swiss Alps Luxury Escape\n\n### 🗓 Day 1-2: Zermatt & Matterhorn\n- **Highlights**: Gornergrat Railway, luxury spa resort in Zermatt.\n- **Dining**: Fondue dinner overlooking the Matterhorn.\n\n### 🗓 Day 3-5: Interlaken & Jungfraujoch\n- **Highlights**: Top of Europe excursion, private helicopter tour over Aletsch Glacier.",
                created_at=datetime.utcnow(),
            ))
            db.commit()
            print(f"Seeded trips for {user1.username}")

        # Seed sample trips for niceuser if none
        trips_u2 = db.query(Trip).filter(Trip.user_id == user2.id).count()
        if trips_u2 == 0:
            db.add(Trip(
                user_id=user2.id,
                destination="Bali & Nusa Penida, Indonesia",
                days=10,
                budget=1200.0,
                category="Backpacker",
                daily_budget=120.0,
                ai_recommendation="# 🌴 10-Day Bali Backpacker Journey\n\n### 🗓 Day 1-4: Ubud Cultural Heart\n- **Highlights**: Campuhan Ridge Walk, Tegallalang Rice Terraces, Ubud Art Market.\n- **Budget Food**: Warung Babi Guling, Nasi Campur ($3/meal).\n\n### 🗓 Day 5-7: Nusa Penida Island\n- **Highlights**: Kelingking T-Rex Beach, Broken Beach, Manta Point snorkeling.\n\n### 🗓 Day 8-10: Canggu & Uluwatu\n- **Highlights**: Sunset at Uluwatu Cliff Temple, surfing in Echo Beach.",
                created_at=datetime.utcnow(),
            ))
            db.commit()
            print(f"Seeded trips for {user2.username}")

        # Seed AI assistant conversations for users
        for u in [user1, user2]:
            conv = db.query(Conversation).filter(Conversation.user_id == u.id).first()
            if not conv:
                conv = Conversation(
                    user_id=u.id,
                    title="Kelana AI Travel Assistant",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(conv)
                db.commit()
                db.refresh(conv)

                m1 = Message(
                    conversation_id=conv.id,
                    sender="assistant",
                    text=f"Hello {u.full_name or u.username}! I am your Kelana AI Travel Assistant. Where are you planning to travel next?",
                    created_at=datetime.utcnow(),
                )
                db.add(m1)
                db.commit()

        print("Migration and seed completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    run_migration_and_seed()
