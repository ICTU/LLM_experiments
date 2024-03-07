import re
from pathlib import Path
from typing import Dict
from src.classes import Summary, Configurations

def write_to_html_file(html_content, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:  # Specify encoding here
        file.write(html_content)

def markdown_to_html(text: str) -> str:
    # Converts markdown line breaks to <br>
    html_text = text.replace('\n', '<br>')
    
    # Converts markdown bold syntax to HTML <b> tags; matches **text**
    html_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html_text)
    
    return html_text

def generate_html_from_configurations(config: Configurations, depth: int) -> str:
    html_parts = []
    html_parts.append(f'<details class="config-details" style="margin-left: {depth*20}px;">')
    html_parts.append(f'<summary class="summary-title">Configuration Details</summary>')
    for key, value in config.items():
        if key == 'prompts':
            html_parts.append(generate_prompts_html(value, depth+1))
        else:
            html_parts.append(f'<p style="margin-left: {depth*20}px;"><b>{key}:</b> {value}</p>')
    html_parts.append('</details>')
    return '\n'.join(html_parts)

def generate_html_from_summary(summary: Summary, depth: int = 0, header: str = "") -> str:
    html_parts = []
    configKeys = ['prompts', 'time', 'max_base_tokens_code', 'max_base_tokens_summaries', 'model_type', 'model_name']

    # Adding header if provided
    if header:
        html_parts.append(f'<h2 style="margin-left: {depth * 20}px; color: #333366;">{header}</h2>')
    
    # Configuration section
    if depth == 0:  # Only at the top level
        html_parts.append(f'<div class="configuration" style="margin-left: {depth * 20}px; background-color: #f3f3f3; padding: 10px; border-radius: 8px; margin: 10px 0;">')
        html_parts.append(f'  <h3 style="color: #666699;">Configurations</h3>')
    
        for key in configKeys:
            if key == 'prompts' and key in summary['details']:  # special handling for prompts as collapsible section
                html_parts.append(generate_prompts_html(summary['details']['prompts'], depth + 2))
            elif key != 'prompts':
                html_parts.append(f'    <p style="margin-left: {20}px;"><b>{key}:</b> {summary["details"][key]}</p>')

        html_parts.append(f'</div>')
    
    # Handling other keys outside of the configuration
    for key, value in summary.items():
        if key not in configKeys and key != 'summaries' and key != 'details':
            # Apply markdown_to_html function to convert value if it's a string
            formatted_value = markdown_to_html(value) if isinstance(value, str) else value
            html_parts.append(f'<p style="margin-left: {depth * 20}px;"><b>{key}:</b> {formatted_value}</p>')

    # for key, value in summary.items():
    #     if key not in configKeys and key != 'summaries' and key != 'details':
    #         html_parts.append(f'<p style="margin-left: {depth * 20}px;"><b>{key}:</b> {value}</p>')
            
    # For nested summaries
    if 'summaries' in summary and summary['summaries']:
        html_parts.append(f'<details class="summary-detail" style="margin-left: {depth*20}px;">')
        html_parts.append(f'  <summary class="summary-title" style="font-weight: bold; cursor: pointer;">Summaries used as input</summary>')
        
        for sub_summary in summary['summaries']:
            html_parts.append(generate_html_from_summary(sub_summary, depth + 1, f"Summary of {Path(sub_summary['path']).name}"))
        
        html_parts.append(f'</details>')
    
    return '\n'.join(html_parts)

def generate_prompts_html(prompts: Dict[str, str], depth: int) -> str:
    html_parts = []
    html_parts.append(f'    <details class="prompts-details" style="margin-left: {depth*20}px;">')
    html_parts.append(f'      <summary class="summary-title">Prompts Details</summary>')
    html_parts.append(f'      <ul>')
    for prompt_key, prompt_value in prompts.items():
        html_parts.append(f'        <li><b>{prompt_key}:</b> {prompt_value}</li>')
    html_parts.append(f'      </ul>')
    html_parts.append(f'    </details>')
    return '\n'.join(html_parts)

def summary_to_html_enhanced(summary: Summary) -> str:
    # Updated CSS styles for design alignment
    style = """
    <style>
      body {
        font-family: 'Arial', sans-serif;
        margin: 0;
        padding: 20px;
        color: #333;
        background-color: #f5f5f5;
      }
      h1 {
        color: #444;
        text-align: center;
        margin-bottom: 40px;
      }
      h2 {
        color: #555;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
      }
      h3 {
        color: #666;
      }
      .summary-container {
        max-width: 960px;
        margin: 0 auto;
        background-color: #fff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }
      .configuration {
        background-color: #fafafa;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
      }
      .summary-detail, .config-details {
        margin-top: 20px;
      }
      .summary-title {
        font-weight: bold;
        cursor: pointer;
        display: block;
        padding: 10px;
        background-color: #eee;
        border-radius: 5px;
        transition: background-color 0.3s;
      }
      .summary-title:hover {
        background-color: #ddd;
      }
      details {
        border-left: 2px solid #ccc;
        padding-left: 10px;
        margin-bottom: 10px;
        margin-top: 10px;
      }
      summary {
        outline: none;
      }
      summary::-webkit-details-marker {
        display: none
      }
      summary:before {
        content: '➤';
        margin-right: 5px;
        font-size: 0.9em;
      }
      details[open] summary:before {
        content: '▼';
      }
      .prompt-list, .summaries-list {
        padding-left: 20px;
      }
      .prompt-list li, .config-details p {
        margin-bottom: 5px;
      }
      p {
        line-height: 1.6;
      }
    </style>
    """

        # HTML structure with UTF-8 Charset Declaration
    html_structure = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Summary Report</title>
    {style}
    </head>
    <body>
    <h1>Summary Report</h1>
    <div class="summary-container">
    """

    html_str = generate_html_from_summary(summary, 0, f"Summary of {summary['path']}")
    html_structure += html_str
    html_structure += '\n</div></body></html>'
    
    return html_structure




