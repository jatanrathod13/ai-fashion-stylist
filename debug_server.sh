#!/bin/bash
cd "/Users/jatanrathod/AI Fashion Shopper"
export OPENAI_TEXT_MODEL=gpt-4o-mini
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8001 --log-level debug 