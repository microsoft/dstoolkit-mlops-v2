import base64
import unittest
from unittest.mock import patch, mock_open
import json

from src.invoice_processing.predict_component.predict.helpers import save_output_as_json, convert_image_to_base64


class TestPredictOrchestratorHelpers(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    def test_save_output_as_json(self, mock_file):
        output = {"key": "value"}
        output_file_path = "test_output.json"

        save_output_as_json(output, output_file_path)

        mock_file.assert_called_once_with(output_file_path, 'w', encoding='utf-8')
        handle = mock_file()
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        self.assertEqual(written_content, json.dumps(output, ensure_ascii=False, indent=4))

    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
    def test_convert_image_to_base64(self, mock_file):
        image_path = "test_image.png"

        result = convert_image_to_base64(image_path)

        mock_file.assert_called_once_with(image_path, "rb")
        self.assertEqual(result, base64.b64encode(b"fake_image_data").decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
