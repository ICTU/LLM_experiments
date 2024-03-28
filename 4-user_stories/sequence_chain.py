from dotenv import load_dotenv
import pprint
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.chains import SequentialChain
from langchain.prompts import PromptTemplate

from src.chain_prompts import user_story_prompt, criteria_prompt, evaluate_prompt
from docs.doc_summaries import fo_summary_inkoop
from docs.use_cases import use_cases_inkoop
from src.to_dutch import translate_to_dutch
from src.evaluate import evaluate_user_stories

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


def simple_seq():
    """initializes a simple sequence of llm chains"""
    chain1 = create_chain(llm, user_story_prompt(), "user_stories")
    chain2 = create_chain(llm, criteria_prompt(), "criteria")
    return SequentialChain(
        chains=[chain1, chain2],
        input_variables=["functional_design", "use_case", "user_stories_list"],
        output_variables=["criteria"],
        verbose=True
    )


def generate_user_stories(fo_summary:str, use_case:str, no_stories:int, user_stories_list=[]):
    """Generate a list of user stories with acceptance criteria for use_case"""
    print("Generating user stories...")
    seq_chain = simple_seq()
    while len(user_stories_list) < no_stories:
        user_stories_list.append(seq_chain.invoke(
            {
                "functional_design": fo_summary,
                "use_case": use_case,
                "user_stories_list": user_stories_list
            }
        )['criteria'])
    #evaluate user stories list
    print("Evaluating user stories...")
    evaluate_user_stories(input=user_stories_list, fo_summary=fo_summary, use_case=use_case)

    #translate user stories to dutch
    print("Translating user stories...")
    return translate_to_dutch(user_stories_list)