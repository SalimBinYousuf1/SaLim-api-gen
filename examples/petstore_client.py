from salim_api_gen import APIGenerator


def main():
    # Generate API client
    generator = APIGenerator("petstore_openapi.yaml")
    generator.generate("petstore_client.py")

    # Generate documentation
    generator.generate_documentation("petstore_docs.md")

    # Generate mock server
    generator.generate_mock_server("petstore_mock_server")

    # Generate synchronous client
    generator.generate_sync_client("petstore_sync_client.py")

    print(
        "Petstore API client, documentation, mock server, and sync client generated successfully!"
    )


if __name__ == "__main__":
    main()
