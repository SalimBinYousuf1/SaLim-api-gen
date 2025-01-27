import asyncio
from github_client import GitHubClient


async def main():
    # Initialize the client with your GitHub token
    client = GitHubClient("https://api.github.com", api_key="YOUR_GITHUB_TOKEN")

    try:
        # Get authenticated user
        user = await client.get_authenticated_user()
        print(f"Authenticated as: {user['login']}")

        # List repositories for the authenticated user
        repos = await client.list_repositories_for_authenticated_user()
        print("Your repositories:")
        for repo in repos:
            print(f"- {repo['name']}")

        # Create a new repository
        new_repo = await client.create_repository(
            data={
                "name": "test-repo",
                "description": "A test repository created using SaLim-api-gen",
                "private": False,
            }
        )
        print(f"Created new repository: {new_repo['html_url']}")

        # Delete the repository
        await client.delete_repository(owner=user["login"], repo="test-repo")
        print("Deleted the test repository")

    except HTTPError as e:
        print(f"HTTP Error: {e}")
    except JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
    except InvalidParameterError as e:
        print(f"Invalid Parameter: {e}")
    except APIError as e:
        print(f"API Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
