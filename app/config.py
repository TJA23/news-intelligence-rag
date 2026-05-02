from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ARTICLES_DIR = DATA_DIR / "articles"
INDEX_DIR = DATA_DIR / "index"
ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

ARTICLES_PATH = ARTICLES_DIR / "articles.json"
FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
CHUNKS_PATH = INDEX_DIR / "chunks.json"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384
CHUNK_SIZE = 350
CHUNK_OVERLAP = 60
TOP_K = 5

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

RSS_FEEDS = [
    ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("Reuters World", "https://feeds.reuters.com/Reuters/worldNews"),
    ("NPR World", "https://feeds.npr.org/1004/rss.xml"),
    ("The Guardian World", "https://www.theguardian.com/world/rss"),
    ("Hacker News Front", "https://hnrss.org/frontpage"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
]

MAX_ARTICLES_PER_FEED = 10
