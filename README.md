# MkDocs Ultralytics Plugin

The MkDocs Ultralytics Plugin is an easy-to-use plugin that generates meta description, image, and share buttons based on your Markdown content. It's specifically designed for MkDocs and provides a seamless integration to enhance your documentation.

## Features

- Generate meta description tag based on the first paragraph of a page
- Generate Open Graph (Facebook) and Twitter meta tags with image and description
- Add share buttons for Twitter and LinkedIn

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

## Plugin Arguments

The plugin supports the following arguments:

- `verbose`: Enable or disable verbose output (default: `True`)
- `enabled`: Enable or disable the plugin (default: `True`)
- `default_image`: Set a default image URL if no image is found in the content (default: `None`)
- `add_desc`: Enable or disable the generation of meta description tags (default: `True`)
- `add_image`: Enable or disable the generation of meta image tags (default: `True`)
- `add_share_buttons`: Enable or disable the addition of share buttons for Twitter and LinkedIn (default: `True`)

To use the arguments, add them to the `ultralytics` plugin section in your `mkdocs.yml` file:

```yaml
plugins:
  - mkdocstrings
  - search
  - ultralytics:
      verbose: True
      enabled: True
      default_image: "https://example.com/default-image.png"
      add_desc: True
      add_image: True
      add_share_buttons: True
```

## How it works

The plugin works by extracting the first paragraph and the first image (if available) from your Markdown content. It then generates and adds the appropriate meta description, image tags, and share buttons to the page.

### Meta Description

The meta description is extracted from the first paragraph of your Markdown content. The generated description is then added to the page's `<head>` section as a `<meta name="description">` tag.

### Meta Image

The meta image is extracted from the first image (if available) in your Markdown content. The generated image URL is then added to the page's `<head>` section as a `<meta property="og:image">` and `<meta property="twitter:image">` tags.

### Share Buttons

If the `add_share_buttons` argument is enabled, share buttons for Twitter and LinkedIn are added to the page, allowing users to easily share the content on social media platforms.

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
