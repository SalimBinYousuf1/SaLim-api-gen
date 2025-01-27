import os
import jinja2
from typing import Dict, Any


class JavaScriptGenerator:
    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir or os.path.join(
            os.path.dirname(__file__), "templates"
        )
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self, api_data: Dict[str, Any], output_file: str):
        template = self.template_env.get_template("js_client.js.jinja2")
        rendered_code = template.render(
            api_info=api_data["info"],
            endpoints=api_data["paths"],
        )

        with open(output_file, "w") as file:
            file.write(rendered_code)
