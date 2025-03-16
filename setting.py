import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")

model_name = 'gemini-1.5-flash'
end_fn_name = 'create_final_result'