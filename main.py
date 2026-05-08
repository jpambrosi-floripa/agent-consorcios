#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from src.cli import app

# Load .env file
load_dotenv()

if __name__ == "__main__":
    app()
