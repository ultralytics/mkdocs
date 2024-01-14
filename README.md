<br>
<img src="https://raw.githubusercontent.com/ultralytics/assets/main/logo/Ultralytics_Logotype_Original.svg" width="320">

# 🚀 MkDocs Ultralytics Plugin

Welcome to the MkDocs Ultralytics Plugin documentation! 📄 This delightful plugin enhances your MkDocs-generated documentation with savvy SEO optimizations and interactive social elements. Through the autogeneration of meta tags and incorporation of social sharing features, it aims to elevate user engagement and broaden your Markdown project's footprint on the web.

[![PyPI version](https://badge.fury.io/py/mkdocs-ultralytics-plugin.svg)](https://badge.fury.io/py/mkdocs-ultralytics-plugin) [![Downloads](https://static.pepy.tech/badge/mkdocs-ultralytics-plugin)](https://pepy.tech/project/mkdocs-ultralytics-plugin) [![Ultralytics Actions](https://github.com/ultralytics/mkdocs/actions/workflows/format.yml/badge.svg)](https://github.com/ultralytics/mkdocs/actions/workflows/format.yml)

## 🌟 Features

This plugin seamlessly integrates a variety of features into your MkDocs site:

- **Meta Tag Generation**: Creates meta description and image tags from the first paragraph and image on the page.
- **Keyword Customization**: Allows you to define meta keywords directly in your Markdown front matter.
- **Social Media Optimization**: Generates Open Graph and Twitter meta tags for improved sharing on social platforms.
- **Sharing Made Simple**: Inserts convenient share buttons for Twitter and LinkedIn at the end of your content.
- **Git Insights**: Gathers and displays git commit information, including dates and authors, within the page footer.

## 🛠 Installation

Getting started with the MkDocs Ultralytics Plugin is easy! Install it via [pip](https://pypi.org/project/mkdocs-ultralytics-plugin/) with the following command:

```bash
pip install mkdocs-ultralytics-plugin
```

## 💻 Usage

To enable the plugin in your MkDocs configuration, simply add it under the `plugins` section in your `mkdocs.yml` file:

```yaml
plugins:
  - mkdocstrings
  - search
  - ultralytics
```

## ⚙️ Plugin Arguments

The plugin supports several configuration arguments to tailor its behavior to your needs:

- `verbose`: Toggles verbose output. Useful for debugging. (default: `True`)
- `enabled`: Toggles plugin activation. (default: `True`)
- `default_image`: Provides a fallback image URL if none is found in your content. (default: `None`)
- `add_desc`: Controls the generation of meta description tags. (default: `True`)
- `add_image`: Manages meta image tag generation. (default: `True`)
- `add_keywords`: Allows meta keyword tag generation. (default: `True`)
- `add_share_buttons`: Adds or removes social share buttons. (default: `True`)
- `add_dates`: Appends git commit dates to your content footer. (default: `True`)
- `add_authors`: Includes git author information in the content footer. (default: `True`)

Include these arguments under the `ultralytics` plugin entry in your `mkdocs.yml`:

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

## 🧩 How it works

Here's a breakdown of the plugin's inner workings:

### Meta Description

When `add_desc` is on, the plugin plucks the first paragraph from your Markdown and turns it into a `<meta name="description">` tag within the `<head>` of your page.

### Meta Image

Enabled by `add_image`, the first available image in the Markdown is assigned as `<meta property="og:image">` and `<meta property="twitter:image">` tags. If no image is detected, `default_image` steps in.

### Meta Keywords

Manually specify meta keywords in the Markdown front matter to inject a `<meta name="keywords">` tag into the `<head>` of your page.

### Share Buttons

Engage `add_share_buttons`, and voila! Twitter and LinkedIn sharing buttons appear, inviting users to spread the word about your content.

### Git Dates and Authors

With `add_dates` and `add_authors`, the plugin fetches and flaunts the git commit timestamp and author names at the bottom of your page, keeping readers informed.

## 💡 Plugin Code Insight

The `MetaPlugin` class within `plugin.py` is the heart of the plugin, orchestrating the metadata and feature insertions:

```python
# Our MkDocs plugin inherits features from the BasePlugin available in mkdocs
from mkdocs.plugins import BasePlugin

# The MetaPlugin class holds the core functionality
class MetaPlugin(BasePlugin):

    # Acts on the page content to generate meta tags
    def on_page_content(self, content, page, config, files):
        # ... (omitted code handling meta description and image generation)
        # Comments could further explain code (but are omitted for brevity)
        return content

    # Alters the final page output to include the new meta tags
    def on_post_page(self, output, page, config):
        # ... (omitted code that injects generated meta tags into the output)
        # Additional comments could describe processing steps
        return output
```

## 🤝 Contribute

Join in on the collaboration! 🤗 The success of Ultralytics' open-source initiatives springs from the vibrant contributions of our community. Whether you're fixing bugs, adding features, warming up our discussions, or sharing your Ultralytics project tale, [check out](https://docs.ultralytics.com/help/contributing) how you can be part of the journey. Filling out our [survey](https://ultralytics.com/survey?utm_source=github&utm_medium=social&utm_campaign=Survey) is another great way to share your feedback. We are deeply thankful 🙇‍♂️ for each contributor's time and efforts!

<!-- A visual tribute to our contributors! -->

<a href="https://github.com/ultralytics/yolov5/graphs/contributors">
<img width="100%" src="https://github.com/ultralytics/assets/raw/main/im/image-contributors.png" alt="Ultralytics open-source contributors"></a>

## 📜 License

Ultralytics projects come with two licensing flavors:

- **AGPL-3.0 License**: This license fosters open collaboration and knowledge sharing, making it a perfect match for students and hobbyists. For specifics, check the [LICENSE](https://github.com/ultralytics/ultralytics/blob/main/LICENSE) file.
- **Enterprise License**: When it comes to commercial endeavors, this license gets things rolling by allowing Ultralytics software and AI models to be woven into your business offerings without the AGPL-3.0's open-source constraints. For commercial integrations, please explore our [Ultralytics Licensing](https://ultralytics.com/license) options.

## ✉️ Connect with Us

Have you stumbled upon a glitch, or do you have a splendid feature idea? Pop over to [GitHub Issues](https://github.com/ultralytics/mkdocs/issues) to drop us a line! Also, join our [Discord](https://ultralytics.com/discord) for buzzing discussions, insights, and tips around our shared ML journeys.

<br>
<div align="center">
  <a href="https://github.com/ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-github.png" width="3%" alt="Ultralytics GitHub"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://www.linkedin.com/company/ultralytics/"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-linkedin.png" width="3%" alt="Ultralytics LinkedIn"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://twitter.com/ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-twitter.png" width="3%" alt="Ultralytics Twitter"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://youtube.com/ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-youtube.png" width="3%" alt="Ultralytics YouTube"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://www.tiktok.com/@ultralytics"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-tiktok.png" width="3%" alt="Ultralytics TikTok"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://www.instagram.com/ultralytics/"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-instagram.png" width="3%" alt="Ultralytics Instagram"></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="3%" alt="space">
  <a href="https://ultralytics.com/discord"><img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-discord.png" width="3%" alt="Ultralytics Discord"></a>
</div>
