"""This module manages the prompts used in the data extraction process."""
from pathlib import Path
import frontmatter
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError, meta, select_autoescape


class PromptManager:
    """Manages the prompts used in the data extraction process."""    

    _env = None

    @classmethod
    def _get_env(cls, templates_dir="prompts/templates"):
        """Get the Jinja2 environment for rendering templates."""
        templates_dir = Path(__file__).parent.parent / templates_dir
        if cls._env is None:
            cls._env = Environment(
                loader=FileSystemLoader(templates_dir),
                undefined=StrictUndefined,
                autoescape=select_autoescape(['html', 'xml'])
            )
        return cls._env

    @staticmethod
    def get_prompt(template, **kwargs):
        """Render a prompt template with the provided context."""
        env = PromptManager._get_env()
        template_path = f"{template}.j2"
        with open(env.loader.get_source(env, template_path)[1]) as file:
            post = frontmatter.load(file)

        template = env.from_string(post.content)
        try:
            return template.render(**kwargs)
        except TemplateError as e:
            raise ValueError(f"Error rendering template: {str(e)}")

    @staticmethod
    def get_template_info(template):
        """Get information about a prompt template."""
        env = PromptManager._get_env()
        template_path = f"{template}.j2"
        with open(env.loader.get_source(env, template_path)[1]) as file:
            post = frontmatter.load(file)

        ast = env.parse(post.content)
        variables = meta.find_undeclared_variables(ast)

        return {
            "name": template,
            "description": post.metadata.get("description", "No description provided"),
            "author": post.metadata.get("author", "Unknown"),
            "variables": list(variables),
            "frontmatter": post.metadata,
        }
