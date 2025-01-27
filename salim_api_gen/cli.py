import argparse
import logging
import os
from typing import List, Dict, Any
from .generator import APIGenerator
from .utils import ensure_directory
from .exceptions import SalimAPIGenException
import inquirer
from .plugin_manager import plugin_manager
from .api_tester import test_api


def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate API wrappers, documentation, and mock servers from OpenAPI/Swagger specifications"
    )
    parser.add_argument(
        "--input", "-i", help="Input OpenAPI specification file or directory"
    )
    parser.add_argument(
        "--output", "-o", help="Output file or directory for generated API wrapper(s)"
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Recursively process all OpenAPI files in the input directory",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--template", "-t", help="Custom Jinja2 template file for code generation"
    )
    parser.add_argument(
        "--mock-server", "-m", action="store_true", help="Generate a mock server"
    )
    parser.add_argument(
        "--interactive", "-int", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--docs", "-d", action="store_true", help="Generate API documentation"
    )
    parser.add_argument(
        "--sync", "-s", action="store_true", help="Generate synchronous API client"
    )
    parser.add_argument("--version", "-ver", help="Specify API version to generate")
    parser.add_argument(
        "--js", action="store_true", help="Generate JavaScript API client"
    )
    parser.add_argument(
        "--spec-format",
        choices=["openapi", "raml"],
        default="openapi",
        help="Specification format (default: openapi)",
    )
    parser.add_argument("--plugins-dir", help="Directory containing plugins")
    parser.add_argument("--execute-plugin", help="Execute a specific plugin")
    parser.add_argument(
        "--list-plugins", action="store_true", help="List available plugins"
    )
    return parser.parse_args()


def interactive_mode() -> Dict[str, Any]:
    questions = [
        inquirer.Text(
            "input",
            message="Enter the path to the OpenAPI specification file or directory",
        ),
        inquirer.Text(
            "output",
            message="Enter the output file or directory for generated API wrapper(s)",
        ),
        inquirer.Confirm(
            "recursive", message="Process all OpenAPI files recursively?", default=False
        ),
        inquirer.Confirm(
            "mock_server", message="Generate a mock server?", default=False
        ),
        inquirer.Confirm("docs", message="Generate API documentation?", default=False),
        inquirer.Confirm(
            "sync", message="Generate synchronous API client?", default=False
        ),
        inquirer.Text(
            "template",
            message="Enter the path to a custom Jinja2 template file (optional)",
        ),
        inquirer.Text(
            "version", message="Enter the API version to generate (optional)"
        ),
        inquirer.Confirm(
            "js", message="Generate JavaScript API client?", default=False
        ),
        inquirer.List(
            "spec_format",
            message="Select the specification format",
            choices=["openapi", "raml"],
            default="openapi",
        ),
        inquirer.Text(
            "plugins_dir", message="Enter the path to the plugins directory (optional)"
        ),
        inquirer.Text(
            "execute_plugin",
            message="Enter the name of the plugin to execute (optional)",
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers


def generate_wrapper(
    input_file: str,
    output_file: str,
    template_file: str = None,
    generate_mock: bool = False,
    generate_docs: bool = False,
    generate_sync: bool = False,
    generate_js: bool = False,
    api_version: str = None,
    spec_format: str = "openapi",
    plugins_dir: str = None,
    execute_plugin: str = None,
):
    logging.info(f"Generating API wrapper for {input_file}")
    ensure_directory(output_file)
    try:
        generator = APIGenerator(
            input_file,
            template_file,
            api_version=api_version,
            spec_format=spec_format,
            plugins_dir=plugins_dir,
        )
        generator.generate(output_file)
        logging.info(f"API wrapper generated: {output_file}")

        if generate_mock:
            mock_output_dir = os.path.join(os.path.dirname(output_file), "mock_server")
            generator.generate_mock_server(mock_output_dir)
            logging.info(f"Mock server generated: {mock_output_dir}")

        if generate_docs:
            docs_output_file = os.path.join(
                os.path.dirname(output_file), "api_documentation.md"
            )
            generator.generate_documentation(docs_output_file)
            logging.info(f"API documentation generated: {docs_output_file}")

        if generate_sync:
            sync_output_file = os.path.join(
                os.path.dirname(output_file), "sync_client.py"
            )
            generator.generate_sync_client(sync_output_file)
            logging.info(f"Synchronous API client generated: {sync_output_file}")

        if generate_js:
            js_output_file = os.path.join(os.path.dirname(output_file), "js_client.js")
            generator.generate_js_client(js_output_file)
            logging.info(f"JavaScript API client generated: {js_output_file}")

        if execute_plugin:
            plugin_result = generator.execute_plugin(execute_plugin, output_file)
            logging.info(f"Plugin '{execute_plugin}' executed: {plugin_result}")

    except SalimAPIGenException as e:
        logging.error(f"Error generating API wrapper for {input_file}: {str(e)}")
    except Exception as e:
        logging.exception(
            f"Unexpected error generating API wrapper for {input_file}: {str(e)}"
        )


def process_input(
    input_path: str,
    output_path: str,
    recursive: bool,
    template_file: str = None,
    generate_mock: bool = False,
    generate_docs: bool = False,
    generate_sync: bool = False,
    generate_js: bool = False,
    api_version: str = None,
    spec_format: str = "openapi",
    plugins_dir: str = None,
    execute_plugin: str = None,
) -> List[str]:
    processed_files = []
    if os.path.isfile(input_path):
        output_file = (
            output_path
            if not os.path.isdir(output_path)
            else os.path.join(
                output_path, os.path.basename(input_path).rsplit(".", 1)[0] + ".py"
            )
        )
        generate_wrapper(
            input_path,
            output_file,
            template_file,
            generate_mock,
            generate_docs,
            generate_sync,
            generate_js,
            api_version,
            spec_format,
            plugins_dir,
            execute_plugin,
        )
        processed_files.append(output_file)
    elif os.path.isdir(input_path):
        if recursive:
            for root, _, files in os.walk(input_path):
                for file in files:
                    if file.endswith((".json", ".yaml", ".yml")):
                        input_file = os.path.join(root, file)
                        rel_path = os.path.relpath(input_file, input_path)
                        output_file = os.path.join(
                            output_path, os.path.splitext(rel_path)[0] + ".py"
                        )
                        generate_wrapper(
                            input_file,
                            output_file,
                            template_file,
                            generate_mock,
                            generate_docs,
                            generate_sync,
                            generate_js,
                            api_version,
                            spec_format,
                            plugins_dir,
                            execute_plugin,
                        )
                        processed_files.append(output_file)
        else:
            for file in os.listdir(input_path):
                if file.endswith((".json", ".yaml", ".yml")):
                    input_file = os.path.join(input_path, file)
                    output_file = os.path.join(
                        output_path, os.path.splitext(file)[0] + ".py"
                    )
                    generate_wrapper(
                        input_file,
                        output_file,
                        template_file,
                        generate_mock,
                        generate_docs,
                        generate_sync,
                        generate_js,
                        api_version,
                        spec_format,
                        plugins_dir,
                        execute_plugin,
                    )
                    processed_files.append(output_file)
    else:
        logging.error(f"Invalid input path: {input_path}")
    return processed_files


def main():
    args = parse_arguments()
    setup_logging(args.verbose)

    if args.interactive:
        answers = interactive_mode()
        args.input = answers["input"]
        args.output = answers["output"]
        args.recursive = answers["recursive"]
        args.mock_server = answers["mock_server"]
        args.docs = answers["docs"]
        args.sync = answers["sync"]
        args.template = answers["template"] if answers["template"] else None
        args.version = answers["version"] if answers["version"] else None
        args.js = answers["js"]
        args.spec_format = answers["spec_format"]
        args.plugins_dir = answers["plugins_dir"]
        args.execute_plugin = answers["execute_plugin"]

    if args.list_plugins:
        if args.plugins_dir:
            plugin_manager.load_plugins(args.plugins_dir)
            plugins = plugin_manager.list_plugins()
            print("Available plugins:")
            for plugin in plugins:
                print(f"- {plugin}")
        else:
            print("Please specify a plugins directory using --plugins-dir")
        return

    if not args.input or not args.output:
        logging.error(
            "Input and output paths are required. Use --help for usage information."
        )
        return

    processed_files = process_input(
        args.input,
        args.output,
        args.recursive,
        args.template,
        args.mock_server,
        args.docs,
        args.sync,
        args.js,
        args.version,
        args.spec_format,
        args.plugins_dir,
        args.execute_plugin,
    )

    if processed_files:
        logging.info(f"Successfully processed {len(processed_files)} file(s)")
    else:
        logging.warning("No files were processed")

    import click

    cli = click.CommandCollection(sources=[test_api])
    cli.add_command(test_api)


if __name__ == "__main__":
    main()
