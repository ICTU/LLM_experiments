

def summary_to_markdown(summary: Summary, level: int = 1, is_nested: bool = False) -> str:
    """
    Converts a Summary instance to a markdown formatted string, improving structure and readability.
    Now supports a more tree-like structure for nested summaries with collapsible sections.
    
    :param summary: The Summary instance to convert.
    :param level: The current heading level for markdown formatting.
    :param is_nested: Indicates if the current summary is a nested summary.
    :return: A markdown formatted string.
    """
    markdown_lines = []
    
    # Heading for the summary
    path = summary.get('path', 'Unknown Path')
    if is_nested:
        markdown_lines.append(f"<details><summary>{'#' * level} Path: {path}</summary>\n\n")
    else:
        markdown_lines.append(f"{'#' * level} Path: {path}\n")
    
    # Summary description
    summary_text = summary.get('summary', 'No summary provided.')
    markdown_lines.append(f"*Summary:* {summary_text}\n")
    
    if not is_nested:
        # Details are only included for the primary layer
        markdown_lines.append(f"\n{'#' * (level + 1)} Configuration Details:\n")
        time = summary.get('time', 'Unknown Time')
        max_tokens_chat = summary.get('max_tokens_chat', 'N/A')
        max_tokens_summaries = summary.get('max_tokens_summaries', 'N/A')
        model_name = summary.get('model_name', 'Unknown Model')
        model_chat_name = summary.get('model_chat_name', 'Unknown Chat Model')
        
        markdown_lines.append(f"- **Time Generated:** {time}\n")
        markdown_lines.append(f"- **Max Tokens for Chat:** {max_tokens_chat}\n")
        markdown_lines.append(f"- **Max Tokens for Generating Summaries:** {max_tokens_summaries}\n")
        markdown_lines.append(f"- **Model Used for Summaries:** {model_name}\n")
        markdown_lines.append(f"- **Model Used for Chat:** {model_chat_name}\n")
        
        # Prompts are only included for the primary layer
        prompts = summary.get('prompts', {})
        if prompts:
            markdown_lines.append(f"\n{'#' * (level + 2)}Used Prompts:\n")
            for prompt, response in prompts.items():
                markdown_lines.append(f"- **Prompt:** {prompt}\n  - Response: {response}\n")
    
    # Input Summaries
    summaries = summary.get('summaries', [])
    if summaries:
        markdown_lines.append(f"\n{'#' * (level + 1)} Summaries used as input:\n")
        for nested_summary in summaries:
            markdown_lines.append(summary_to_markdown(nested_summary, level + 2, is_nested=True))
    
    if is_nested:
        markdown_lines.append("\n</details>")  # Close the details tag for nested summaries
    
    return '\n'.join(markdown_lines)