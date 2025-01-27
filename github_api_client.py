from salim_api_gen import APIGenerator


def generate_github_api_client():
    generator = APIGenerator("github_openapi.yaml", api_version="2022-11-28")
    generator.generate("github_client.py")
    generator.generate_documentation("github_api_docs.md")
    generator.generate_mock_server("github_mock_server")
    generator.generate_sync_client("github_sync_client.py")


if __name__ == "__main__":
    generate_github_api_client()
