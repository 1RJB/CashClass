from app.config import Config
from app import create_app
import os, warnings

app = create_app(Config)
if not os.environ.get("NEWS_API_KEY"):
    warnings.warn("NEWS_API_KEY not set")
if __name__ == '__main__':
    app.run() 
