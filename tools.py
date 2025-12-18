import requests
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

def web_search(query: str) -> List[Dict[str, str]]:
    api_key = "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"
    url = "https://api.tavily.com/search"
    
    params = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "max_results": 5
    }
    
    try:
        response = requests.post(url, json=params)
        data = response.json()
        print(f"Raw response for '{query}':", data)  # DEBUG - remove later
        
        results = data.get("results", [])
        return [
            {
                "title": r.get("title", ""),
                "snippet": r.get("content", ""),
                "url": r.get("url", "")
            }
            for r in results
        ]
    except Exception as e:
        print(f"Search error: {e}")  # DEBUG
        return [{"title": "Demo", "snippet": f"Sample for '{query}'", "url": "#"}]
