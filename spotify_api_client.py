from salim_api_gen import APIGenerator


def generate_spotify_api_client():
    generator = APIGenerator("spotify_openapi.yaml")
    generator.generate("spotify_client.py")
    generator.generate_documentation("spotify_api_docs.md")
    generator.generate_mock_server("spotify_mock_server")
    generator.generate_sync_client("spotify_sync_client.py")


if __name__ == "__main__":
    generate_spotify_api_client()
