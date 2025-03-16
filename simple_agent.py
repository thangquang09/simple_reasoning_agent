from google import genai
from google.genai import types
from tools_config import *
from setting import *
import time



config = types.GenerateContentConfig(
    tools=[tools_config],
    temperature=0
)
client = genai.Client(api_key=GOOGLE_API_KEY)

def simplify_results(intermediate_results, max_length=500):
    simplified = []
    for item in intermediate_results:
        simple_item = {
            "action": item["action"],
            "parameters": item["parameters"]
        }
        
        if "result" in item and isinstance(item["result"], str) and len(item["result"]) > max_length:
            simple_item["result"] = item["result"][:max_length] + "... (truncated)"
        else:
            simple_item["result"] = item["result"]
            
        simplified.append(simple_item)
    
    return simplified

def make_response(prompt):

    state = prompt["state"]
    user_input = prompt["user_input"]
    intermediate_results = simplify_results(prompt["intermediate_results"])
    
    contents = f"""You are a reasoning and acting agent. Based on the current state and user input, decide the next action.
            State: {state}
            User Input: {user_input}
            Intermediate Results: {intermediate_results}
            
            Please pay attention to current state and previous actions in the Intermediate Results. If an action has already been performed, consider not repeating that action again.
            """.strip()
                
    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=config
    )
    
    
    if response.function_calls:
        function_call = response.function_calls[0]
        function_name = function_call.name
        function_args = function_call.args
        
        # print(function_name)
        # print(function_args)
        
        return function_name, function_args 
    else:
        print("not using function call")
        return (end_fn_name,) 
    
def generate_with_function_calling(prompt: dict, max_iter: int = 5):
    intermediate_results = []
    for step in range(max_iter):
        
        fn_name, args = make_response(prompt)
        print("Current task: ", fn_name)
        print("Thinking ...")
        if fn_name == end_fn_name:
            # return intermediate_results[-1]["result"]
            final_response_content = f"""Based on the following information, provide a direct response to the user's question:
                        
            User Input: {prompt['user_input']}
                        
            Intermediate Results: {intermediate_results if intermediate_results else 'No intermediate processing was needed to answer this question directly.'}

            Please provide a clear, concise answer to the user's question based on the available information.""".strip()
            
            response = client.models.generate_content(
                model=model_name,
                contents=final_response_content,
            )
            return response.text
            
        action_result = func_mapping[fn_name](**args)
        # print(action_result)
    
        # update prompt
        new_state = {
            "status": "in_progress",
            "last_action": fn_name,
            "last_parameters": args
        }
        
        intermediate_results.append(
            {
                "action": fn_name,
                "parameters": args,
                "result": action_result
            }
        )
        
        prompt.update(
            {
                "state": new_state,
                "intermediate_results": intermediate_results
            }
        )
        print("Finish task ", fn_name)
        time.sleep(1)
        
    return intermediate_results

    
prompt = {
    "state": {"status": "start", "last_action": None, "last_parameters": None},
    "user_input": "1 + 1 bằng bao nhiêu?",
    "intermediate_results": [

    ]
}

print(generate_with_function_calling(prompt))