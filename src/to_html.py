from pathlib import Path
from typing import Dict
from src.classes import Summary, Configurations

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
            html_parts.append(f'<p style="margin-left: {depth * 20}px;"><b>{key}:</b> {value}</p>')
            
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
    # CSS styles for improved design
    style = """
    <style>
      body { font-family: 'Arial', sans-serif; margin: 20px; color: #333; }
      h1 { color: #666; text-align: center; }
      h2, h3 { color: #333; margin-top: 20px; }
      .summary-container { max-width: 800px; margin: 0 auto; }
      .configuration { background-color: #f9f9f9; padding: 15px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
      .details-box { margin-left: 20px; padding-left: 15px; border-left: 2px solid #ccc; }
      .summary-detail, .config-details { margin-top: 20px; }
      .summary-title { font-weight: bold; cursor: pointer; }
      .summaries-list { list-style-type: none; margin: 0; padding: 0; }
      .prompt-list { padding-left: 20px; }
      .prompt-list li { margin-bottom: 5px; }
      .config-details p { margin: 5px 0; }
      details { border-left: 2px solid #ccc; margin-bottom: 10px; }
      summary:focus + * { display: block; }
    </style>
    """

    html_str = '<div class="summary-container">\n'
    html_str += generate_html_from_summary(summary, 0, f"Summary of {summary['path']}")
    html_str += '\n</div>'
    return f"<html><head>{style}</head><body><h1>Summary Report</h1>{html_str}</body></html>"