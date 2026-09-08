import json
from claude_api import ClaudeClient
from statistics import mean
import ast
import re
client = ClaudeClient()

def run_prompt(test_case):
    """
    Merges the prompt and test case input, then returns the result"""
    prompt = f"""
    Please solve the following task:

    {test_case["task"]}

    * Respond only with Python, json or a plain regex
    * Do not add any comments or explanation
    """
    
    messages = []
    client.add_user_message(messages, prompt)
    client.add_assistant_message(messages, "```code")
    output = client.chat(messages, stop_sequences=["```"])
    return output

def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        print(f"Error: {text}")
        return 0
    
def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        print(f"Error: {text}")
        return 0
    
def validate_regex(text):
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        print(f"Error: {text}")
        return 0

def run_eval_model(test_case, output):
    eval_prompt = f"""
    You are an expert AWS code reviewer. Your task is to evaluate the following AI-generated solution.

    Original Task:
    <task>
    {test_case["task"]}
    </task>

    Solution to Evaluate:
    <solution>
    {output}
    </solution>

    Criteria you should use to evaluate the solution:
    <criteria>
    {test_case["solution_criteria"]}
    </criteria>

    Output Format
        Provide your evaluation as a structured JSON object with the following fields, in this specific order:
        - "strengths": An array of 1-3 key strengths
        - "weaknesses": An array of 1-3 key areas for improvement
        - "reasoning": A concise explanation of your overall assessment
        - "score": A number between 1-10

        Respond with JSON. Keep your response concise and direct.
        Example response shape:
        {{
            "strengths": string[],
            "weaknesses": string[],
            "reasoning": string,
            "score": number
        }}
    """

    messages = []
    client.add_user_message(messages, eval_prompt)
    client.add_assistant_message(messages, "```json")
    eval_text = client.chat(messages, stop_sequences=["```"])
    return json.loads(eval_text)

def run_code_eval(test_case, output):
    if test_case["format"] == "python":
        return validate_python(output)
    elif test_case["format"] == "json":
        return validate_json(output)
    elif test_case["format"] == "regex":
        return validate_regex(output)

def run_test_case(test_case):
    """Calls run_prompt, then grades the result"""
    output = run_prompt(test_case)
    
    # TODO - Grading
    model_grade = run_eval_model(test_case, output)
    score = model_grade["score"]

    code_grade = run_code_eval(test_case, output)
    
    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "score_code": code_grade
    }

def run_eval(dataset):
    """Loads the dataset and calls run_test_case with each case"""
    results = []
    
    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)

    average_score = mean([result["score"] for result in results])
    average_score_code = mean([result["score_code"] for result in results])
    print(f"Average score: {average_score}")
    print(f"Average score code: {average_score_code}")
    
    return results

with open("dataset.json", "r") as f:
    dataset = json.load(f)

results = run_eval(dataset)

print(json.dumps(results, indent=2))
