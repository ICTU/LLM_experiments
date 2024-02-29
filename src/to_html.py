from pathlib import Path

def summary_to_html_enhanced(summary: dict) -> str:
    """Converts an instance of the Summary class to an html format"""
    def generate_html_from_summary(summary: dict, depth: int = 0, header: str = "") -> str:
        html_parts = []
        configKeys = ['prompts', 'time', 'max_tokens_chat', 'max_tokens_summaries', 'model_name', 'model_chat_name']

        # Adding header if provided
        if header:
            html_parts.append(f'<h2 style="margin-left: {depth*20}px;">{header}</h2>')
        
        # Configuration section
        if depth == 0:  # Only at the top level
            html_parts.append(f'<div class="configuration" style="margin-left: {depth*20}px;">')
            html_parts.append(f'  <h3>Configuration</h3>')
            for key in configKeys:
                if key == 'prompts' and key in summary:  # special handling for prompts as a numbered list
                    html_parts.append(f'    <p><b>{key}:</b></p>')
                    html_parts.append(f'    <ol>')
                    for item in summary[key]:
                        html_parts.append(f'      <li>{item}</li>')
                    html_parts.append(f'    </ol>')
                elif key in summary:
                    html_parts.append(f'    <p><b>{key}:</b> {summary[key]}</p>')                    
            html_parts.append(f'</div>')
        
        # Handling other keys outside of the configuration
        for key, value in summary.items():
            if key not in configKeys and key != 'summaries':
                html_parts.append(f'<p style="margin-left: {depth*20}px;"><b>{key}:</b> {value}</p>')
                
        # For nested summaries
        if 'summaries' in summary and summary['summaries']:
            for sub_summary in summary['summaries']:
                html_parts.append(f'<details class="summary-detail" style="margin-left: {depth*20}px;">')
                html_parts.append(f'  <summary class="summary-title">Summaries used as input</summary>')
                html_parts.append(generate_html_from_summary(sub_summary, depth+1, f"Summary of {Path(sub_summary['path']).name}"))
                html_parts.append(f'</details>')
        
        return '\n'.join(html_parts)
    
    # Adding a simple CSS style for better visualization
    style = """
    <style>
      div.summary-container { font-family: Arial, sans-serif; margin: 20px; }
      .configuration { background-color: #f3f3f3; padding: 10px; border-radius: 8px; margin: 10px 0; }
      p, ol { margin: 5px 0; }
      h2, h3 { margin: 10px 0; }
      h2 { color: #333366; }
      h3 { color: #666699; }
      details.summary-detail { margin-top: 10px; }
      summary.summary-title { font-weight: bold; cursor: pointer; }
    </style>
    """
    
    # Path usage in the original scope might require importing Path or adjustment
    html_str = '<div class="summary-container">\n'
    html_str += generate_html_from_summary(summary, 0, f"Summary of {summary['path']}")
    html_str += '\n</div>'
    return style + html_str


# def summary_to_markdown(summary: Summary, level: int = 1, is_nested: bool = False) -> str:
#     """
#     Converts a Summary instance to a markdown formatted string, improving structure and readability.
#     Now supports a more tree-like structure for nested summaries with collapsible sections.
    
#     :param summary: The Summary instance to convert.
#     :param level: The current heading level for markdown formatting.
#     :param is_nested: Indicates if the current summary is a nested summary.
#     :return: A markdown formatted string.
#     """
#     markdown_lines = []
    
#     # Heading for the summary
#     path = summary.get('path', 'Unknown Path')
#     if is_nested:
#         markdown_lines.append(f"<details><summary>{'#' * level} Path: {path}</summary>\n\n")
#     else:
#         markdown_lines.append(f"{'#' * level} Path: {path}\n")
    
#     # Summary description
#     summary_text = summary.get('summary', 'No summary provided.')
#     markdown_lines.append(f"*Summary:* {summary_text}\n")
    
#     if not is_nested:
#         # Details are only included for the primary layer
#         markdown_lines.append(f"\n{'#' * (level)} Configuration Details:\n")
#         time = summary.get('time', 'Unknown Time')
#         max_tokens_chat = summary.get('max_tokens_chat', 'N/A')
#         max_tokens_summaries = summary.get('max_tokens_summaries', 'N/A')
#         model_name = summary.get('model_name', 'Unknown Model')
#         model_chat_name = summary.get('model_chat_name', 'Unknown Chat Model')
        
#         markdown_lines.append(f"- **Time Generated:** {time}\n")
#         markdown_lines.append(f"- **Max Tokens for Chat:** {max_tokens_chat}\n")
#         markdown_lines.append(f"- **Max Tokens for Generating Summaries:** {max_tokens_summaries}\n")
#         markdown_lines.append(f"- **Model Used for Summaries:** {model_name}\n")
#         markdown_lines.append(f"- **Model Used for Chat:** {model_chat_name}\n")
        
#         # Prompts are only included for the primary layer
#         prompts = summary.get('prompts', {})
#         if prompts:
#             markdown_lines.append(f"\n{'#' * (level + 1)} Used Prompts:\n")
#             for prompt, response in prompts.items():
#                 markdown_lines.append(f"- **Prompt:** {prompt}\n  - Response: {response}\n")
    
#     # Input Summaries
#     summaries = summary.get('summaries', [])
#     if summaries:
#         markdown_lines.append(f"\n{'#' * (level)} Summaries used as input:\n")
#         for nested_summary in summaries:
#             markdown_lines.append(summary_to_markdown(nested_summary, level + 1, is_nested=True))
    
#     if is_nested:
#         markdown_lines.append("\n</details>")  # Close the details tag for nested summaries
    
#     return '\n'.join(markdown_lines)
