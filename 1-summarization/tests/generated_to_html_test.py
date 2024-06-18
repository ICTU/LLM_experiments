import unittest
from pathlib import Path
from src.classes import Summary, Configurations
from src.to_html import summary_to_html_enhanced, markdown_to_html, generate_html_from_summary, generate_prompts_html

class TestOutputPresentation(unittest.TestCase):

    def setUp(self):
        self.summary = Summary(
            path="test/path",
            summary="This is a **test** summary.",
            summaries=[],
            details=Configurations(
                time="2023-06-08",
                max_base_tokens_code=100,
                max_base_tokens_summaries=200,
                model_type="test_model",
                model_name="Test Model",
                prompts={
                    "prompt1": "Test prompt 1",
                    "prompt2": "Test prompt 2"
                }
            )
        )

    def test_markdown_to_html(self):
        markdown_text = "This is a **bold** text with a\nnew line."
        expected_html = 'This is a <b>bold</b> text with a<br>new line.'
        self.assertEqual(markdown_to_html(markdown_text), expected_html)

    def test_generate_prompts_html(self):
        prompts = {"prompt1": "Test prompt 1", "prompt2": "Test prompt 2"}
        expected_html = '''    <details class="prompts-details" style="margin-left: 40px;">
      <summary class="summary-title">Prompts Details</summary>
      <ul>
        <li><b>prompt1:</b> Test prompt 1</li>
        <li><b>prompt2:</b> Test prompt 2</li>
      </ul>
    </details>'''
        self.assertEqual(generate_prompts_html(prompts, 2), expected_html)

    def test_generate_html_from_summary_top_level(self):
        html = generate_html_from_summary(self.summary)
        self.assertIn('<h2 style="margin-left: 0px; color: #333366;">Summary of test/path</h2>', html)
        self.assertIn('<div class="configuration" style="margin-left: 0px; background-color: #f3f3f3; padding: 10px; border-radius: 8px; margin: 10px 0;">', html)
        self.assertIn('<p style="margin-left: 0px;"><b>path:</b> test/path</p>', html)
        self.assertIn('<p style="margin-left: 0px;"><b>summary:</b> This is a <b>test</b> summary.</p>', html)

    def test_generate_html_from_summary_nested(self):
        nested_summary = Summary(
            path="nested/path",
            summary="This is a nested summary.",
            summaries=[],
            details=Configurations(
                time="2023-06-08",
                max_base_tokens_code=50,
                max_base_tokens_summaries=100,
                model_type="nested_model",
                model_name="Nested Model",
                prompts={}
            )
        )
        self.summary["summaries"].append(nested_summary)

        html = generate_html_from_summary(self.summary)
        self.assertIn('<details class="summary-detail" style="margin-left: 0px;">', html)
        self.assertIn('<h2 style="margin-left: 20px; color: #333366;">Summary of path</h2>', html)
        self.assertIn('<p style="margin-left: 20px;"><b>path:</b> nested/path</p>', html)
        self.assertIn('<p style="margin-left: 20px;"><b>summary:</b> This is a nested summary.</p>', html)

    def test_summary_to_html_enhanced(self):
        html = summary_to_html_enhanced(self.summary)
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('<html lang="en">', html)
        self.assertIn('<h1>Summary Report</h1>', html)
        self.assertIn('<div class="summary-container">', html)
        self.assertIn(generate_html_from_summary(self.summary, 0, f"Summary of {self.summary['path']}"), html)

if __name__ == '__main__':
    unittest.main()


# These tests cover the key functions related to presenting the output as HTML, including:

# 1. `test_markdown_to_html`: Tests the conversion of Markdown syntax to HTML.
# 2. `test_generate_prompts_html`: Tests the generation of HTML for prompts details.
# 3. `test_generate_html_from_summary_top_level`: Tests the generation of HTML for a top-level summary.
# 4. `test_generate_html_from_summary_nested`: Tests the generation of HTML for a nested summary.
# 5. `test_summary_to_html_enhanced`: Tests the overall generation of the enhanced HTML structure for the summary report.

# The tests use a sample `Summary` object and verify that the generated HTML contains the expected elements and content. They also test edge cases like nested summaries and the conversion of Markdown to HTML.