from typing import List, Dict
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.callbacks import get_openai_callback
from pydantic import BaseModel, Field
from models import CodeCheckResponse


def CodeCheck(question, code, llm):
    # Define the prompt
    prompt = f"""
    Check if the following code is correct. For correct code, return 'Correct'. For incorrect code, return 'Incorrect'. 
    For the INCORRECT code provide a detailed explanation of why it is incorrect and how it can be corrected. 
    DO NOT PROVIDE ANY DIRECT HINTS OR DIRECT SOLUTION IN THE EXPLANATION. 
    Question: 
    {question} 

    Code: 
    {code}

    Please provide the scores and feedback to the candidate in the following format:

    Correctness: {{Correct or Incorrect}}
    Explanation: {{Detailed explanation of why the code is incorrect and how it can be improved.}}
    Efficiency: {{If the code is incorrect mention "None". If the code is correct, give suggestions on how the code can be optimised. Also, suggest some alternate ways of implementation.}}
    
    PLEASE RESPOND ONLY IN FORMAT AS MENTIONED ABOVE.
    """
    with get_openai_callback() as cb:
        response = llm.predict(prompt)
        print(f"Usage: {cb}")

    parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=CodeCheckResponse), llm=llm)
    # format_instructions = parser.get_format_instructions()

    codecheck = parser.parse(response)

    return codecheck, cb


def runcode(code):
    try:
        exec(code)
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"Error occurred: {e}"


#### 
# example for run code
code = """
def larger(a,b):
    if a>b:
        return a
    elif b>a:
        return b
    else:
        return None

print(larger(3,4))

"""

runcode(code)
######
