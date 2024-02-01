import json
from dotenv import load_dotenv
import yaml
import box
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain

#loading data from JSON file
with open ("metrics/example-metrics.json") as read_file:
    data = json.load(read_file)

summaries_list = []

for item in data[ "experiment1_summarization"]:
    if item["component"] == "notifier":
        summaries_list.append(item["summary"])
    else:
        continue

print(summaries_list)

#load API key from .env
load_dotenv()

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = box.Box(yaml.safe_load(ymlfile))

#initalize OpenAI model
llm = ChatOpenAI(model=cfg.MODEL_NAME, temperature=cfg.TEMPERATURE, max_tokens=cfg.MAX_TOKENS)

chain = load_summarize_chain(llm=llm, chain_type="refine", verbose=True)

#run llm chain
chain.run(summaries_list)

