from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables first

from flask import Flask
app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

from ReikiNikki import views  # Import views last