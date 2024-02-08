from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain, MapReduceDocumentsChain, ReduceDocumentsChain, StuffDocumentsChain
from langchain.text_splitter import CharacterTextSplitter
from src.llm import llm
from src.prompt_template import code_summary_prompt



#load API key
load_dotenv()

selected_dir = Path("C:/Users/jeelb/OneDrive - Stichting ICTU/Documenten/Code genAI/quality-time/components/notifier/src/notifier/")

summaries = []

def read_code_as_str(code_filepath):
    code_str = code_filepath.read_text()
    return code_str

for path in Path.iterdir(selected_dir):
    code_str = read_code_as_str(path)
    if code_str == "":
        continue
    prompt = code_summary_prompt(code_str)
    summary = llm(prompt)
    summaries.append(summary)

#select code file



#Initialize model
llm_chat = ChatOpenAI(temperature=0)

#map template
map_template = """"The following is a set of summaries describing a codebase component. 
summaries: {summaries}

Based on the list of summaries, distil a general description of the component
Helpful Answer:
"""

map_prompt = PromptTemplate.from_template(map_template)
map_chain = LLMChain(llm=llm_chat, prompt=map_prompt)

#reduce template
reduce_template = """The following list of summaries delineated by triple backticks describes files and directories forming a codebase component.
    List of Summaries: ```{summaries}```

    Take these summaries and distill them into a final consolidated summary of the component.
    Helpful answer:"""

reduce_prompt = ChatPromptTemplate.from_template(reduce_template)

#run reduce chain
reduce_chain = LLMChain(llm=llm_chat, prompt=reduce_prompt) 

#takes list of summaries and combines into string, passes to llmchain
combine_summaries_chain = StuffDocumentsChain(llm_chain=reduce_chain, document_variable_name="summaries")


#Combines an interatively reduces mapped docs
reduce_documents_chain = ReduceDocumentsChain(
    combine_documents_chain=combine_summaries_chain,
    collapse_documents_chain=combine_summaries_chain,
    token_max = 4000 
)

#combining documents by mapping a chain over them, combining results
map_reduce_chain = MapReduceDocumentsChain(
    llm_chain=map_chain,
    reduce_documents_chain=reduce_documents_chain,
    document_variable_name="summaries",
    return_intermediate_steps=True
)

#split list of summaries in chunks to run in chain
#text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
#    chunk_size=1000, chunk_overlap=0
#    )

#split_summaries = text_splitter.split_text(summaries)

#print reduced summaries
print(map_reduce_chain.run(summaries))
