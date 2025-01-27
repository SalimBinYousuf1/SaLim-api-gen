# SaLim-api-gen

SaLim-api-gen is a versatile Python library for generating API wrappers, documentation, and mock servers based on OpenAPI/Swagger and RAML specifications. It's designed to streamline API-related tasks in your development workflow, making it easier for developers of all levels to work with various APIs.

## Features

- Generate asynchronous and synchronous API client wrappers in Python and JavaScript
- Create comprehensive API documentation in Markdown and HTML formats
- Generate mock servers for testing and development
- Support for API versioning
- Interactive CLI for easy usage
- Customizable code generation through Jinja2 templates
- Robust error handling and logging
- Rate limiting and caching support
- OAuth2 authentication handling
- Pagination support
- Webhook support
- Comprehensive unit testing
- Continuous Integration (CI) setup
- Plugin system for easy extensibility
- Dynamic API throttling to optimize request rates
- Advanced error handling with custom error callbacks
- Command-line interface for API testing

## Installation

Install SaLim-api-gen using pip:

\`\`\`bash
pip install salim-api-gen
\`\`\`

## API Throttling

SaLim-api-gen includes a dynamic API throttling feature that automatically adjusts the request rate based on the success rate of API calls. This helps to optimize performance while avoiding rate limit errors.

## Advanced Error Handling

The library now includes an advanced error handling system that allows you to register custom error callbacks for different types of errors. This enables you to implement custom logic for handling specific error scenarios.

Example:

\`\`\`python
from salim_api_gen import APIGenerator, ErrorHandler

def custom_rate_limit_handler(error, context):
    print(f"Rate limit exceeded. Context: {context}")
    # Implement custom logic here

generator = APIGenerator("path/to/openapi.yaml")
generator.error_handler.register_error_callback("RateLimitExceeded", custom_rate_limit_handler)
\`\`\`

## API Testing CLI

SaLim-api-gen now includes a command-line interface for testing API endpoints. You can use this feature to quickly test endpoints without writing additional code.

Usage:

\`\`\`bash
salim-api-gen test-api --spec path/to/openapi.yaml --endpoint /users --method GET --output response.json
\`\`\`

This command will generate a temporary API client, make a request to the specified endpoint, and save the response to a JSON file.

