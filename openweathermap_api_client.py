from salim_api_gen import APIGenerator


def generate_openweathermap_api_client():
    generator = APIGenerator("openweathermap_openapi.yaml")
    generator.generate("openweathermap_client.py")
    generator.generate_documentation("openweathermap_api_docs.md")
    generator.generate_mock_server("openweathermap_mock_server")
    generator.generate_sync_client("openweathermap_sync_client.py")


if __name__ == "__main__":
    generate_openweathermap_api_client()
