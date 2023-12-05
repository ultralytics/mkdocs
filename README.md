<br>
<img src="https://raw.githubusercontent.com/ultralytics/assets/main/logo/Ultralytics_Logotype_Original.svg" width="320">

# 📚 MkDocs Ultralytics Plugin

The MkDocs Ultralytics Plugin is an intuitive tool designed to enhance your MkDocs site's search engine visibility 🌐 and user engagement 👥 by automatically generating metadata tags based on your Markdown content. Additionally, it adds interactive elements such as social share buttons, providing a more dynamic experience for your readers.

## Features 🌟

- **Automatic Meta Tags**: Generates meta description and image tags based on your content.
- **Meta Keywords**: Allows the addition of custom meta keywords specified in Markdown frontmatter.
- **Social Media Optimization**: Creates Open Graph (for Facebook) and Twitter meta tags for improved content sharing.
- **Share Buttons**: Integrates social share buttons for quick sharing on Twitter and LinkedIn.
- **Git Integration**: Appends Git dates and authors to the page footer, maintaining transparency and credibility.

## Installation 💻

Install the MkDocs Ultralytics Plugin effortlessly via [pip](https://pypi.org/project/mkdocs-ultralytics-plugin/):

[![PyPI version](https://badge.fury.io/py/mkdocs-ultralytics-plugin.svg)](https://badge.fury.io/py/mkdocs-ultralytics-plugin) [![Downloads](https://static.pepy.tech/badge/mkdocs-ultralytics-plugin)](https://pepy.tech/project/mkdocs-ultralytics-plugin)

```bash
pip install mkdocs-ultralytics-plugin
```

## Usage 📘

To integrate the plugin into your MkDocs project, simply add the plugin to the `plugins` section in your `mkdocs.yml` configuration:

```yaml
plugins:
  - mkdocstrings
  - search
  - ultralytics
```

## Plugin Arguments 🛠️

Customize the plugin behavior with the following configurable arguments:

- `verbose`: Toggles detailed output during processing.
- `enabled`: Determines if the plugin is active.
- `default_image`: Specifies a fallback image URL.
- `add_desc`: Controls the meta description tag generation.
- `add_image`: Manages the meta image tag creation.
- `add_keywords`: Enables the inclusion of meta keyword tags.
- `add_share_buttons`: Adds or removes the social share buttons.
- `add_dates`: Appends Git commit dates to page footers.
- `add_authors`: Includes Git author information in footers.

Configure these arguments by adding them to your `mkdocs.yml` file under the `ultralytics` plugin section:

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

## How it Works ⚙️

### Meta Description
When `add_desc` is set, the first paragraph serves as your page's meta description, housed within a `<meta name="description">` tag in the HTML.

### Meta Image
With `add_image` enabled, the plugin looks for the first image in your content, or uses `default_image` when none is found, to create sharing-optimized meta tags.

### Meta Keywords
Define custom keywords in your content's frontmatter. They will be inserted as `<meta name="keywords">`.

### Share Buttons
Activate `add_share_buttons` to add built-in Twitter and LinkedIn sharing options at the end of each page.

### Git Dates and Authors
`add_dates` and `add_authors` augment your page footer with commit dates and author names for a comprehensive content history.

## Plugin Code 🖥️

The `plugin.py` file encapsulates the main operations. It defines `MetaPlugin`, a class inheriting from `BasePlugin`, which interacts with page content to generate meta tags and features (commentary added for clarity):

```python
from mkdocs.plugins import BasePlugin


class MetaPlugin(BasePlugin):

    def on_page_content(self, content, page, config, files):
        # Process and extract metadata from content
        # ...

    def on_post_page(self, output, page, config):
        # Insert the generated metadata into the final output
        # ...
```

## Contribute 🤝

Ultralytics welcomes community contributions! Check out our [Contributing Guide](https://docs.ultralytics.com/help/contributing) and share your valuable input. Complete our [Survey](https://ultralytics.com/survey?utm_source=github&utm_medium=social&utm_campaign=Survey) to provide feedback. A massive thank you 🙏 to all contributors!

<a href="https://github.com/ultralytics/yolov5/graphs/contributors">
<img width="100%" src="https://github.com/ultralytics/assets/raw/main/im/image-contributors.png" alt="Ultralytics open-source contributors"></a>

## License 📄

Ultralytics provides two options:

- **AGPL-3.0 License**: For students and enthusiasts, this encourages collaboration. Consult the [LICENSE](https://github.com/ultralytics/ultralytics/blob/main/LICENSE) for specifics.
- **Enterprise License**: Suited for commercial use, granting rights outside the scope of AGPL-3.0. For enterprise solutions, visit [Ultralytics Licensing](https://ultralytics.com/license).

## Contact 📬

Submit bug reports and feature suggestions at [GitHub Issues](https://github.com/ultralytics/mkdocs/issues). For discussions and queries, engage with our [Discord](https://ultralytics.com/discord) community.

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
