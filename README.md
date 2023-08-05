# MkDocs Ultralytics Plugin

The MkDocs Ultralytics Plugin is an easy-to-use plugin that enhances your MkDocs site's SEO and user engagement by generating meta tags (description, image, keywords) and adding interactive features based on your Markdown content.

## Features

- Automatically generates meta description and image tags based on the first paragraph and the first image of a page, respectively.
- Allows manual specification of meta keywords in the Markdown frontmatter.
- Generates Open Graph (Facebook) and Twitter meta tags for better social media sharing.
- Adds social share buttons for Twitter and LinkedIn at the end of each page.
- Fetches git information (dates and authors) from your repository and appends it to the page footer.

## Installation

To install the MkDocs Ultralytics Plugin from [pip](https://pypi.org/project/mkdocs-ultralytics-plugin/), run the following command:

[![PyPI version](https://badge.fury.io/py/mkdocs-ultralytics-plugin.svg)](https://badge.fury.io/py/mkdocs-ultralytics-plugin) [![Downloads](https://static.pepy.tech/badge/mkdocs-ultralytics-plugin)](https://pepy.tech/project/mkdocs-ultralytics-plugin)

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
- `add_keywords`: Enable or disable the generation of meta keyword tags (default: `True`)
- `add_share_buttons`: Enable or disable the addition of share buttons for Twitter and LinkedIn (default: `True`)
- `add_dates`: Enable or disable the addition of git dates to the page footer (default: `True`)
- `add_authors`: Enable or disable the addition of git authors to the page footer (default: `True`)

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
      add_keywords: True
      add_share_buttons: True
      add_dates: True
      add_authors: True
```

## How it works

The plugin works by processing your Markdown content, extracting relevant information, and generating additional meta tags and interactive features.

### Meta Description

If `add_desc` is enabled, the meta description is extracted from the first paragraph of your Markdown content. The generated description is then added to the page's `<head>` section as a `<meta name="description">` tag.

### Meta Image

If `add_image` is enabled, the meta image is extracted from the first image in your Markdown content. If no image is available, it uses the `default_image` (if specified). The image URL is added as `<meta property="og:image">` and `<meta property="twitter:image">` tags.

### Meta Keywords

You can manually specify meta keywords in the Markdown frontmatter. These will be added as a `<meta name="keywords">` tag in the page's `<head>` section.

### Share Buttons

If `add_share_buttons` is enabled, share buttons for Twitter and LinkedIn are added to the page. These allow users to easily share your content on social media.

### Git Dates and Authors

If `add_dates` or `add_authors` is enabled,

the plugin fetches relevant git information from your repository and appends it to the page footer. This keeps your readers informed about the recency and authorship of the content.

## Plugin Code

The core functionality of the plugin is implemented in `plugin.py`, which defines the `MetaPlugin` class:

```python
from mkdocs.plugins import BasePlugin


class MetaPlugin(BasePlugin):

    def on_page_content(self, content, page, config, files):
        # ... (code to generate meta description and image)

    def on_post_page(self, output, page, config):
        # ... (code to update the output with the generated meta tags)
```

## License

This project is licensed under the AGPL-3.0 License. For more information, see the [LICENSE](LICENSE) file.
