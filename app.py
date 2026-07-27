
from app import create_app, db

app = create_app()

with app.app_context():
    try:
        db.engine.connect()
        print("✅ Successfully connected to Supabase!")
    except Exception as e:
        print("❌ Connection failed!")
        print(e)

if __name__ == "__main__":
    app.run()