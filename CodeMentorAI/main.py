from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
from fastapi.staticfiles import StaticFiles
from langchain.chains import LLMChain
import os
os.environ['OPENAI_API_KEY'] = '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'
from langchain_openai import OpenAI
from langchain.chains.openai_functions import (
    
    create_openai_fn_chain,
    create_openai_fn_runnable,
    create_structured_output_chain,
    create_structured_output_runnable,
)
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="testapplication")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

llm = OpenAI(temperature=0.9)

class Code_Eval(BaseModel):
    """Identifying information about a person."""
    correct: bool = Field(..., description="Whether the code is correct or not")
    explanation: str = Field(..., description="Explanation about the correctness or incorrectness of the code without any suggestion.")
    suggestion: str = Field(..., description="Only hints for correcting the code without any direct solution.")
prompt = PromptTemplate(
    input_variables=["question", "code"],
    template="Check if the following code is correct. If it is incorrect, provide a detailed explanation of why it is "
            "incorrect and provide hints of how it can be corrected."
            "DO NOT PROVIDE ANY DIRECT SOLUTION IN ANY FORM."
            "ANSWER. Question: {question} Code: {code}",
)
chain = LLMChain(llm=llm, prompt=prompt)

llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI assistant. Your job is to provide the best assistance to the user.",
        ),
        (
            "human",
            "Check if the following code is correct. For incorrect code provide an explanation of why it is "
            "incorrect. Do not return 'Correct'. "
            "Next, provide suggestion of how it can be corrected WITHOUT ANY DIRECT HINTS OR DIRECT SOLUTION."
            "Question: {question} Code: {code}"
            "Return the output in the following format \n Correct: \n Explanation: \n Suggestion: ",
        ),
        ("human", "Tip: Make sure to answer in the correct format"),
    ]
)

runnable = create_structured_output_runnable(Code_Eval, llm, prompt)

with open("static/problems.json", "r", encoding="utf-8") as file:
    questions_data = json.load(file)


@app.get("/")
def form_post(request: Request):
    return templates.TemplateResponse('form.html', context={'request': request})


from starlette.responses import JSONResponse

@app.post("/")
async def form_post(request: Request):
    form_data = await request.form()
    print("Form data:", form_data)

    topic = form_data.get('topics')
    print("Topic:", topic)
    if topic is None:
        return JSONResponse({"error": "No topic provided"})
    try:
        topic_index = int(topic) - 1
    except ValueError:
        return JSONResponse({"error": "Invalid topic"})
    if not (0 <= topic_index < len(questions_data)):
        return JSONResponse({"error": "Topic index out of range"})

    topic_name = questions_data[topic_index]['title']
    question = form_data.get('question')
    code = form_data.get('code')

    output = runnable.invoke({"question": question, "code": code})
    print(output)

    return JSONResponse({
        "topic": topic_name,
        "code": code,
        "question": question,
        'correct': str(output.correct),
        "explanation": output.explanation,
        "suggestion": output.suggestion
    })

