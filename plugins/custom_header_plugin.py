PLUGIN_NAME = "custom_header"


def add_custom_header(client_code: str, header_name: str, header_value: str) -> str:
    """Add a custom header to the API client."""
    header_line = f"        '{header_name}': '{header_value}',"
    insertion_point = client_code.index("headers = {")
    insertion_index = client_code.index("\n", insertion_point) + 1
    return (
        client_code[:insertion_index]
        + header_line
        + "\n"
        + client_code[insertion_index:]
    )


def register_plugin():
    return add_custom_header
