# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

from __future__ import annotations

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

from plugin.processor import process_html


class MetaPlugin(BasePlugin):
    """MetaPlugin class for enhancing MkDocs documentation with metadata, social sharing, and structured data."""

    config_scheme = (
        ("verbose", config_options.Type(bool, default=True)),
        ("enabled", config_options.Type(bool, default=True)),
        ("default_image", config_options.Type(str, default=None)),
        ("default_author", config_options.Type(str, default=None)),
        ("add_desc", config_options.Type(bool, default=True)),
        ("add_image", config_options.Type(bool, default=True)),
        ("add_keywords", config_options.Type(bool, default=True)),
        ("add_share_buttons", config_options.Type(bool, default=True)),
        ("add_authors", config_options.Type(bool, default=False)),
        ("add_json_ld", config_options.Type(bool, default=False)),
        ("add_css", config_options.Type(bool, default=True)),
        ("add_copy_llm", config_options.Type(bool, default=True)),
    )

    def on_post_page(self, output: str, page, config) -> str:
        """Enhance HTML output by delegating to shared processor."""
        if not self.config["enabled"]:
            return output

        if not config["site_url"] and self.config["verbose"]:
            print(
                "WARNING - mkdocs-ultralytics-plugin: Please add a 'site_url' to your mkdocs.yml "
                "to enable all Ultralytics features, i.e. 'site_url: https://docs.ultralytics.com'"
            )

        try:
            page_url = (config["site_url"] or "") + page.url.rstrip("/")
            title = page.title
            keywords = page.meta.get("keywords", None) if hasattr(page, "meta") else None

            return process_html(
                html=output,
                page_url=page_url,
                title=title,
                src_path=page.file.abs_src_path,
                default_image=self.config["default_image"],
                default_author=self.config["default_author"],
                keywords=keywords,
                add_desc=self.config["add_desc"],
                add_image=self.config["add_image"],
                add_keywords=self.config["add_keywords"],
                add_share_buttons=self.config["add_share_buttons"],
                add_authors=self.config["add_authors"],
                add_json_ld=self.config["add_json_ld"],
                add_css=self.config["add_css"],
                add_copy_llm=self.config["add_copy_llm"],
            )
        except Exception as e:
            if self.config["verbose"]:
                print(f"ERROR - mkdocs-ultralytics-plugin: Failed to process {page.file.src_path}: {e}")
            return output  # Return original output on error
