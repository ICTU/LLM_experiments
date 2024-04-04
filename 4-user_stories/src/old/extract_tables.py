import fitz #PyMuPDF
import pandas as pd
import logging
from pathlib import Path
from summarize_docs import write_to_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def reformat_df_for_llm(dataframe:pd.DataFrame, use_case_id:int):
    """Writes info from a pandas dataframe to a file in a structured key-value pair format"""
    output_file = Path(f"use_cases/use_case{use_case_id}.txt")
    output_file.parent.mkdir(parents=True, exist_ok=True) #ensure directory exists otherwise create

    with output_file.open("w") as f:
        for index, row in dataframe.iterrows():
            row_str = ""
            for column in dataframe.columns:
                row_str += f"{column}: {row[column]},"
            f.write(row_str + "\n")
            logging.info(f"Use case {use_case_id} saved to {output_file}.")

    return write_to_file(text=dataframe, file_path=output_file)

def extract_use_cases_from_pdf(path:Path):
    """Extract use case info from tables in pdf to key-value pairs in txt doc"""
    try:
        doc = fitz.open(path)
    except Exception as e:
        logging.error(f"Failed to open PDF: {e}")
        return

    counter = 0
    for page in doc:
        tables = page.find_tables()
        for tab in tables:
            if 'Apsect' and 'Beschrijving' in tab.header.names:
                counter += 1
                df = tab.to_pandas()
                reformat_df_for_llm(dataframe=df, use_case_id=counter)
    return logging.info(f"Total use cases extracted from {path}: {counter}")


extract_use_cases_from_pdf(path="../docs/Globaal-Functioneel-Ontwerp InkoopDB.pdf")