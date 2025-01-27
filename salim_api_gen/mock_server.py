import os
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import JSONResponse


class MockServerGenerator:
    def generate(self, api_data: Dict[str, Any], output_dir: str):
        app = FastAPI(
            title=api_data["info"]["title"], version=api_data["info"]["version"]
        )

        for path, path_item in api_data["paths"].items():
            for method, operation in path_item.items():
                self.add_endpoint(app, method, path, operation)

        self.save_mock_server(app, output_dir)

    def add_endpoint(
        self, app: FastAPI, method: str, path: str, operation: Dict[str, Any]
    ):
        async def mock_endpoint():
            return JSONResponse(content={"message": "This is a mock response"})

        getattr(app, method.lower())(path)(mock_endpoint)

    def save_mock_server(self, app: FastAPI, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "mock_server.py"), "w") as f:
            f.write(
                f"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="{app.title}", version="{app.version}")

{self.generate_endpoint_code(app)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
            )

    def generate_endpoint_code(self, app: FastAPI) -> str:
        endpoint_code = ""
        for route in app.routes:
            endpoint_code += f"""
@app.{route.methods[0].lower()}("{route.path}")
async def {route.name}():
    return JSONResponse(content={{"message": "This is a mock response"}})
"""
        return endpoint_code
