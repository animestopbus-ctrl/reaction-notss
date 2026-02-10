web: uvicorn main:main_app --host=0.0.0.0 --port=${PORT:-8000}
worker: python keep_alive.py
release: mkdir -p logs && touch logs/lastperson07.log
