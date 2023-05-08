# MkDocs Ultralytics Plugin

The MkDocs Ultralytics Plugin is an easy-to-use plugin that generates meta description and image tags based on the first paragraph and the first image in a page. It's specifically designed for MkDocs and provides a seamless integration to enhance your documentation.

## Installation

To install the MkDocs Ultralytics Plugin from [pip](https://pypi.org/project/mkdocs-ultralytics-plugin/), run the following command:

```bash
pip install mkdocs-ultralytics-plugin
```

## Usage

To enable the plugin in your MkDocs project, add it to the `plugins` section of your `mkdocs.yml` file:

```yaml
plugins:
  - mkdocstrings
  - search
  - ultralytics
```

## How it works

The plugin works by extracting the first paragraph and the first image (if available) from your Markdown content. It then generates and adds the appropriate meta description and image tags to the page's `<head>` section.

### Meta Description

The meta description is extracted from the first paragraph of your Markdown content. The generated description is then added to the page's `<head>` section as a `<meta name="description">` tag.

### Meta Image

The meta image is extracted from the first image (if available) in your Markdown content. The generated image URL is then added to the page's `<head>` section as a `<meta property="og:image">` tag.

## Plugin Code

The core functionality of the plugin is implemented in `plugin.py`, which defines the `MetaPlugin` class:

```python
from bs4 import BeautifulSoup
from mkdocs.plugins import BasePlugin

class MetaPlugin(BasePlugin):

    def on_page_content(self, content, page, config, files):
        # ... (code to generate meta description and image)

    def on_post_page(self, output, page, config):
        # ... (code to update the output with the generated meta tags)

```

## License

This project is licensed under the AGPL-3.0 License. For more information, see the [LICENSE](LICENSE) file.
