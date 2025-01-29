# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

import json
from datetime import datetime, timedelta
from pathlib import Path
from subprocess import check_output

from bs4 import BeautifulSoup
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

from plugin.utils import (
    calculate_time_difference,
    get_github_usernames_from_file,
    get_youtube_video_ids,
)

today = datetime.now()
DEFAULT_CREATION_DATE = (today - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S +0000")
DEFAULT_MODIFIED_DATE = (today - timedelta(days=40)).strftime("%Y-%m-%d %H:%M:%S +0000")


class MetaPlugin(BasePlugin):
    """
    MetaPlugin class for enhancing MkDocs documentation with metadata, social sharing, and structured data.

    This class extends the BasePlugin class from MkDocs to add various meta tags, social sharing buttons, and
    structured data to the generated HTML pages. It also retrieves git information for each file to include
    authorship and modification details.

    Methods:
        get_git_info: Retrieves git information of a specified file including hash, date, and branch.
        on_page_content: Processes page content with optional enhancements like images, descriptions, and keywords.
        insert_content: Inserts additional content into a BeautifulSoup object at a specified location.
        parse_faq: Parses the FAQ questions and answers from the HTML page content.
        on_post_page: Enhances the HTML output of a page with metadata tags, git information, and share buttons.
        get_css: Provides simplified CSS for styling the added elements.
    """

    config_scheme = (
        ("verbose", config_options.Type(bool, default=True)),  # Enable verbose output for debugging
        ("enabled", config_options.Type(bool, default=True)),  # Enable or disable the plugin
        ("default_image", config_options.Type(str, default=None)),  # Default image URL if none found in content
        ("default_author", config_options.Type(str, default=None)),  # Default GitHub author email if none found
        ("add_desc", config_options.Type(bool, default=True)),  # Add meta description tags
        ("add_image", config_options.Type(bool, default=True)),  # Add meta image tags
        ("add_keywords", config_options.Type(bool, default=True)),  # Add meta keywords tags
        ("add_share_buttons", config_options.Type(bool, default=True)),  # Add social share buttons
        ("add_authors", config_options.Type(bool, default=False)),  # Add git author and date information
        ("add_json_ld", config_options.Type(bool, default=False)),  # Add JSON-LD structured data
        ("add_css", config_options.Type(bool, default=True)),  # Inline CSS for styling
    )

    def get_git_info(self, file_path):
        """
        Retrieves git information of a specified file including hash, date, and branch.

        Args:
            file_path (str): The path to the file for which git information is to be retrieved.

        Returns:
            (dict): A dictionary containing git information. The dictionary contains the following keys:
                - creation_date (str): The creation date of the file.
                - last_modified_date (str): The last modified date of the file.
                - authors (list[tuple]): Optional. A list of tuples where each tuple contains author information
                  (name (str), url (str), changes (int)) if `add_authors` is enabled in the plugin config.

        Notes:
            Ensure git is installed and the file is within a git repository to retrieve accurate information.

        Examples:
            ```python
            plugin = MetaPlugin()
            git_info = plugin.get_git_info('path/to/file.py')
            print(git_info)
            ```
        """
        file_path = str(Path(file_path).resolve())

        # Get the creation and last modified dates
        args = ["git", "log", "--reverse", "--pretty=format:%ai", file_path]
        creation_date = check_output(args).decode("utf-8").split("\n")[0]
        last_modified_date = check_output(["git", "log", "-1", "--pretty=format:%ai", file_path]).decode("utf-8")
        git_info = {
            "creation_date": creation_date or DEFAULT_CREATION_DATE,
            "last_modified_date": last_modified_date or DEFAULT_MODIFIED_DATE,
        }

        # Get the authors and their contributions count using get_github_usernames_from_file function
        if self.config["add_authors"]:
            authors_info = get_github_usernames_from_file(file_path, default_user=self.config["default_author"])
            git_info["authors"] = [
                (author, info["url"], info["changes"], info["avatar"]) for author, info in authors_info.items()
            ]

        return git_info

    def on_page_content(self, content, page, config, files):
        """
        Processes page content with optional enhancements like images, descriptions, and keywords.

        Args:
            content (str): The content of the page in HTML format.
            page (mkdocs.structure.pages.Page): The MkDocs page object.
            config (mkdocs.config.Config): The global MkDocs configuration object.
            files (mkdocs.structure.files.Files): A collection of files in the documentation directory.

        Returns:
            (str): The modified page content with additional meta tags as per plugin configuration.

        Notes:
            This method enhances the content of a MkDocs page by adding meta tags such as descriptions and images.
            It checks and utilizes the first paragraph for a description, the first image or YouTube video for
            a thumbnail, and applies the specified default image if necessary. The functionality is controlled by
            the plugin's configuration settings. This is particularly useful for optimizing pages for SEO and
            social media sharing.
        """
        if not self.config["enabled"]:
            return content

        soup = BeautifulSoup(content, "html.parser")

        # Check if custom description is already defined in the Markdown header
        if first_paragraph := soup.find("p"):
            if self.config["add_desc"] and "description" not in page.meta:
                meta_description = first_paragraph.text.strip()
                page.meta["description"] = meta_description

        if self.config["add_image"]:
            if first_image := soup.find("img"):
                meta_image = first_image["src"]
                page.meta["image"] = meta_image
            # Check for embedded YouTube videos
            elif youtube_ids := get_youtube_video_ids(soup):
                # Just use the first YouTube video ID to get the thumbnail.
                first_youtube_id = youtube_ids[0]
                youtube_thumbnail_url = f"https://img.youtube.com/vi/{first_youtube_id}/maxresdefault.jpg"
                page.meta["image"] = youtube_thumbnail_url
            elif self.config["default_image"]:
                page.meta["image"] = self.config["default_image"]

        return content

    @staticmethod
    def insert_content(soup, content_to_insert):
        """
        Inserts additional content into a BeautifulSoup object at a specified location.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
            content_to_insert (Tag | NavigableString): The HTML content to be inserted.

        Returns:
            None

        Notes:
            This function specifically searches for an HTML element with the id "__comments" and inserts the
            content_to_insert before it. If the "__comments" element is not found, it defaults to appending
            the content to the element with class "md-content__inner".

        Example:
            ```python
            from bs4 import BeautifulSoup
            from bs4.element import Tag, NavigableString

            html_content = '<div class="md-content__inner"><h2 id="__comments">Comments</h2></div>'
            soup = BeautifulSoup(html_content, 'html.parser')
            new_content = soup.new_tag('div', id='new')
            new_content.string = "This is new content"

            MetaPlugin.insert_content(soup, new_content)
            print(soup.prettify())
            ```
        """
        if comments_header := soup.find("h2", id="__comments"):
            comments_header.insert_before(content_to_insert)
        # Fallback: append the content to the md-typeset div if the comments header is not found
        if md_typeset := soup.select_one(".md-content__inner"):
            md_typeset.append(content_to_insert)

    @staticmethod
    def parse_faq(soup):
        """
        Parse the FAQ questions and answers from the HTML page content.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML page content.

        Returns:
            (list[dict]): A list of dictionaries, each containing a parsed FAQ entry with 'Question' and 'Answer' fields
                          following the JSON-LD schema.

        Example:
            ```python
            from bs4 import BeautifulSoup
            from mymodule import MetaPlugin

            html_content = '<h2>FAQ</h2><h3>Question 1?</h3><p>Answer to question 1.</p>'
            soup = BeautifulSoup(html_content, 'html.parser')
            faq_data = MetaPlugin.parse_faq(soup)
            ```

        Note:
            This method identifies the FAQ section by looking for an `h2` tag with the text "FAQ". Each question is identified
            by an `h3` tag, and its corresponding answer is captured from `p` tags until the next `h3` or `h2` tag.
        """
        faqs = []
        if faq_section := soup.find("h2", string="FAQ"):
            current_section = faq_section.find_next_sibling()

            while current_section and current_section.name != "h2":
                if current_section.name == "h3":
                    question = current_section.text.strip()
                    answer = ""
                    next_sibling = current_section.find_next_sibling()

                    while next_sibling and next_sibling.name != "h3" and next_sibling.name != "h2":
                        if next_sibling.name == "p":
                            answer += f"{next_sibling.text.strip()} "
                        next_sibling = next_sibling.find_next_sibling()

                    if question and answer:
                        faqs.append(
                            {
                                "@type": "Question",
                                "name": question,
                                "acceptedAnswer": {"@type": "Answer", "text": answer.strip()},
                            }
                        )

                current_section = current_section.find_next_sibling()

        return faqs

    def on_post_page(self, output, page, config):
        """
        Enhances the HTML output of a page with metadata tags, git information, and share buttons.

        Args:
            output (str): The HTML content of the rendered page.
            page (Page): An object representing the current processed page.
            config (Config): The MkDocs configuration object.

        Returns:
            (str): The updated HTML content with additional metadata and enhancements.

        Notes:
            The output HTML is enhanced with meta tags for SEO, Open Graph, and Twitter. Additionally, git
            information such as creation and modification dates, and authorship details can be included,
            depending on the plugin configuration. Share buttons for Twitter and LinkedIn are optionally
            added to facilitate content sharing. Structured data in JSON-LD format is also appended when
            enabled, providing better integration with search engines. Ensure to configure 'site_url' in
            your MkDocs configuration for full functionality.
        """
        if not config["site_url"]:
            print(
                "WARNING - mkdocs-ultralytics-plugin: Please add a 'site_url' to your mkdocs.yml "
                "to enable all Ultralytics features, i.e. 'site_url: https://docs.ultralytics.com'"
            )
        page_url = (config["site_url"] or "") + page.url.rstrip("/")
        if not self.config["enabled"]:
            return output

        if "description" not in page.meta and "image" not in page.meta:
            return output

        # Update meta description
        soup = BeautifulSoup(output, "html.parser")

        # Primary Meta Tags
        title_tag = soup.new_tag("meta")
        title_tag.attrs.update({"name": "title", "content": page.title})
        soup.head.append(title_tag)

        # Append the Font Awesome CSS <link> tag to the <head> section for Twitter and LinkedIn emojis
        if self.config["add_share_buttons"]:
            soup.head.append(
                soup.new_tag(
                    "link",
                    rel="stylesheet",
                    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css",
                )
            )

        # New block for keywords
        if self.config["add_keywords"] and "keywords" in page.meta:
            meta_keywords = soup.new_tag("meta")
            meta_keywords.attrs.update({"name": "keywords", "content": page.meta["keywords"]})
            soup.head.append(meta_keywords)

        if meta_description := soup.find("meta", attrs={"name": "description"}):
            if self.config["add_desc"] and "description" in page.meta and (10 < len(page.meta["description"]) < 500):
                if self.config["verbose"]:
                    print(f"File: {page.file.src_path}, Description: {page.meta['description']}")
                meta_description["content"] = page.meta["description"]

        # Open Graph / Facebook
        og_type_tag = soup.new_tag("meta")
        og_type_tag.attrs.update({"property": "og:type", "content": "website"})
        soup.head.append(og_type_tag)

        og_url_tag = soup.new_tag("meta")
        og_url_tag.attrs.update({"property": "og:url", "content": page_url})
        soup.head.append(og_url_tag)

        og_title_tag = soup.new_tag("meta")
        og_title_tag.attrs.update({"property": "og:title", "content": page.title})
        soup.head.append(og_title_tag)

        og_desc_tag = soup.new_tag("meta")
        og_desc_tag.attrs.update({"property": "og:description", "content": page.meta.get("description", "")})
        soup.head.append(og_desc_tag)

        if self.config["add_image"] and "image" in page.meta:
            if meta_image := soup.find("meta", attrs={"property": "og:image"}):
                meta_image["content"] = page.meta["image"]
            else:
                meta_image = soup.new_tag("meta")
                meta_image.attrs.update({"property": "og:image", "content": page.meta["image"]})
                soup.head.append(meta_image)

        # Twitter
        twitter_card_tag = soup.new_tag("meta")
        twitter_card_tag.attrs.update({"property": "twitter:card", "content": "summary_large_image"})
        soup.head.append(twitter_card_tag)

        twitter_url_tag = soup.new_tag("meta")
        twitter_url_tag.attrs.update({"property": "twitter:url", "content": page_url})
        soup.head.append(twitter_url_tag)

        twitter_title_tag = soup.new_tag("meta")
        twitter_title_tag.attrs.update({"property": "twitter:title", "content": page.title})
        soup.head.append(twitter_title_tag)

        twitter_desc_tag = soup.new_tag("meta")
        twitter_desc_tag.attrs.update({"property": "twitter:description", "content": page.meta.get("description", "")})
        soup.head.append(twitter_desc_tag)

        if self.config["add_image"] and "image" in page.meta:
            twitter_image_tag = soup.new_tag("meta")
            twitter_image_tag.attrs.update({"property": "twitter:image", "content": page.meta["image"]})
            soup.head.append(twitter_image_tag)

        # Add git information (dates and authors) to the footer, if enabled
        git_info = self.get_git_info(page.file.abs_src_path)
        if (self.config["add_authors"]) and git_info["creation_date"]:
            created_ago, created_date = calculate_time_difference(git_info["creation_date"])
            updated_ago, updated_date = calculate_time_difference(git_info["last_modified_date"])

            div = f"""<div class="git-info">
<div class="dates-container">
    <span class="date-item" title="This page was first created on {created_date}">
        <span class="hover-item">📅</span> Created {created_ago} ago
    </span>
    <span class="date-item" title="This page was last updated on {updated_date}">
        <span class="hover-item">✏️</span> Updated {updated_ago} ago
    </span>
</div>
<div class="authors-container">
"""

            if self.config["add_authors"]:
                for author in git_info["authors"]:
                    name, url, n, avatar = author  # n is number of changes
                    div += f"""<a href="{url}" class="author-link" title="{name} ({n} change{"s" * (n > 1)})">
    <img src="{avatar}&s=96" alt="{name}" class="hover-item" loading="lazy">
</a>
"""

            div += "</div></div>"

            if self.config["add_css"]:
                style_tag = soup.new_tag("style")
                style_tag.string = self.get_css()
                soup.head.append(style_tag)

            div = BeautifulSoup(div, "html.parser")
            self.insert_content(soup, div)

        # Add share buttons to the footer, if enabled
        if self.config["add_share_buttons"]:
            twitter_share_link = f"https://twitter.com/intent/tweet?url={page_url}"
            linkedin_share_link = f"https://www.linkedin.com/shareArticle?url={page_url}"

            share_buttons = f"""<div class="share-buttons">
    <button onclick="window.open('{twitter_share_link}', 'TwitterShare', 'width=550,height=680,menubar=no,toolbar=no'); return false;" class="share-button hover-item">
        <i class="fa-brands fa-x-twitter"></i> Tweet
    </button>
    <button onclick="window.open('{linkedin_share_link}', 'LinkedinShare', 'width=550,height=730,menubar=no,toolbar=no'); return false;" class="share-button hover-item linkedin">
        <i class="fa-brands fa-linkedin-in"></i> Share
    </button>
</div>
"""
            share_buttons = BeautifulSoup(share_buttons, "html.parser")
            self.insert_content(soup, share_buttons)

        # Check if LD+JSON is enabled and add structured data to the <head>
        if self.config["add_json_ld"]:
            ld_json_script = soup.new_tag("script", type="application/ld+json")
            ld_json_content = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": page.title,
                "image": [page.meta["image"]] if "image" in page.meta else [],
                "datePublished": git_info["creation_date"],
                "dateModified": git_info["last_modified_date"],
                "author": [{"@type": "Organization", "name": "Ultralytics", "url": "https://ultralytics.com/"}],
                "abstract": page.meta.get("description", ""),
            }

            if faqs := self.parse_faq(soup):
                ld_json_content["@type"] = ["Article", "FAQPage"]
                ld_json_content["mainEntity"] = faqs

            ld_json_script.string = json.dumps(ld_json_content)
            soup.head.append(ld_json_script)

        return str(soup)

    @staticmethod
    def get_css():
        """Simplified CSS with unified hover effects, closer author circles, and larger share buttons."""
        return """
.git-info, .dates-container, .authors-container, .share-buttons {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: wrap;
}

.git-info {
    font-size: 0.8em;
    color: grey;
    margin-bottom: 10px;
}

.dates-container, .authors-container {
    margin-bottom: 10px;
}

.date-item, .author-link, .share-button {
    display: flex;
    align-items: center;
    cursor: pointer;
}

.date-item {
    margin-right: 10px;
}

.hover-item {
    transition: all 0.2s ease;
    filter: grayscale(100%);
}

.date-item .hover-item {
    font-size: 1.6em;
    margin-right: 5px;
}

.author-link .hover-item {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    margin-right: 3px;
    background-color: #f0f0f0;  /* Placeholder color */
    opacity: 0;  /* Start fully transparent */
    transition: opacity 0.3s ease-in-out;
}

.author-link .hover-item[src] {
    opacity: 1;  /* Fade in when src is set (image loaded) */
}

.hover-item:hover {
    transform: scale(1.2);
    filter: grayscale(0%);
}

.share-buttons {
    margin-top: 10px;
}

.share-button {
    background-color: #1da1f2;
    color: white;
    padding: 6px 12px;
    border-radius: 5px;
    border: none;
    font-size: 0.95em;
    margin: 5px;
    transition: all 0.2s ease;
}

.share-button:hover {
    transform: scale(1.1);
    filter: brightness(1.2);
}

.share-button.linkedin {
    background-color: #0077b5;
}

.share-button i {
    margin-right: 5px;
    font-size: 1.1em;
}

@media (max-width: 1024px) {
    .git-info {
        flex-direction: column;
        align-items: flex-end;
    }
    .dates-container, .authors-container {
        width: 100%;
    }
}
"""
