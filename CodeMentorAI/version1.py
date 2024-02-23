import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
# from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from fastapi.staticfiles import StaticFiles
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser

from utils import CodeCheck, runcode
from starlette.middleware.sessions import SessionMiddleware

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Mount the "static" folder to "/static" URL
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Initialize the OpenAI API
# llm = OpenAI(temperature=0.9)
codellama_model = ChatOpenAI(model='codellama/CodeLlama-34b-Instruct-hf',
                             openai_api_base="https://api.endpoints.anyscale.com/v1",
                             openai_api_key=os.getenv("ANYSCALE_API_TOKEN"))

gpt3_model = ChatOpenAI(model="gpt-3.5-turbo-1106")


@app.get("/")
def form_post(request: Request):
    return templates.TemplateResponse('form.html', context={'request': request})


@app.post("/")
async def form_post(request: Request):
    form_data = await request.form()
    question = form_data.get('question')
    code = form_data.get('code')
    codecheck, usage = CodeCheck(question=question, code=code, llm=gpt3_model)
    runtime = runcode(code)
    print(runtime)
    # Store the output in the session
    # request.session['output'] = codecheck
    return templates.TemplateResponse('form.html', context={'request': request, 'output': codecheck, 'runtime': runtime,
                                                            'usage': usage})
