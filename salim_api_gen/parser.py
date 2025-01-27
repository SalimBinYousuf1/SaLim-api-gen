from abc import ABC, abstractmethod
import yaml
import json
from typing import Dict, Any, List, Optional
from jsonschema import validate, ValidationError
import ramlfications


class BaseSpecParser(ABC):
    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_api_info(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_endpoints(self) -> Dict[str, Dict[str, Any]]:
        pass


class OpenAPIParser(BaseSpecParser):
    def __init__(self, spec_file: str, api_version: Optional[str] = None):
        self.spec_file = spec_file
        self.api_version = api_version
        self.spec_data: Dict[str, Any] = {}
        self.components: Dict[str, Any] = {}

    def parse(self) -> Dict[str, Any]:
        """
        Parse the OpenAPI specification file and return the data as a dictionary.
        """
        file_extension = self.spec_file.split(".")[-1].lower()

        try:
            with open(self.spec_file, "r") as file:
                if file_extension in ["yaml", "yml"]:
                    self.spec_data = yaml.safe_load(file)
                elif file_extension == "json":
                    self.spec_data = json.load(file)
                else:
                    raise ValueError(f"Unsupported file format: {file_extension}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Specification file not found: {self.spec_file}")
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Error parsing specification file: {str(e)}")

        self.components = self.spec_data.get("components", {})
        if self.api_version:
            self.spec_data = self._filter_by_version(self.spec_data)
        return self.spec_data

    def _filter_by_version(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        filtered_paths = {}
        for path, methods in spec_data.get("paths", {}).items():
            filtered_methods = {}
            for method, details in methods.items():
                if "x-api-version" in details:
                    if details["x-api-version"] == self.api_version:
                        filtered_methods[method] = details
                else:
                    filtered_methods[method] = details
            if filtered_methods:
                filtered_paths[path] = filtered_methods
        spec_data["paths"] = filtered_paths
        return spec_data

    def get_api_info(self) -> Dict[str, str]:
        """
        Extract basic API information from the parsed specification.
        """
        info = self.spec_data.get("info", {})
        return {
            "title": info.get("title", ""),
            "version": info.get("version", ""),
            "description": info.get("description", ""),
            "terms_of_service": info.get("termsOfService", ""),
            "contact": info.get("contact", {}),
            "license": info.get("license", {}),
        }

    def get_servers(self) -> List[Dict[str, str]]:
        """
        Extract server information from the parsed specification.
        """
        return self.spec_data.get("servers", [])

    def get_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract endpoint information from the parsed specification.
        """
        endpoints = {}
        paths = self.spec_data.get("paths", {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() not in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "options",
                    "head",
                ]:
                    continue

                endpoint_key = f"{method.upper()} {path}"
                endpoints[endpoint_key] = {
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "operationId": details.get("operationId", ""),
                    "parameters": self._process_parameters(
                        details.get("parameters", [])
                    ),
                    "requestBody": self._process_request_body(
                        details.get("requestBody", {})
                    ),
                    "responses": self._process_responses(details.get("responses", {})),
                    "security": details.get("security", []),
                    "tags": details.get("tags", []),
                }

        return endpoints

    def _process_parameters(
        self, parameters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process and resolve parameter references.
        """
        processed_params = []
        for param in parameters:
            if "$ref" in param:
                ref_path = param["$ref"].split("/")
                ref_param = self.components
                for path in ref_path[1:]:
                    ref_param = ref_param.get(path, {})
                processed_params.append(ref_param)
            else:
                processed_params.append(param)
        return processed_params

    def _process_request_body(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and resolve request body references.
        """
        if "$ref" in request_body:
            ref_path = request_body["$ref"].split("/")
            ref_body = self.components
            for path in ref_path[1:]:
                ref_body = ref_body.get(path, {})
            return ref_body
        return request_body

    def _process_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and resolve response references.
        """
        processed_responses = {}
        for status_code, response in responses.items():
            if "$ref" in response:
                ref_path = response["$ref"].split("/")
                ref_response = self.components
                for path in ref_path[1:]:
                    ref_response = ref_response.get(path, {})
                processed_responses[status_code] = ref_response
            else:
                processed_responses[status_code] = response
        return processed_responses

    def infer_type(self, schema: Dict[str, Any]) -> str:
        """
        Infer the Python type from an OpenAPI schema.
        """
        if "type" not in schema:
            return "Any"

        type_mapping = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": "List[{0}]",
            "object": "Dict[str, Any]",
        }

        if schema["type"] == "array" and "items" in schema:
            item_type = self.infer_type(schema["items"])
            return type_mapping["array"].format(item_type)

        if schema["type"] == "object" and "properties" in schema:
            properties = []
            for prop_name, prop_schema in schema["properties"].items():
                prop_type = self.infer_type(prop_schema)
                properties.append(f'"{prop_name}": {prop_type}')
            return f"Dict[{', '.join(properties)}]"

        if "enum" in schema:
            return f"Literal[{', '.join(repr(e) for e in schema['enum'])}]"

        if "$ref" in schema:
            ref_type = schema["$ref"].split("/")[-1]
            return ref_type

        return type_mapping.get(schema["type"], "Any")

    def get_request_body_type(self, request_body: Dict[str, Any]) -> str:
        """
        Infer the type of the request body.
        """
        if not request_body or "content" not in request_body:
            return "Any"

        content = request_body["content"]
        if "application/json" in content:
            schema = content["application/json"].get("schema", {})
            return self.infer_type(schema)

        return "Any"

    def get_response_type(self, responses: Dict[str, Any]) -> str:
        """
        Infer the type of the response.
        """
        for status_code in ("200", "201", "default"):
            if status_code in responses:
                response = responses[status_code]
                if "content" in response and "application/json" in response["content"]:
                    schema = response["content"]["application/json"].get("schema", {})
                    return self.infer_type(schema)

        return "Any"

    def validate_schema(self, data: Any, schema: Dict[str, Any]) -> None:
        """
        Validate data against a JSON schema.
        """
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            raise ValueError(f"Schema validation failed: {e}")

    def get_security_schemes(self) -> Dict[str, Any]:
        """
        Extract security schemes from the parsed specification.
        """
        return self.components.get("securitySchemes", {})

    def get_tags(self) -> List[Dict[str, str]]:
        """
        Extract tags from the parsed specification.
        """
        return self.spec_data.get("tags", [])

    def get_external_docs(self) -> Optional[Dict[str, str]]:
        """
        Extract external documentation information from the parsed specification.
        """
        return self.spec_data.get("externalDocs")


class APIBlueprintParser(BaseSpecParser):
    def __init__(self, spec_file: str):
        self.spec_file = spec_file
        self.spec_data: Dict[str, Any] = {}

    def parse(self) -> Dict[str, Any]:
        # Implement API Blueprint parsing logic here
        pass

    def get_api_info(self) -> Dict[str, str]:
        # Implement API Blueprint info extraction logic here
        pass

    def get_endpoints(self) -> Dict[str, Dict[str, Any]]:
        # Implement API Blueprint endpoints extraction logic here
        pass


class RAMLParser(BaseSpecParser):
    def __init__(self, spec_file: str):
        self.spec_file = spec_file
        self.api = None

    def parse(self) -> Dict[str, Any]:
        try:
            self.api = ramlfications.parse(self.spec_file)
            return self._convert_to_openapi_structure()
        except Exception as e:
            raise ValueError(f"Error parsing RAML specification: {str(e)}")

    def _convert_to_openapi_structure(self) -> Dict[str, Any]:
        openapi_structure = {
            "openapi": "3.0.0",
            "info": self.get_api_info(),
            "paths": self._get_paths(),
        }
        return openapi_structure

    def get_api_info(self) -> Dict[str, str]:
        return {
            "title": self.api.title,
            "version": self.api.version,
            "description": self.api.description or "",
        }

    def _get_paths(self) -> Dict[str, Any]:
        paths = {}
        for resource in self.api.resources:
            path = resource.path
            methods = {}
            for method in resource.methods:
                methods[method.method] = {
                    "summary": method.description or "",
                    "parameters": self._get_parameters(method),
                    "responses": self._get_responses(method),
                }
            paths[path] = methods
        return paths

    def _get_parameters(self, method) -> List[Dict[str, Any]]:
        parameters = []
        for param in method.query_params:
            parameters.append(
                {
                    "name": param.name,
                    "in": "query",
                    "description": param.description,
                    "required": param.required,
                    "schema": {"type": param.type},
                }
            )
        return parameters

    def _get_responses(self, method) -> Dict[str, Any]:
        responses = {}
        for response in method.responses:
            responses[str(response.code)] = {
                "description": response.description or "",
            }
        return responses

    def get_endpoints(self) -> Dict[str, Dict[str, Any]]:
        endpoints = {}
        for resource in self.api.resources:
            for method in resource.methods:
                endpoint_key = f"{method.method.upper()} {resource.path}"
                endpoints[endpoint_key] = {
                    "summary": method.description or "",
                    "parameters": self._get_parameters(method),
                    "responses": self._get_responses(method),
                }
        return endpoints


# Factory function to create the appropriate parser
def create_parser(spec_file: str, spec_format: str = "openapi") -> BaseSpecParser:
    if spec_format.lower() == "openapi":
        return OpenAPIParser(spec_file)
    elif spec_format.lower() == "raml":
        return RAMLParser(spec_file)
    elif spec_format.lower() == "apiblueprint":
        return APIBlueprintParser(spec_file)
    else:
        raise ValueError(f"Unsupported specification format: {spec_format}")
