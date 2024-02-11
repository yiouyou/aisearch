from dotenv import load_dotenv
load_dotenv()

from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda,
    RunnableParallel,
    RunnableBranch,
)
from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from operator import itemgetter
import json
import re

from .util import (
    get_context_search_bing,
    parse_list
)
from .prompt import (
  _prompt_rag_query_EN,
  _prompt_rag_query_CN,
  _prompt_more_questions_CN
)

from loguru import logger
logger.add("1_week.log", rotation="1 week")


class outparser(StrOutputParser):
    def parse(self, output):
        output = re.sub(r'^ +', '', output)
        output = re.sub(r' +$', '', output)
        return output


def ai_search(_dict):
    question = _dict["question"]
    context, sources = get_context_search_bing(question)
    # logger.info(f"{type(_dict)}: {_dict}")
    # logger.info(type(context))
    ### llm
    # llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
    llm = ChatMistralAI(model="mistral-medium")
    ### rag_query
    _rq = PromptTemplate.from_template(_prompt_rag_query_CN)
    prompt_rq = _rq.format(context=context, question=question)
    print(prompt_rq)
    out_rq = llm.invoke(prompt_rq).content
    print(out_rq)
    # logger.info(prompt_rq)
    # logger.info(out_rq)
    # ### more_questions
    _mq = PromptTemplate.from_template(_prompt_more_questions_CN)
    prompt_mq = _mq.format(context=context, question=question)
    out_mq = llm.invoke(prompt_mq).content
    # logger.info(prompt_mq)
    # logger.info(out_mq)
    ### out
    out = {
        "answer": out_rq,
        "relates": parse_list(out_mq),
        "sources": sources
    }
    out_string = json.dumps(out, ensure_ascii=False)
    # logger.info(out_string)
    return out_string


def ai_search1(_dict):
    question = _dict["question"]
    context, sources = get_context_search_bing(question)
    # logger.info(f"{type(_dict)}: {_dict}")
    # logger.info(type(context))
    llm = ChatOpenAI()
    ### rag_query
    _rq = PromptTemplate.from_template(_prompt_rag_query_CN)
    chain_rq = (
        _rq
        | llm
        | outparser
    )
    out_rq = chain_rq.invoke({"question": question, "context": context}).content
    # logger.info(out_rq)
    # ### more_questions
    _mq = PromptTemplate.from_template(_prompt_more_questions_CN)
    prompt_mq = _mq.format(context=context, question=question)
    chain_mq = (
        _mq
        | llm
        | outparser
    )
    out_mq = chain_mq.invoke({"question": question, "context": context}).content
    # logger.info(out_mq)
    ### out
    out = {
        "answer": out_rq,
        "relates": parse_list(out_mq),
        "sources": sources
    }
    out_string = json.dumps(out, ensure_ascii=False)
    # logger.info(out_string)
    return out_string


chain = (
    RunnableLambda(ai_search)
)

chain1 = (
    RunnableLambda(ai_search1)
)

# '为什么月球绕地球公转和自转的周期相等？',
# '地球对月球的引力有什么影响？'

class Input(BaseModel):
    question: str = '为什么月球绕地球公转和自转的周期相等？'

class Input1(BaseModel):
    question: str = '为什么月球绕地球公转和自转的周期相等？'
    context: str = 'context'

chain = chain.with_types(input_type=Input)
# chain = chain1.with_types(input_type=Input1)

