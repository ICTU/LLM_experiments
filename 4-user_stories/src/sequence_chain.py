from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.chains import SequentialChain
from langchain.prompts import PromptTemplate

from src.chain_prompts import user_story_prompt, criteria_prompt
from src.to_dutch import translate_to_dutch
from src.evaluate import evaluate_prompt_po, evaluate_prompt_dev
from src.output_parser import create_parser_chain

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


def generate_sequence():
    """initializes sequence of llm chains to generate a user stories"""
    chain1 = create_chain(llm, user_story_prompt(), "user_stories")
    chain2 = create_chain(llm, criteria_prompt(), "criteria")
    return SequentialChain(
        chains=[chain1, chain2],
        input_variables=["functional_design", "use_case", "user_stories_list"],
        output_variables=["criteria"],
        verbose=True
    )

def parse_output(fo_summary:str, use_case:str, user_stories_list=list):
    chain = create_parser_chain(llm=llm)
    return chain.invoke({
        "functional_design": fo_summary,
        "use_case": use_case,
        "user_stories_list": user_stories_list}
        )["user_story_json"]

def generate_user_stories(fo_summary:str, use_case:str, no_stories:int, user_stories_list=[]):
    """Generate a list of user stories with acceptance criteria for use_case"""
    print("Generating user stories...")
    seq_chain = generate_sequence()
    while len(user_stories_list) < no_stories:
        user_story = seq_chain.invoke(
            {
                "functional_design": fo_summary,
                "use_case": use_case,
                "user_stories_list": user_stories_list
            }
        )['criteria']
        user_stories_list.append(user_story)
    output_nl = translate_to_dutch(user_stories_list)

    return parse_output(fo_summary=fo_summary, use_case=use_case, user_stories_list=output_nl)

def evaluate_sequence():
    """initializes a simple sequence of llm chains"""
    chain1 = create_chain(llm, evaluate_prompt_po(), "po_comments")
    chain2 = create_chain(llm, evaluate_prompt_dev(), "dev_comments")
    return SequentialChain(
        chains=[chain1, chain2],
        input_variables=["functional_design", "use_case", "user_stories_list"],
        output_variables=["dev_comments"],
        verbose=True
    )

def evaluate_user_stories(fo_summary:str, use_case:str, user_stories_list=dict):
    """Evaluate the list of generated user stories"""
    print("Evaluating user stories...")
    seq_chain = evaluate_sequence()
    return seq_chain.invoke(
            {
                "functional_design": fo_summary,
                "use_case": use_case,
                "user_stories_list": user_stories_list
            }
            )['dev_comments']



