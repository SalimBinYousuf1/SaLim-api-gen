from salim_api_gen import APIGenerator


def generate_twitter_api_client():
    generator = APIGenerator("twitter_openapi.yaml", api_version="2")
    generator.generate("twitter_client.py")
    generator.generate_documentation("twitter_api_docs.md")
    generator.generate_mock_server("twitter_mock_server")
    generator.generate_sync_client("twitter_sync_client.py")


if __name__ == "__main__":
    generate_twitter_api_client()
