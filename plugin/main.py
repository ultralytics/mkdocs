# Ultralytics MkDocs plugin 🚀, AGPL-3.0 license


import json
from pathlib import Path
from subprocess import check_output

from bs4 import BeautifulSoup
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

# import get_github_usernames_from_file function from the previous script
from .utils import get_github_usernames_from_file, get_youtube_video_ids


class MetaPlugin(BasePlugin):
    # Plugin arguments
    config_scheme = (
        ("verbose", config_options.Type(bool, default=True)),
        ("enabled", config_options.Type(bool, default=True)),
        ("default_image", config_options.Type(str, default=None)),
        ("add_desc", config_options.Type(bool, default=True)),
        ("add_image", config_options.Type(bool, default=True)),
        ("add_keywords", config_options.Type(bool, default=True)),  # Add new argument for keywords
        ("add_share_buttons", config_options.Type(bool, default=True)),  # Add new argument
        ("add_dates", config_options.Type(bool, default=True)),  # Add dates section
        ("add_authors", config_options.Type(bool, default=False)),  # Add authors section
        ("add_json_ld", config_options.Type(bool, default=False)),  # Add JSON-LD structured data
    )

    def get_git_info(self, file_path):
        """
        Retrieves git information of a specified file including hash, date, and branch.

        Args:
            file_path (str): The path to the file for which git information is to be retrieved.

        Returns:
            (dict): A dictionary containing git information. The dictionary contains the following keys:
                - 'creation_date' (str): The creation date of the file.
                - 'last_modified_date' (str): The last modified date of the file.
                - 'authors' (list[tuple], optional): A list of tuples where each tuple contains author
                    information (name, url, changes) if `add_authors` is enabled in the plugin config.
        """
        file_path = str(Path(file_path).resolve())

        # Get the creation date
        args = ["git", "log", "--reverse", "--pretty=format:%ai", file_path]
        creation_date = check_output(args).decode("utf-8").split("\n")[0]
        git_info = {"creation_date": creation_date}

        # Get the last modification date
        last_modified_date = check_output(["git", "log", "-1", "--pretty=format:%ai", file_path]).decode("utf-8")
        git_info["last_modified_date"] = last_modified_date

        # Get the authors and their contributions count using get_github_usernames_from_file function
        if self.config["add_authors"]:
            authors_info = get_github_usernames_from_file(file_path)
            git_info["authors"] = [(author, info["url"], info["changes"]) for author, info in authors_info.items()]

        return git_info

    def on_page_content(self, content, page, config, files):
        """
        Processes page content with optional enhancements like images and keywords.

        Args:
            content (str): The content of the page in HTML format.
            page (mkdocs.structure.pages.Page): The MkDocs page object.
            config (mkdocs.config.Config): The global MkDocs configuration object.
            files (mkdocs.structure.files.Files): A collection of files in the documentation directory.

        Returns:
            (str): The modified page content with additional meta tags as per plugin configuration.
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
            content_to_insert (Tag or NavigableString): The HTML content to be inserted.

        Returns:
            None
        """
        if comments_header := soup.find("h2", id="__comments"):
            comments_header.insert_before(content_to_insert)
        # Fallback: append the content to the md-typeset div if the comments header is not found
        if md_typeset := soup.select_one(".md-content__inner"):
            md_typeset.append(content_to_insert)

    @staticmethod
    def parse_faq(soup):
        """Parse the FAQ questions and answers from the page content."""
        faqs = []
        faq_section = soup.find("h2", string="FAQ")

        if faq_section:
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
                    print(f'File: {page.file.src_path}, Description: {page.meta["description"]}')
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
        if (self.config["add_dates"] or self.config["add_authors"]) and git_info["creation_date"]:
            div = '<div class="git-info" style="font-size: 0.8em; text-align: right; margin-bottom: 10px;"><br>'

            if self.config["add_dates"]:
                div += f"Created {git_info['creation_date'][:10]}, Updated {git_info['last_modified_date'][:10]}"

            if self.config["add_authors"]:
                if self.config["add_dates"]:
                    div += "<br>"
                authors_str = ", ".join([f"<a href='{a[1]}'>{a[0]}</a> ({a[2]})" for a in git_info["authors"]])
                div += f"Authors: {authors_str}"

            div += "</div>"
            div = BeautifulSoup(div, "html.parser")
            self.insert_content(soup, div)

        # Add share buttons to the footer, if enabled
        if self.config["add_share_buttons"]:  # Check if share buttons are enabled
            twitter_share_link = f"https://twitter.com/intent/tweet?url={page_url}"
            linkedin_share_link = f"https://www.linkedin.com/shareArticle?url={page_url}"

            share_buttons = f"""
            <style>
                .share-button:hover {{
                    filter: brightness(1.2);
                }}
                .share-buttons {{
                    display: flex;
                    justify-content: flex-end;
                }}
            </style>
            <div class="share-buttons">
                <button onclick="window.open('{twitter_share_link}', 'TwitterShare', 'width=550,height=680,menubar=no,toolbar=no'); return false;" class="share-button" style="background-color: #1da1f2; color: white; padding: 5px 10px; border-radius: 5px; margin-right: 10px; cursor: pointer; display: flex; align-items: center;">
                    <i class="fa-brands fa-twitter" style="margin-right: 5px;"></i> Tweet
                </button>
                <button onclick="window.open('{linkedin_share_link}', 'LinkedinShare', 'width=550,height=730,menubar=no,toolbar=no'); return false;" class="share-button" style="background-color: #0077b5; color: white; padding: 5px 10px; border-radius: 5px; cursor: pointer; display: flex; align-items: center;">
                    <i class="fa-brands fa-linkedin" style="margin-right: 5px;"></i> Share
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

            faqs = self.parse_faq(soup)
            if faqs:
                ld_json_content["@type"] = ["Article", "FAQPage"]
                ld_json_content["mainEntity"] = faqs

            ld_json_script.string = json.dumps(ld_json_content)
            soup.head.append(ld_json_script)

        return str(soup)
