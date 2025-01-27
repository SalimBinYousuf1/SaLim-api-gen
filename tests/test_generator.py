import unittest
from unittest.mock import patch
import os
import tempfile
from salim_api_gen import APIGenerator
from salim_api_gen.exceptions import ConfigurationError


class TestAPIGenerator(unittest.TestCase):
    def setUp(self):
        self.spec_file = "test_spec.yaml"
        self.output_file = "test_output.py"
        self.api_generator = APIGenerator(self.spec_file)

    @patch("salim_api_gen.generator.OpenAPIParser")
    def test_generate(self, mock_parser):
        mock_parser.return_value.parse.return_value = {
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/test": {"get": {"summary": "Test endpoint"}}},
        }
        mock_parser.return_value.get_api_info.return_value = {
            "title": "Test API",
            "version": "1.0.0",
        }
        mock_parser.return_value.get_endpoints.return_value = {
            "GET /test": {"summary": "Test endpoint"}
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, self.output_file)
            self.api_generator.generate(output_file)
            self.assertTrue(os.path.exists(output_file))

    @patch("salim_api_gen.generator.OpenAPIParser")
    def test_generate_mock_server(self, mock_parser):
        mock_parser.return_value.parse.return_value = {
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/test": {"get": {"summary": "Test endpoint"}}},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.api_generator.generate_mock_server(tmpdir)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "mock_server.py")))

    @patch("salim_api_gen.generator.OpenAPIParser")
    def test_generate_documentation(self, mock_parser):
        mock_parser.return_value.parse.return_value = {
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "Test description",
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "description": "Test description",
                    }
                }
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "api_docs.md")
            self.api_generator.generate_documentation(output_file)
            self.assertTrue(os.path.exists(output_file))
            self.assertTrue(os.path.exists(output_file + ".html"))

    @patch("salim_api_gen.generator.OpenAPIParser")
    def test_generate_sync_client(self, mock_parser):
        mock_parser.return_value.parse.return_value = {
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/test": {"get": {"summary": "Test endpoint"}}},
        }
        mock_parser.return_value.get_api_info.return_value = {
            "title": "Test API",
            "version": "1.0.0",
        }
        mock_parser.return_value.get_endpoints.return_value = {
            "GET /test": {"summary": "Test endpoint"}
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "sync_client.py")
            self.api_generator.generate_sync_client(output_file)
            self.assertTrue(os.path.exists(output_file))

    def test_invalid_spec_file(self):
        with self.assertRaises(FileNotFoundError):
            APIGenerator("nonexistent_file.yaml")

    @patch("salim_api_gen.generator.OpenAPIParser")
    def test_configuration_error(self, mock_parser):
        mock_parser.return_value.parse.side_effect = ValueError("Invalid specification")

        with self.assertRaises(ConfigurationError):
            self.api_generator.generate(self.output_file)


if __name__ == "__main__":
    unittest.main()
