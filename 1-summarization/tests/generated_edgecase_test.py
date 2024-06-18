import unittest
from unittest.mock import patch
import json
from pathlib import Path

from compare_arch_test import llm_arch_call, create_llm, get_tokens_from_messages
from src.llm import llm_generate_summary, llm_summarize_summary, create_llm, create_chat_llm, is_prompt_too_big, get_num_tokens
from src.classes import Summary, Configurations
from src.to_html import summary_to_html_enhanced, markdown_to_html, generate_html_from_summary, generate_prompts_html

class TestLLMArchCall(unittest.TestCase):

    @patch('compare_arch_test.create_llm')
    def test_llm_arch_call_token_limit_exceeded(self, mock_create_llm):
        mock_llm = unittest.mock.MagicMock()
        mock_llm.invoke.return_value = "Test output"
        mock_create_llm.return_value = mock_llm

        result = llm_arch_call("test_doc.docx", "test_json.json")
        self.assertEqual(result, "Input exceeds model token limit")

    @patch('compare_arch_test.create_llm')
    def test_llm_arch_call_token_limit_close(self, mock_create_llm):
        mock_llm = unittest.mock.MagicMock()
        mock_llm.invoke.return_value = "Test output"
        mock_create_llm.return_value = mock_llm

        with patch('compare_arch_test.get_tokens_from_messages', return_value=125000):
            result = llm_arch_call("test_doc.docx", "test_json.json") 
            mock_create_llm.assert_called_with(max_tokens=3000)
            self.assertEqual(result, "Test output")

    def test_create_llm_invalid_model(self):
        with patch('compare_arch_test.ChatOpenAI') as mock_chat_open_ai:
            mock_chat_open_ai.side_effect = ValueError("Invalid model")
            with self.assertRaises(ValueError):
                create_llm(max_tokens=100)

    def test_get_tokens_from_messages_empty(self):
        tokens = get_tokens_from_messages([])
        self.assertEqual(tokens, 0)

class TestLLM(unittest.TestCase):

    def test_llm_generate_summary_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            llm_generate_summary(Path("nonexistent_file.py"), "")

    def test_llm_generate_summary_empty_code(self):
        with self.assertRaises(ValueError):
            llm_generate_summary(Path("empty.py"), "")

    @patch('src.llm.create_llm')  
    def test_llm_generate_summary_prompt_too_big(self, mock_create_llm):
        mock_llm = unittest.mock.MagicMock()
        mock_llm.get_num_tokens.return_value = 1000000  # Simulate large prompt
        mock_create_llm.return_value = mock_llm

        summary = llm_generate_summary(Path("large_file.py"), "a" * 1000000)
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)

    def test_llm_summarize_summary_empty_summaries(self):
        with self.assertRaises(ValueError):
            llm_summarize_summary(Path("test"), [])

    def test_create_llm_invalid_model(self):
        with patch('src.llm.OpenAI') as mock_open_ai:
            mock_open_ai.side_effect = ValueError("Invalid model")
            with self.assertRaises(ValueError):
                create_llm(max_tokens=100)

    def test_create_chat_llm_invalid_model(self):
        with patch('src.llm.ChatOpenAI') as mock_chat_open_ai:  
            mock_chat_open_ai.side_effect = ValueError("Invalid model")
            with self.assertRaises(ValueError):
                create_chat_llm(max_tokens=100)

    def test_is_prompt_too_big_no_context_window(self):
        with patch('src.llm.cfg') as mock_cfg:
            mock_cfg.CONTEXT_WINDOW = 0
            self.assertTrue(is_prompt_too_big(None, "test"))

    def test_get_num_tokens_invalid_model(self):
        with patch('src.llm.OpenAI') as mock_open_ai:
            mock_open_ai.side_effect = ValueError("Invalid model")
            with self.assertRaises(ValueError):
                get_num_tokens("test")

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

    def test_markdown_to_html_no_markdown(self):
        text = "This is a plain text."
        self.assertEqual(markdown_to_html(text), text)

    def test_generate_prompts_html_empty_prompts(self):
        prompts = {}
        expected_html = '''    <details class="prompts-details" style="margin-left: 40px;">
      <summary class="summary-title">Prompts Details</summary>
      <ul>
      </ul>
    </details>'''
        self.assertEqual(generate_prompts_html(prompts, 2), expected_html)

    def test_generate_html_from_summary_no_details(self):
        summary = Summary(
            path="test/path",
            summary="This is a test summary.",
            summaries=[],
            details={}
        )
        html = generate_html_from_summary(summary)
        self.assertNotIn('<div class="configuration"', html)

    def test_generate_html_from_summary_empty_summaries(self):
        html = generate_html_from_summary(self.summary)
        self.assertNotIn('<details class="summary-detail"', html)

    def test_summary_to_html_enhanced_empty_summary(self):
        summary = Summary(
            path="",
            summary="",
            summaries=[],
            details={}
        )
        html = summary_to_html_enhanced(summary)
        self.assertIn('<h2 style="margin-left: 0px; color: #333366;">Summary of </h2>', html)
        self.assertNotIn('<div class="configuration"', html)
        self.assertNotIn('<details class="summary-detail"', html)

if __name__ == '__main__':
    unittest.main()

# These tests cover some additional edge cases and potential failure scenarios, such as:

# 1. Handling token limit exceeded and close to limit scenarios in `llm_arch_call`.
# 2. Testing invalid model errors in `create_llm` and `get_tokens_from_messages`.
# 3. Handling file not found and empty code scenarios in `llm_generate_summary`.
# 4. Testing prompt too big scenario in `llm_generate_summary`.
# 5. Handling empty summaries in `llm_summarize_summary`.
# 6. Testing invalid model errors in `create_llm`, `create_chat_llm`, and `get_num_tokens`.
# 7. Handling no context window scenario in `is_prompt_too_big`.
# 8. Testing no markdown text in `markdown_to_html`.
# 9. Handling empty prompts in `generate_prompts_html`.
# 10. Testing summary with no details and empty summaries in `generate_html_from_summary`.
# 11. Handling empty summary in `summary_to_html_enhanced`.

# These tests aim to ensure the robustness of the code by covering various unexpected situations and edge cases.