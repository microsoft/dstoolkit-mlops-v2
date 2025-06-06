import unittest
from unittest.mock import patch, mock_open

from src.invoice_processing.predict_component.predict.data_extraction.prompts.prompt_manager import PromptManager


class TestPromptManager(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open,
           read_data='---\ndescription: Test template\nauthor: Test Author\n---\nHello, {{ name }}!')
    @patch('src.invoice_processing.predict_component.predict.data_extraction.prompts.prompt_manager.FileSystemLoader.get_source')
    def test_get_prompt(self, mock_get_source, mock_file):
        mock_get_source.return_value = ('template content', 'template/path', lambda: True)
        result = PromptManager.get_prompt('test_template', name='World')
        self.assertEqual(result, 'Hello, World!')

    @patch('builtins.open', new_callable=mock_open,
           read_data='---\ndescription: Test template\nauthor: Test Author\n---\nHello, {{ name }}!')
    @patch('src.invoice_processing.predict_component.predict.data_extraction.prompts.prompt_manager.FileSystemLoader.get_source')
    def test_get_prompt_template_error(self, mock_get_source, mock_file):
        mock_get_source.return_value = ('template content', 'template/path', lambda: True)
        with self.assertRaises(ValueError) as context:
            PromptManager.get_prompt('test_template')
        self.assertIn('Error rendering template', str(context.exception))

    @patch('builtins.open', new_callable=mock_open,
           read_data='---\ndescription: Test template\nauthor: Test Author\n---\nHello, {{ name }}!')
    @patch('src.invoice_processing.predict_component.predict.data_extraction.prompts.prompt_manager.FileSystemLoader.get_source')
    def test_get_template_info(self, mock_get_source, mock_file):
        mock_get_source.return_value = ('template content', 'template/path', lambda: True)
        result = PromptManager.get_template_info('test_template')
        expected_result = {
            'name': 'test_template',
            'description': 'Test template',
            'author': 'Test Author',
            'variables': ['name'],
            'frontmatter': {
                'description': 'Test template',
                'author': 'Test Author'
            }
        }
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
