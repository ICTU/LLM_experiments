from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.chains import SequentialChain
from langchain.prompts import PromptTemplate
from chain_prompts import solutions_prompt, evaluate_prompt, deepen_prompt, rank_prompt

#import api keys for OpenAI en Langsmith
load_dotenv()

llm = ChatOpenAI(
    model="gpt-3.5-turbo-16k",
    temperature=0,
)

def create_chain(llm, prompt:PromptTemplate, output_key:str):
    """initializes a single llm chain"""
    return LLMChain(
        llm=llm,
        prompt=prompt,
        output_key=output_key
    )


def create_seq_chain():
    """initializes a sequence of llm chains"""
    chain1 = create_chain(llm, solutions_prompt(), "solutions")
    chain2 = create_chain(llm, evaluate_prompt(), "review")
    chain3 = create_chain(llm, deepen_prompt(), "deepen_thought_process")
    chain4 = create_chain(llm, rank_prompt(), "ranked_solutions")
    return SequentialChain(
        chains=[chain1, chain2, chain3, chain4],
        input_variables=["input", "perfect_factors"],
        output_variables=["ranked_solutions"],
        verbose=True
    )


seq_steps_chain = create_seq_chain()

print(
        seq_steps_chain(
            {
                "input": "defining a workflow create valid user stories base on use cases for an application",
                "perfect_factors": "- the workflow should have 4 steps - user stories should relate to a singe use case"
            }
    )
)