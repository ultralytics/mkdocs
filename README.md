<a href="https://www.ultralytics.com/"><img src="https://raw.githubusercontent.com/ultralytics/assets/main/logo/Ultralytics_Logotype_Original.svg" width="320" alt="Ultralytics logo"></a>

# 🚀 MkDocs Ultralytics Plugin

Welcome to the MkDocs Ultralytics Plugin! 📄 This powerful tool enhances your [MkDocs](https://www.mkdocs.org/), [Zensical](https://zensical.com/), or any static site documentation with advanced Search Engine Optimization (SEO) features, interactive social elements, and structured data support. It automates the generation of essential meta tags, incorporates social sharing capabilities, and adds [JSON-LD](https://json-ld.org/) structured data to elevate user engagement and improve your documentation's visibility on the web.

**Two modes available:**

- 🔌 **Plugin Mode**: Real-time processing during MkDocs builds
- 🔄 **Postprocess Mode**: Process any generated static site HTML after build

[![Ultralytics Actions](https://github.com/ultralytics/mkdocs/actions/workflows/format.yml/badge.svg)](https://github.com/ultralytics/mkdocs/actions/workflows/format.yml)

[![Ultralytics Discord](https://img.shields.io/discord/1089800235347353640?logo=discord&logoColor=white&label=Discord&color=blue)](https://discord.com/invite/ultralytics)
[![Ultralytics Forums](https://img.shields.io/discourse/users?server=https%3A%2F%2Fcommunity.ultralytics.com&logo=discourse&label=Forums&color=blue)](https://community.ultralytics.com/)
[![Ultralytics Reddit](https://img.shields.io/reddit/subreddit-subscribers/ultralytics?style=flat&logo=reddit&logoColor=white&label=Reddit&color=blue)](https://reddit.com/r/ultralytics)

## ✨ Features

This tool seamlessly integrates valuable features into your documentation site:

- **Meta Tag Generation**: Automatically creates meta description and image tags using the first paragraph and image found on each page, crucial for SEO and social previews.
- **Keyword Customization**: Allows you to define specific meta keywords directly within your Markdown front matter for targeted SEO.
- **Social Media Optimization**: Generates [Open Graph](https://ogp.me/) and [Twitter Card](https://developer.x.com/en/docs/x-for-websites/cards/overview/summary-card-with-large-image) meta tags to ensure your content looks great when shared on social platforms.
- **Simple Sharing**: Inserts convenient share buttons for Twitter and LinkedIn at the end of your content, encouraging readers to share.
- **Git Insights**: Gathers and displays [Git](https://git-scm.com/) commit information, including update dates and authors, directly within the page footer for transparency.
- **JSON-LD Support**: Adds structured data in JSON-LD format, helping search engines understand your content better and potentially enabling rich results.
- **FAQ Parsing**: Automatically parses FAQ sections (if present) and includes them in the structured data for enhanced search visibility.
- **Copy for LLM**: Adds a button to copy page content in Markdown format, optimized for sharing with AI assistants.
- **Customizable Styling**: Includes optional inline CSS to maintain consistent styling across your documentation, aligning with themes like [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## 🛠️ Installation

[![PyPI - Version](https://img.shields.io/pypi/v/mkdocs-ultralytics-plugin?logo=pypi&logoColor=white)](https://pypi.org/project/mkdocs-ultralytics-plugin/) [![Ultralytics Downloads](https://static.pepy.tech/badge/mkdocs-ultralytics-plugin)](https://clickpy.clickhouse.com/dashboard/mkdocs-ultralytics-plugin) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-ultralytics-plugin?logo=python&logoColor=gold)](https://pypi.org/project/mkdocs-ultralytics-plugin/)

Install via [pip](https://pypi.org/project/pip/):

```bash
pip install mkdocs-ultralytics-plugin
```

Or install from source for development:

```bash
git clone https://github.com/ultralytics/mkdocs
cd mkdocs
pip install -e .
```

## 💻 Usage

### 🔌 Plugin Mode (MkDocs)

Activate the plugin in your `mkdocs.yml`:

```yaml
plugins:
  - search
  - ultralytics:
      add_desc: False
      add_image: True
      add_authors: True
      add_json_ld: True
      add_share_buttons: True
      default_image: https://example.com/image.png
      default_author: you@example.com
```

Then build normally:

```bash
mkdocs build
mkdocs serve
```

### 🔄 Postprocess Mode (Zensical, Hugo, Jekyll, etc.)

For static site generators that don't support MkDocs plugins, use the standalone postprocess script.

**Step 1:** Create `postprocess.py` in your project root:

```python
from plugin import postprocess_site

if __name__ == "__main__":
    postprocess_site(
        site_dir="site",  # Your build output directory
        docs_dir="docs",  # Your source docs directory
        site_url="https://example.com",
        default_image="https://example.com/image.png",
        default_author="you@example.com",
        add_desc=True,
        add_image=True,
        add_authors=True,
        add_json_ld=True,
        add_share_buttons=True,
        add_css=True,
        add_copy_llm=True,
        verbose=True,
    )
```

**Step 2:** Build your site and run postprocess:

```bash
# For Zensical
zensical build && python postprocess.py

# For MkDocs (without plugin)
mkdocs build && python postprocess.py

# For Hugo
hugo && python postprocess.py

# For Jekyll
jekyll build && python postprocess.py
```

## ⚙️ Configuration Options

Both modes support the same configuration options:

| Option              | Type | Default | Description                      |
| ------------------- | ---- | ------- | -------------------------------- |
| `verbose`           | bool | `True`  | Enable detailed console output   |
| `enabled`           | bool | `True`  | Enable/disable processing        |
| `default_image`     | str  | `None`  | Fallback image URL for meta tags |
| `default_author`    | str  | `None`  | Default GitHub author email      |
| `add_desc`          | bool | `True`  | Generate meta description tags   |
| `add_image`         | bool | `True`  | Generate meta image tags         |
| `add_keywords`      | bool | `True`  | Generate meta keyword tags       |
| `add_share_buttons` | bool | `True`  | Add social share buttons         |
| `add_authors`       | bool | `False` | Display Git author info          |
| `add_json_ld`       | bool | `False` | Add JSON-LD structured data      |
| `add_css`           | bool | `True`  | Include inline CSS styles        |
| `add_copy_llm`      | bool | `True`  | Add "Copy for LLM" button        |

## 🧩 How It Works

The tool processes HTML pages to enhance them with metadata and interactive elements:

### Meta Description Generation

Extracts the first paragraph from your content and generates `<meta name="description">` tags for SEO.

### Meta Image Tagging

Identifies the first image in the content or uses the default image for `og:image` and `twitter:image` tags.

### Social Share Buttons

Appends pre-styled Twitter and LinkedIn sharing buttons to your content.

### Git Information Display

Retrieves Git history to show creation/update dates and author avatars at the bottom of pages.

### JSON-LD Structured Data

Generates Article and FAQPage schema for better search engine understanding.

### Copy for LLM Button

Adds a button next to the "Edit this page" button that fetches the raw Markdown and copies it to clipboard, perfect for sharing with AI assistants.

## 💡 Architecture

The codebase is organized for maximum code reuse:

```
plugin/
├── __init__.py       # Package metadata
├── processor.py      # ⭐ Core HTML processing logic
├── main.py          # MkDocs plugin wrapper
├── postprocess.py   # Standalone postprocess wrapper
└── utils.py         # Helper functions
```

Both plugin mode and postprocess mode use the same `process_html()` function in `processor.py`, ensuring identical output regardless of which mode you use.

## 📊 Plugin Mode vs Postprocess Mode

| Feature             | Plugin Mode             | Postprocess Mode             |
| ------------------- | ----------------------- | ---------------------------- |
| **Works with**      | MkDocs only             | Any static site generator    |
| **Processing time** | During build (per-page) | After build (batch)          |
| **Configuration**   | `mkdocs.yml`            | Python script                |
| **Hot reload**      | ✅ Yes                  | ❌ No (rebuild required)     |
| **Git info**        | ✅ Yes                  | ✅ Yes                       |
| **Best for**        | MkDocs projects         | Zensical, Hugo, Jekyll, etc. |

## 🤝 Contribute

Collaboration fuels innovation! 🤗 The success of Ultralytics' open-source projects thrives on community contributions. We welcome your involvement, whether it's fixing bugs, proposing new features, improving documentation, engaging in discussions, or sharing how you use Ultralytics tools.

Please see our [Contributing Guide](https://docs.ultralytics.com/help/contributing/) for details. Filling out our [Survey](https://www.ultralytics.com/survey?utm_source=github&utm_medium=social&utm_campaign=Survey) also provides valuable feedback. We sincerely appreciate 🙇‍♂️ every contribution!

[![Ultralytics open-source contributors](https://raw.githubusercontent.com/ultralytics/assets/main/im/image-contributors.png)](https://github.com/ultralytics/ultralytics/graphs/contributors)

## 📜 License

Ultralytics provides two licensing options:

- **AGPL-3.0 License**: Ideal for students, researchers, and enthusiasts, this [OSI-approved](https://opensource.org/license/agpl-v3) license promotes open collaboration and knowledge sharing. See the [LICENSE](https://github.com/ultralytics/mkdocs/blob/main/LICENSE) file for details.
- **Enterprise License**: Designed for commercial applications, this license allows seamless integration of Ultralytics software into commercial products, bypassing AGPL-3.0 requirements. Visit [Ultralytics Licensing](https://www.ultralytics.com/license) for details.

## ✉️ Connect with Us

Encountered a bug or have an idea? Visit [GitHub Issues](https://github.com/ultralytics/mkdocs/issues) to report problems or suggest enhancements. For discussions and community support, join our [Discord](https://discord.com/invite/ultralytics) server and check out [Ultralytics Reddit](https://www.reddit.com/r/ultralytics/).

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
