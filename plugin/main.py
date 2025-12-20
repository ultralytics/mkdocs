# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

from __future__ import annotations

from pathlib import Path

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

import plugin.processor as processor
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
        ("add_llms_txt", config_options.Type(bool, default=True)),
    )

    def __init__(self):
        super().__init__()
        self.git_repo_url = None
        self.git_data = None

    def on_config(self, config):
        """Prepare git metadata once for all pages if authors/JSON-LD are enabled."""
        if not self.config.get("enabled", True):
            return config

        if self.config.get("add_authors") or self.config.get("add_json_ld"):
            docs_dir = Path(config["docs_dir"])
            md_files = [str(p) for p in docs_dir.rglob("*.md")] if docs_dir.exists() else []
            self.git_repo_url, self.git_data = processor.build_git_map(md_files)
        return config

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
                git_data=self.git_data,
                repo_url=self.git_repo_url,
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

    def on_post_build(self, config):
        """Generate llms.txt after build completes."""
        if not self.config.get("enabled", True) or not self.config.get("add_llms_txt", True):
            return
        from plugin.postprocess import generate_llms_txt

        generate_llms_txt(Path(config["site_dir"]), Path(config["docs_dir"]), config.get("site_url", ""))
