import requests
import os
from google import genai
from google.genai.types import (
    FunctionDeclaration,
    GenerateContentConfig,
    Tool,
)
from setting import SEARCH_API_KEY, GOOGLE_API_KEY, end_fn_name

model_name = 'gemini-2.0-flash'

def search(api_key:str = SEARCH_API_KEY, query: str = "", number_samples_return: int = 5) -> str:
    url = "https://api.serphouse.com/serp/live"
    payload = '''{
        "data": {
            "q": "%s",
            "domain": "google.com",
            "loc": "Vietnam",
            "lang": "vi",
            "device": "desktop",
            "serp_type": "web",
            "page": "1",
            "verbatim": "0"
        }
    }''' % query
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': f"Bearer {api_key}"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    if response.status_code == 200:
        # print("Successfully Search")
        response_json = response.json()
        results = response_json.get("results").get("results").get("organic")
        
        if results:
            results = [sample['snippet'] for sample in results[:number_samples_return]]
            final_results = ' '.join(results)
        else:
            final_results = 'There is no result'
        return final_results
    else:
        print(f"Error in search: {response.status_code}")
        return 'There is no result'

def summarize(query: str, text: str) -> str:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = client.models.generate_content(
        model=model_name,
        contents=f"Summarize this text based on query.\nQuery: {query}\nText: {text}"
    )
    return response.text

def do_nothing():
    return None
    

search_function = FunctionDeclaration(
    name="search",
    description="Search the web for current information on a specific topic. Use this when you need external knowledge that's not in the conversation.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query to find information about (e.g., 'weather in Tokyo', 'latest news')"
            },
            "number_samples_return": {
                "type": "INTEGER",
                "description": "Number of search results to return (default: 5)"
            },
            "api_key": {
                "type": "STRING",
                "description": "Optional API key for the search service"
            }
        },
        "required": ["query"]
    },
)

summarize_function = FunctionDeclaration(
    name="summarize",
    description="Summarize or analyze text that has already been provided. Use this when the user gives you text and asks for a summary or analysis.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "What aspect to focus on in the summarization (e.g., 'main points', 'key characters')"
            },
            "text": {
                "type": "STRING", 
                "description": "The full text content to be summarized - this must be the actual content needing summarization"
            }
        },
        "required": ["query", "text"]
    },
)

do_nothing_function = FunctionDeclaration(
    name=end_fn_name,
    description="Do nothing and return a direct response. Use this when no external search or summarization is needed.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "dummy": {
                "type": "STRING",
                "description": "Dummy parameter (not used)"
            }
        },
        "required": []
    },
)

tools_config = Tool(
    function_declarations=[
        search_function,
        summarize_function,
        do_nothing_function
    ],
)

func_mapping = {
    "search": search,
    "summarize": summarize,
    end_fn_name: do_nothing
}