# modules/gemini_parser.py

import json
from google import genai

def call_gemini(prompt: str) -> str:
    """
    Call the Gemini (google-genai) model with a given prompt and return its raw text response.

    This function initializes a Gemini client with the specified API key, then sends the prompt to 
    the Gemini model to generate content. It strips any leading or trailing whitespace from the 
    response text before returning it.

    Args:
        prompt (str): The prompt string to be sent to the Gemini model. This should include the 
                      detailed instructions for the model on how to parse the tasks.

    Returns:
        str: The raw text response from the Gemini model, with whitespace removed.

    Example:
        >>> prompt = "Parse the following tasks: Remind me to call John at 17:00"
        >>> output = call_gemini(prompt)
        >>> print(output)
    """
    # Initialize the Gemini client with the provided API key.
    client = genai.Client(api_key="Your APi key here")
    
    # Generate content using the specified Gemini model and the given prompt.
    response = client.models.generate_content(
        model="gemini-2.0-flash",  # Specify the Gemini model to use.
        contents=prompt
    )
    # Return the generated text after stripping any extra whitespace.
    return response.text.strip()


def clean_llm_output(llm_output: str) -> str:
    """
    Clean the output from the language model by removing markdown code fences.

    Some language model outputs may be wrapped in markdown code fences (e.g., ```json ... ```).
    This function checks for and removes these fences from both the start and the end of the output.

    Args:
        llm_output (str): The raw output string from the language model that may contain markdown fences.

    Returns:
        str: The cleaned output string without any markdown code fences.

    Example:
        >>> dirty_output = "```json\n[{'task': 'example'}]\n```"
        >>> clean_output = clean_llm_output(dirty_output)
        >>> print(clean_output)
    """
    # Check if the output starts with a markdown code fence for JSON and remove it.
    if llm_output.startswith("```json"):
        llm_output = llm_output[len("```json"):].strip()
    # Check if the output ends with a markdown code fence and remove it.
    if llm_output.endswith("```"):
        llm_output = llm_output[:-3].strip()
    return llm_output


def parse_tasks(task_text: str) -> list:
    """
    Parse raw task instructions into a structured list of task dictionaries using Gemini.

    This function builds a detailed prompt that instructs the Gemini model on how to interpret the 
    raw task instructions. It calls the Gemini model with the prompt, cleans the returned output 
    (removing any markdown formatting), and then attempts to parse the output as JSON. If parsing 
    fails, an error is printed and an empty list is returned.

    Args:
        task_text (str): The raw task instructions as a string. These are the tasks provided by the user,
                         such as "Remind me to call John at 17:00".

    Returns:
        list: A list of task dictionaries parsed from the language model's output. Each dictionary 
              contains keys like "task_type", "time", and additional fields based on the task type.
              Returns an empty list if the output is not valid JSON.

    Example:
        >>> tasks_text = "Remind me to call John at 17:00"
        >>> tasks = parse_tasks(tasks_text)
        >>> print(tasks)
    """
    # Construct the prompt with instructions and examples for Gemini.
    prompt = (
        "You are an assistant that parses user instructions about tasks into JSON.\n\n"
        "The user will provide lines like:\n"
        "- \"Remind me to do X at HH:MM\"\n"
        "- \"Send me the price of NVDA stock via email at HH:MM\"\n"
        "- \"Add an invite for a meeting on YYYY-MM-DD at HH:MM\"\n\n"
        "Output a JSON array of task objects. Each object has:\n"
        "1) \"task_type\" : one of [\"email_reminder\", \"stock_price\", \"calendar_invite\"]\n"
        "2) \"time\" : a string like \"17:00\" or in ISO format, e.g. \"2025-03-15T16:30:00\"\n"
        "3) Additional fields depending on the task type:\n"
        "   - For an email_reminder: \"email\", \"subject\", \"message\"\n"
        "   - For a stock_price: \"stock_symbol\", \"email\", \"subject\"\n"
        "   - For a calendar_invite: an \"event\" object with \"summary\", \"start\", and \"end\"\n\n"
        "Output valid JSON only, with no extra text. For example:\n\n"
        "[\n"
        "  {\n"
        "    \"task_type\": \"email_reminder\",\n"
        "    \"email\": \"someone@gmail.com\",\n"
        "    \"subject\": \"Reminder\",\n"
        "    \"message\": \"Remind me to do X\",\n"
        "    \"time\": \"17:00\"\n"
        "  }\n"
        "]\n\n"
        "Now parse these instructions into JSON:\n\n"
    ) + task_text

    # Call Gemini with the constructed prompt to get the raw output.
    llm_output = call_gemini(prompt)
    
    # Clean the LLM output to remove any markdown code fences.
    llm_output = clean_llm_output(llm_output)

    # Attempt to parse the cleaned output into a JSON object (list).
    try:
        tasks = json.loads(llm_output)
        return tasks
    except json.JSONDecodeError as e:
        # Print error messages if the output is not valid JSON.
        print("[Gemini Parser] Error: LLM did not return valid JSON.")
        print("Raw output was:", llm_output)
        return []


def pretty_print_tasks(tasks: list):
    """
    Print the list of tasks in a formatted JSON style for readability.

    This function uses json.dumps to convert the list of task dictionaries into a prettified JSON
    string and prints it to the console. It is mainly used for debugging and verifying the output.

    Args:
        tasks (list): A list of task dictionaries that need to be printed in a formatted manner.

    Returns:
        None

    Example:
        >>> tasks = [{"task_type": "email_reminder", "time": "17:00", "email": "test@example.com"}]
        >>> pretty_print_tasks(tasks)
    """
    print(json.dumps(tasks, indent=2))
