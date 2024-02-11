from util import search_with_bing
from prompt import (
  _prompt_rag_query_CN,
  _prompt_more_questions_CN
)

from dotenv import load_dotenv
load_dotenv()

from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda,
    RunnableParallel,
    RunnableBranch,
)
from langchain_core.pydantic_v1 import BaseModel
from operator import itemgetter
import json
import re

def get_context_search_bing(query: str):
    contexts = search_with_bing(query)
    context = "\n\n".join(
        [f"[[citation:{i+1}]] {c['snippet']}" for i, c in enumerate(contexts)]
    )
    # print(context)
    return context

question = '为什么月球绕地球公转和自转的周期相等？'
context = get_context_search_bing(question)
# print(context)

_rag_query = PromptTemplate.from_template(_prompt_rag_query_CN)
llm_openai = ChatOpenAI()

class outparser(StrOutputParser):
    def parse(self, output):
        output = re.sub(r'^ +', '', output)
        output = re.sub(r' +$', '', output)
        return output

chain = (
    _rag_query
    | llm_openai
    | outparser
)

out = chain.invoke({"question": question, "context": context})
print(out)

# prompt_string = _rag_query.format(context=context, question=question)
# print(prompt_string)
# out_rag_query = llm_openai.invoke(prompt_string)
# print(out_rag_query.content)


# def parse_list(text: str):
#     out = []
#     arr = text.split("\n")
#     for i in arr:
#         print(i)
#         _i = re.sub(r"\d+\.\s+", "", i)
#         out.append(_i)
#     return out

# print(parse_list("1. 月球的潮汐锁定是如何导致公转和自转周期相等的？\n2. 月球的自转周期和公转周期分别是多少？\n3. 地球和月球之间的引力交互作用如何影响月球的自转和公转周期 ？"))
