import os
import asyncio
import aiohttp
import jinja2
from typing import Dict, Any, List, Optional
from .parser import create_parser, BaseSpecParser
from .exceptions import (
    RateLimitExceeded,
    ConfigurationError,
)
from ratelimit import limits, sleep_and_retry
from .auth import OAuth2Handler
from .pagination import PaginationHandler
from .cache import APICache
from .webhook import WebhookHandler
from .mock_server import MockServerGenerator
import re
import markdown2
import logging
from .js_generator import JavaScriptGenerator
from .plugin_manager import plugin_manager
from .throttling import DynamicAPIThrottler
from .error_handler import ErrorHandler


class APIGenerator:
    def __init__(
        self,
        spec_file: str,
        template_dir: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        api_version: Optional[str] = None,
        spec_format: str = "openapi",
        plugins_dir: Optional[str] = None,
    ):
        self.logger = logging.getLogger(__name__)
        self.parser: BaseSpecParser = create_parser(spec_file, spec_format)
        self.api_data: Dict[str, Any] = {}
        self.template_dir = template_dir or os.path.join(
            os.path.dirname(__file__), "templates"
        )
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.template_env.filters["camel_case"] = self.to_camel_case
        self.template_env.filters["snake_case"] = self.to_snake_case
        self.oauth_handler = OAuth2Handler()
        self.pagination_handler = PaginationHandler()
        self.cache = APICache()
        self.webhook_handler = WebhookHandler()
        self.mock_server_generator = MockServerGenerator()
        self.custom_headers = custom_headers or {}
        self.js_generator = JavaScriptGenerator(self.template_dir)
        if plugins_dir:
            plugin_manager.load_plugins(plugins_dir)
        self.throttler = DynamicAPIThrottler(
            initial_rate_limit=5, initial_time_period=1
        )
        self.error_handler = ErrorHandler()

    def generate(self, output_file: str):
        """
        Generate the API client code and write it to the output file.
        """
        try:
            self.api_data = self.parser.parse()
            api_info = self.parser.get_api_info()
            endpoints = self.parser.get_endpoints()
            servers = self.parser.get_servers()
            security_schemes = self.parser.get_security_schemes()
            tags = self.parser.get_tags()
            external_docs = self.parser.get_external_docs()

            template = self.template_env.get_template("client.py.jinja2")
            rendered_code = template.render(
                api_info=api_info,
                endpoints=endpoints,
                servers=servers,
                security_schemes=security_schemes,
                tags=tags,
                external_docs=external_docs,
                parser=self.parser,
                oauth_handler=self.oauth_handler,
                pagination_handler=self.pagination_handler,
                cache=self.cache,
                webhook_handler=self.webhook_handler,
            )

            with open(output_file, "w") as file:
                file.write(rendered_code)

            self.logger.info(f"API client generated successfully: {output_file}")
        except Exception as e:
            self.logger.error(f"Error generating API client: {str(e)}")
            raise ConfigurationError(f"Failed to generate API client: {str(e)}")

    def generate_mock_server(self, output_dir: str):
        """
        Generate a mock server based on the OpenAPI specification.
        """
        try:
            self.mock_server_generator.generate(self.api_data, output_dir)
            self.logger.info(f"Mock server generated successfully: {output_dir}")
        except Exception as e:
            self.logger.error(f"Error generating mock server: {str(e)}")
            raise ConfigurationError(f"Failed to generate mock server: {str(e)}")

    def generate_documentation(self, output_file: str):
        """
        Generate API documentation in Markdown and HTML formats.
        """
        try:
            doc = f"# {self.api_data['info']['title']} v{self.api_data['info']['version']}\n\n"
            doc += f"{self.api_data['info']['description']}\n\n"

            for path, methods in self.api_data["paths"].items():
                for method, details in methods.items():
                    doc += f"## {method.upper()} {path}\n\n"
                    doc += f"{details.get('summary', '')}\n\n"
                    doc += f"{details.get('description', '')}\n\n"

                    if details.get("parameters"):
                        doc += "### Parameters\n\n"
                        for param in details["parameters"]:
                            doc += f"- `{param['name']}` ({param['in']}): {param.get('description', '')}\n"
                        doc += "\n"

                    if "requestBody" in details:
                        doc += "### Request Body\n\n"
                        doc += f"{details['requestBody'].get('description', '')}\n\n"

                    if details.get("responses"):
                        doc += "### Responses\n\n"
                        for status, response in details["responses"].items():
                            doc += f"- `{status}`: {response.get('description', '')}\n"
                        doc += "\n"

            with open(output_file, "w") as f:
                f.write(doc)

            # Convert Markdown to HTML
            html = markdown2.markdown(doc)
            with open(f"{output_file}.html", "w") as f:
                f.write(html)

            self.logger.info(
                f"API documentation generated successfully: {output_file} and {output_file}.html"
            )
        except Exception as e:
            self.logger.error(f"Error generating API documentation: {str(e)}")
            raise ConfigurationError(f"Failed to generate API documentation: {str(e)}")

    @staticmethod
    def to_camel_case(string: str) -> str:
        """Convert a string to camelCase."""
        words = string.split("_")
        return words[0] + "".join(word.capitalize() for word in words[1:])

    @staticmethod
    def to_snake_case(string: str) -> str:
        """Convert a string to snake_case."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()

    @sleep_and_retry
    @limits(calls=5, period=1)  # 5 calls per second
    async def _request(
        self, session: aiohttp.ClientSession, method: str, url: str, **kwargs
    ) -> Any:
        """
        Make an HTTP request with rate limiting, retries, throttling, and error handling.
        """
        headers = kwargs.get("headers", {})
        headers.update(self.custom_headers)
        kwargs["headers"] = headers
        retries = 3
        for attempt in range(retries):
            try:
                self.throttler.throttle(url)
                async with session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    result = await response.json()
                    self.throttler.record_request_result(True)
                    return result
            except Exception as e:
                self.throttler.record_request_result(False)
                context = {"method": method, "url": url, "attempt": attempt + 1}
                try:
                    self.error_handler.handle_error(e, context)
                except RateLimitExceeded:
                    raise
                except Exception as handled_error:
                    if attempt == retries - 1:
                        raise handled_error
                    await asyncio.sleep(2**attempt)  # Exponential backoff

    def generate_endpoint_method(self, endpoint: str, details: Dict[str, Any]) -> str:
        """
        Generate a method for a single API endpoint.
        """
        method, path = endpoint.split(" ")
        method_name = self.to_snake_case(details["operationId"] or path.split("/")[-1])
        params = []
        query_params = []
        path_params = []
        body_param = None

        for param in details["parameters"]:
            param_name = self.to_snake_case(param["name"])
            param_type = self.parser.infer_type(param["schema"])
            default_value = param.get("default", "None")
            if param["in"] == "query":
                query_params.append(f"{param_name}={param_name}")
            elif param["in"] == "path":
                path_params.append(param_name)
            params.append(f"{param_name}: {param_type} = {default_value}")

        if "requestBody" in details:
            body_type = self.parser.get_request_body_type(details["requestBody"])
            body_param = f"data: {body_type}"
            params.append(body_param)

        response_type = self.parser.get_response_type(details["responses"])
        docstring = (
            f'"""\n    {details["summary"]}\n\n    {details["description"]}\n    """'
        )

        method_code = f"""
    async def {method_name}(self, {', '.join(params)}) -> {response_type}:
        {docstring}
        path = f"{path}"
        {''.join(f'.replace("{{{p}}}", str({p}))' for p in path_params)}
        query = {{{', '.join(query_params)}}}
        {'data = self.parser.validate_schema(data, ' + str(details['requestBody']['content']['application/json']['schema']) + ')' if body_param else ''}
        return await self._request("{method.lower()}", path, params=query{',' if body_param else ''} {'json=data' if body_param else ''})
    """
        return method_code

    def generate_sync_client(self, output_file: str):
        """
        Generate a synchronous version of the API client.
        """
        try:
            async_client_code = self.template_env.get_template(
                "client.py.jinja2"
            ).render(
                api_info=self.parser.get_api_info(),
                endpoints=self.parser.get_endpoints(),
                servers=self.parser.get_servers(),
                security_schemes=self.parser.get_security_schemes(),
                tags=self.parser.get_tags(),
                external_docs=self.parser.get_external_docs(),
                parser=self.parser,
                oauth_handler=self.oauth_handler,
                pagination_handler=self.pagination_handler,
                cache=self.cache,
                webhook_handler=self.webhook_handler,
            )

            sync_client_code = self._convert_to_sync(async_client_code)

            with open(output_file, "w") as file:
                file.write(sync_client_code)

            self.logger.info(
                f"Synchronous API client generated successfully: {output_file}"
            )
        except Exception as e:
            self.logger.error(f"Error generating synchronous API client: {str(e)}")
            raise ConfigurationError(
                f"Failed to generate synchronous API client: {str(e)}"
            )

    def _convert_to_sync(self, async_code: str) -> str:
        """
        Convert asynchronous code to synchronous code.
        """
        # Replace async def with def
        sync_code = re.sub(r"async def", "def", async_code)

        # Replace await with synchronous equivalents
        sync_code = re.sub(r"await (.*?)\(", r"\1(", sync_code)

        # Replace aiohttp with requests
        sync_code = sync_code.replace("import aiohttp", "import requests")
        sync_code = sync_code.replace("aiohttp.ClientSession()", "requests.Session()")

        # Replace async with statements
        sync_code = re.sub(r"async with (.*?) as (.*?):", r"with \1 as \2:", sync_code)

        return sync_code

    def generate_js_client(self, output_file: str):
        """
        Generate a JavaScript client based on the API specification.
        """
        try:
            self.js_generator.generate(self.api_data, output_file)
            self.logger.info(
                f"JavaScript API client generated successfully: {output_file}"
            )
        except Exception as e:
            self.logger.error(f"Error generating JavaScript API client: {str(e)}")
            raise ConfigurationError(
                f"Failed to generate JavaScript API client: {str(e)}"
            )

    def execute_plugin(self, plugin_name: str, *args, **kwargs):
        """Execute a plugin by name."""
        return plugin_manager.execute_plugin(plugin_name, *args, **kwargs)

    def list_plugins(self) -> List[str]:
        """List all available plugins."""
        return plugin_manager.list_plugins()
