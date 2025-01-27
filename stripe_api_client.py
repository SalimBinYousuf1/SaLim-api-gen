from salim_api_gen import APIGenerator


def generate_stripe_api_client():
    generator = APIGenerator("stripe_openapi.yaml", api_version="2022-11-15")
    generator.generate("stripe_client.py")
    generator.generate_documentation("stripe_api_docs.md")
    generator.generate_mock_server("stripe_mock_server")
    generator.generate_sync_client("stripe_sync_client.py")


if __name__ == "__main__":
    generate_stripe_api_client()
