<a href="https://www.ultralytics.com/"><img src="https://raw.githubusercontent.com/ultralytics/assets/main/logo/Ultralytics_Logotype_Original.svg" width="320" alt="Ultralytics logo"></a>

# 🚀 MkDocs Ultralytics Plugin

Welcome to the documentation for the MkDocs Ultralytics Plugin! 📄 This powerful plugin enhances your [MkDocs](https://www.mkdocs.org/)-generated documentation with advanced Search Engine Optimization (SEO) features, interactive social elements, and structured data support. It automates the generation of essential meta tags, incorporates social sharing capabilities, and adds [JSON-LD](https://json-ld.org/) structured data to elevate user engagement and improve your Markdown project's visibility on the web.

[![PyPI version](https://badge.fury.io/py/mkdocs-ultralytics-plugin.svg)](https://badge.fury.io/py/mkdocs-ultralytics-plugin)
[![Downloads](https://static.pepy.tech/badge/mkdocs-ultralytics-plugin)](https://clickpy.clickhouse.com/dashboard/mkdocs-ultralytics-plugin)
[![Ultralytics Actions](https://github.com/ultralytics/mkdocs/actions/workflows/format.yml/badge.svg)](https://github.com/ultralytics/mkdocs/actions/workflows/format.yml)
[![Ultralytics Discord](https://img.shields.io/discord/1089800235347353640?logo=discord&logoColor=white&label=Discord&color=blue)](https://discord.com/invite/ultralytics)
[![Ultralytics Forums](https://img.shields.io/discourse/users?server=https%3A%2F%2Fcommunity.ultralytics.com&logo=discourse&label=Forums&color=blue)](https://community.ultralytics.com/)
[![Ultralytics Reddit](https://img.shields.io/reddit/subreddit-subscribers/ultralytics?style=flat&logo=reddit&logoColor=white&label=Reddit&color=blue)](https://reddit.com/r/ultralytics)

## ✨ Features

This plugin seamlessly integrates a variety of valuable features into your MkDocs site:

- **Meta Tag Generation**: Automatically creates meta description and image tags using the first paragraph and image found on each page, crucial for SEO and social previews.
- **Keyword Customization**: Allows you to define specific meta keywords directly within your Markdown front matter for targeted SEO.
- **Social Media Optimization**: Generates [Open Graph](https://ogp.me/) and [Twitter Card](https://developer.x.com/en/docs/x-for-websites/cards/overview/summary-card-with-large-image) meta tags to ensure your content looks great when shared on social platforms.
- **Simple Sharing**: Inserts convenient share buttons for Twitter and LinkedIn at the end of your content, encouraging readers to share.
- **Git Insights**: Gathers and displays [Git](https://git-scm.com/) commit information, including update dates and authors, directly within the page footer for transparency.
- **JSON-LD Support**: Adds structured data in JSON-LD format, helping search engines understand your content better and potentially enabling rich results.
- **FAQ Parsing**: Automatically parses FAQ sections (if present) and includes them in the structured data for enhanced search visibility.
- **Customizable Styling**: Includes optional inline CSS to maintain consistent styling for plugin elements across your documentation, aligning with themes like [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## 🛠️ Installation

Getting started with the MkDocs Ultralytics Plugin is straightforward. Install it via [pip](https://pypi.org/project/pip/) using the following command:

```bash
pip install mkdocs-ultralytics-plugin
```

## 💻 Usage

To activate the plugin within your MkDocs project, add it to the `plugins` section of your `mkdocs.yml` configuration file:

```yaml
plugins:
  - mkdocstrings # Example of another plugin
  - search # Example of another plugin
  - ultralytics # Add the Ultralytics plugin here
```

## ⚙️ Configuration Arguments

The plugin offers several configuration arguments to customize its behavior according to your project's requirements:

- `verbose` (bool): Enables or disables detailed console output during the build process. Useful for debugging. Default: `True`.
- `enabled` (bool): Globally enables or disables the plugin. Default: `True`.
- `default_image` (str | None): Specifies a fallback image URL to use for meta tags if no image is found within the page content. Default: `None`.
- `default_author` (str | None): Sets a default GitHub author email to use if Git author information cannot be retrieved for a page. Default: `None`.
- `add_desc` (bool): Controls whether meta description tags are automatically generated. Default: `True`.
- `add_image` (bool): Controls whether meta image tags (Open Graph, Twitter) are automatically generated. Default: `True`.
- `add_keywords` (bool): Controls whether meta keyword tags are generated based on front matter. Default: `True`.
- `add_share_buttons` (bool): Determines if social media share buttons (Twitter, LinkedIn) are added to the page content. Default: `True`.
- `add_authors` (bool): Controls the display of author and last updated date information in the content footer based on Git history. Default: `False`.
- `add_json_ld` (bool): Enables the generation and injection of JSON-LD structured data into the page's head. Default: `False`.
- `add_css` (bool): Determines if the plugin's inline CSS styles are included for elements like share buttons. Default: `True`.

You can include these arguments under the `ultralytics` entry in your `mkdocs.yml` file like this:

```yaml
plugins:
  - mkdocstrings
  - search
  - ultralytics:
      verbose: True
      enabled: True
      default_image: "https://www.ultralytics.com/images/social.png" # Example default image
      default_author: "git@ultralytics.com" # Example default author
      add_desc: True
      add_image: True
      add_keywords: True
      add_share_buttons: True
      add_authors: False # Disabled by default
      add_json_ld: False # Disabled by default
      add_css: True
```

## 🧩 How It Works

Here’s a brief overview of the plugin's core functionalities:

### Meta Description Generation

When `add_desc` is enabled, the plugin extracts the first paragraph from your Markdown content and uses it to generate a `<meta name="description">` tag within the `<head>` section of the corresponding HTML page. This helps search engines and users understand the page's content at a glance.

### Meta Image Tagging

If `add_image` is active, the plugin identifies the first image referenced in the Markdown source. This image URL is then used to populate the `<meta property="og:image">` and `<meta property="twitter:image">` tags. If no image is detected on the page, the URL provided in `default_image` (if set) is used as a fallback.

### Meta Keyword Integration

By defining keywords in the Markdown front matter (e.g., `keywords: machine learning, computer vision, mkdocs`), and with `add_keywords` enabled, the plugin injects a corresponding `<meta name="keywords">` tag into the page's `<head>`.

### Social Share Buttons

Activating `add_share_buttons` automatically appends pre-styled Twitter and LinkedIn sharing buttons to the bottom of your main content area, making it easy for readers to share your documentation.

### Git Information Display

When `add_authors` is enabled, the plugin leverages Git history to retrieve the commit timestamp and author(s) for each page. This information is then displayed at the bottom of the page, providing context on when the content was last updated and by whom.

## 💡 Plugin Code Insight

The core logic resides within the `MetaPlugin` class in `plugin.py`. This class hooks into the MkDocs build process to modify page content and metadata.

```python
# Import the base class for MkDocs plugins
from mkdocs.plugins import BasePlugin


# Define the MetaPlugin class inheriting from BasePlugin
class MetaPlugin(BasePlugin):
    # This method runs after the Markdown is converted to HTML,
    # but before the template is rendered.
    # It's used here primarily to extract information like the first paragraph or image.
    def on_page_content(self, content, page, config, files):
        # Logic to find the first paragraph for meta description
        # Logic to find the first image for meta image tags
        # ... (details omitted for brevity)
        # The modified or extracted data is often stored for later use.
        return content  # Return the original content, as modifications happen later

    # This method runs after the page template has been rendered.
    # It allows modification of the final HTML output.
    def on_post_page(self, output, page, config):
        # Logic to inject generated meta tags (description, image, keywords) into <head>
        # Logic to add share buttons HTML to the end of the content area
        # Logic to add author/date footer HTML
        # Logic to add JSON-LD script tag to <head>
        # Logic to add inline CSS if enabled
        # ... (details omitted for brevity)
        return output  # Return the modified HTML output
```

This structure allows the plugin to analyze content and then inject the necessary HTML elements and metadata into the final output effectively. Check the source code for the full implementation details.

## 🤝 Contribute

Collaboration fuels innovation! 🤗 The success of Ultralytics' open-source projects, including this plugin, thrives on community contributions. We welcome your involvement, whether it's fixing bugs, proposing new features, improving documentation, engaging in discussions, or sharing how you use Ultralytics tools.

Please see our [Contributing Guide](https://docs.ultralytics.com/help/contributing/) for more details on how you can make a difference. Filling out our short [Survey](https://www.ultralytics.com/survey?utm_source=github&utm_medium=social&utm_campaign=Survey) also provides valuable feedback. We sincerely appreciate 🙇‍♂️ every contribution!

[![Ultralytics open-source contributors](https://raw.githubusercontent.com/ultralytics/assets/main/im/image-contributors.png)](https://github.com/ultralytics/ultralytics/graphs/contributors)

## 📜 License

Ultralytics provides two licensing options to accommodate different use cases:

- **AGPL-3.0 License**: Ideal for students, researchers, and enthusiasts, this [OSI-approved](https://opensource.org/license/agpl-v3) license promotes open collaboration and knowledge sharing. See the [LICENSE](https://github.com/ultralytics/mkdocs/blob/main/LICENSE) file for details.
- **Enterprise License**: Designed for commercial applications, this license allows seamless integration of Ultralytics software and AI models into commercial products and services, bypassing the open-source requirements of AGPL-3.0. If your project requires an Enterprise License, please visit [Ultralytics Licensing](https://www.ultralytics.com/license).

## ✉️ Connect with Us

Encountered a bug or have an idea for a new feature? Please visit [GitHub Issues](https://github.com/ultralytics/mkdocs/issues) to report problems or suggest enhancements. For broader discussions, questions, and community support related to Ultralytics projects, join our vibrant [Discord](https://discord.com/invite/ultralytics) server and check out the [Ultralytics Reddit](https://www.reddit.com/r/ultralytics/?rdt=34950).

<br>
<div align="center">
  <a href="https://github.com/ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-github.png" width="3%" alt="Ultralytics GitHub"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://www.linkedin.com/company/ultralytics/"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-linkedin.png" width="3%" alt="Ultralytics LinkedIn"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://twitter.com/ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-twitter.png" width="3%" alt="Ultralytics Twitter"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://youtube.com/ultralytics?sub_confirmation=1"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-youtube.png" width="3%" alt="Ultralytics YouTube"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://www.tiktok.com/@ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-tiktok.png" width="3%" alt="Ultralytics TikTok"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://ultralytics.com/bilibili"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-bilibili.png" width="3%" alt="Ultralytics BiliBili"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://discord.com/invite/ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-discord.png" width="3%" alt="Ultralytics Discord"></a>
</div>
