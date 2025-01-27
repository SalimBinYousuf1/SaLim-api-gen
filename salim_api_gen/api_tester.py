import asyncio
import json
import click
from .generator import APIGenerator


@click.command()
@click.option("--spec", required=True, help="Path to the API specification file")
@click.option("--endpoint", required=True, help="API endpoint to test")
@click.option("--method", default="GET", help="HTTP method to use")
@click.option("--data", help="JSON data to send with the request")
@click.option("--output", default="response.json", help="Output file for the response")
def test_api(spec, endpoint, method, data, output):
    """Test an API endpoint using the generated client."""
    click.echo(f"Testing API endpoint: {endpoint}")

    generator = APIGenerator(spec)
    generator.generate("temp_client.py")

    from temp_client import APIClient

    async def run_test():
        async with APIClient("https://api.example.com") as client:
            method_to_call = getattr(client, endpoint.replace("/", "_"))
            kwargs = {}
            if data:
                kwargs["data"] = json.loads(data)
            response = await method_to_call(**kwargs)
            with open(output, "w") as f:
                json.dump(response, f, indent=2)
            click.echo(f"Response saved to {output}")

    asyncio.run(run_test())


if __name__ == "__main__":
    test_api()
