import subprocess
from pathlib import Path

from bs4 import BeautifulSoup
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

# import get_github_usernames_from_file function from the previous script
from .utils import get_github_usernames_from_file


class MetaPlugin(BasePlugin):
    # Plugin arguments
    config_scheme = (
        ('verbose', config_options.Type(bool, default=True)),
        ('enabled', config_options.Type(bool, default=True)),
        ('default_image', config_options.Type(str, default=None)),
        ('add_desc', config_options.Type(bool, default=True)),
        ('add_image', config_options.Type(bool, default=True)),
        ('add_keywords', config_options.Type(bool, default=True)),  # Add new argument for keywords
        ('add_share_buttons', config_options.Type(bool, default=True)),  # Add new argument
        ('add_dates', config_options.Type(bool, default=True)),  # Add dates section
        ('add_authors', config_options.Type(bool, default=True)),  # Add authors section
    )

    @staticmethod
    def get_git_info(file_path):
        file_path = Path(file_path).resolve()

        # Get the creation date
        args = ['git', 'log', '--reverse', '--pretty=format:%ai', str(file_path)]
        creation_date = subprocess.check_output(args).decode('utf-8').split('\n')[0]
        git_info = {'creation_date': creation_date}

        # Get the last modification date
        last_modification_date = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=format:%ai', str(file_path)]).decode('utf-8')
        git_info['last_modification_date'] = last_modification_date

        # Get the authors and their contributions count using get_github_usernames_from_file function
        authors_info = get_github_usernames_from_file(file_path)
        git_info['authors'] = [(author, info['url'], info['changes']) for author, info in authors_info.items()]

        return git_info

    def on_page_content(self, content, page, config, files):
        if not self.config['enabled']:
            return content

        soup = BeautifulSoup(content, 'html.parser')

        # Check if custom description is already defined in the Markdown header
        if self.config['add_desc'] and 'description' not in page.meta:
            if first_paragraph := soup.find('p'):
                meta_description = first_paragraph.text.strip()
                page.meta['description'] = meta_description

        if self.config['add_image']:
            if first_image := soup.find('img'):
                meta_image = first_image['src']
                page.meta['image'] = meta_image
            elif self.config['default_image']:
                page.meta['image'] = self.config['default_image']

        return content

    @staticmethod
    def insert_content(soup, content_to_insert):
        if comments_header := soup.find('h2', id='__comments'):
            comments_header.insert_before(content_to_insert)
        # Fallback: append the content to the md-typeset div if the comments header is not found
        if md_typeset := soup.select_one('.md-typeset'):
            md_typeset.append(content_to_insert)

    def on_post_page(self, output, page, config):
        page_url = config['site_url'] + page.url.rstrip('/')
        if not self.config['enabled']:
            return output

        if 'description' not in page.meta and 'image' not in page.meta:
            return output

        # Update meta description
        soup = BeautifulSoup(output, 'html.parser')

        # Primary Meta Tags
        title_tag = soup.new_tag("meta")
        title_tag.attrs.update({'name': 'title', 'content': page.title})
        soup.head.append(title_tag)

        # New block for keywords
        if self.config['add_keywords'] and 'keywords' in page.meta:
            meta_keywords = soup.new_tag("meta")
            meta_keywords.attrs.update({'name': 'keywords', 'content': page.meta['keywords']})
            soup.head.append(meta_keywords)

        if meta_description := soup.find("meta", attrs={"name": "description"}):
            if self.config['add_desc'] and 'description' in page.meta and (10 < len(page.meta['description']) < 500):
                if self.config['verbose']:
                    print(f'File: {page.file.src_path}, Description: {page.meta["description"]}')
                meta_description['content'] = page.meta['description']

        # Open Graph / Facebook
        og_type_tag = soup.new_tag("meta")
        og_type_tag.attrs.update({'property': 'og:type', 'content': 'website'})
        soup.head.append(og_type_tag)

        og_url_tag = soup.new_tag("meta")
        og_url_tag.attrs.update({'property': 'og:url', 'content': page_url})
        soup.head.append(og_url_tag)

        og_title_tag = soup.new_tag("meta")
        og_title_tag.attrs.update({'property': 'og:title', 'content': page.title})
        soup.head.append(og_title_tag)

        og_description_tag = soup.new_tag("meta")
        og_description_tag.attrs.update({'property': 'og:description', 'content': page.meta.get('description', '')})
        soup.head.append(og_description_tag)

        if self.config['add_image'] and 'image' in page.meta:
            if meta_image := soup.find("meta", attrs={"property": "og:image"}):
                meta_image['content'] = page.meta['image']
            else:
                meta_image = soup.new_tag("meta")
                meta_image.attrs.update({'property': 'og:image', 'content': page.meta['image']})
                soup.head.append(meta_image)

        # Twitter
        twitter_card_tag = soup.new_tag("meta")
        twitter_card_tag.attrs.update({'property': 'twitter:card', 'content': 'summary_large_image'})
        soup.head.append(twitter_card_tag)

        twitter_url_tag = soup.new_tag("meta")
        twitter_url_tag.attrs.update({'property': 'twitter:url', 'content': page_url})
        soup.head.append(twitter_url_tag)

        twitter_title_tag = soup.new_tag("meta")
        twitter_title_tag.attrs.update({'property': 'twitter:title', 'content': page.title})
        soup.head.append(twitter_title_tag)

        twitter_description_tag = soup.new_tag("meta")
        twitter_description_tag.attrs.update(
            {'property': 'twitter:description', 'content': page.meta.get('description', '')})
        soup.head.append(twitter_description_tag)

        if self.config['add_image'] and 'image' in page.meta:
            twitter_image_tag = soup.new_tag("meta")
            twitter_image_tag.attrs.update({'property': 'twitter:image', 'content': page.meta['image']})
            soup.head.append(twitter_image_tag)

        # Add git information (dates and authors) to the footer, if enabled
        if self.config['add_dates'] or self.config['add_authors']:
            git_info = self.get_git_info(page.file.abs_src_path)
            dates_and_authors_div = '<div class="git-info" style="font-size: 0.8em; text-align: right; margin-bottom: 10px;"><br>'

            if self.config['add_dates']:
                dates_and_authors_div += f"Created {git_info['creation_date'][:10]}, Updated {git_info['last_modification_date'][:10]}"

            if self.config['add_authors']:
                if self.config['add_dates']:
                    dates_and_authors_div += '<br>'
                authors_str = ', '.join(
                    [f"<a href='{author[1]}'>{author[0]}</a> ({author[2]})" for author in git_info['authors']])
                dates_and_authors_div += f"Authors: {authors_str}"

            dates_and_authors_div += '</div>'
            dates_and_authors_div = BeautifulSoup(dates_and_authors_div, 'html.parser')
            self.insert_content(soup, dates_and_authors_div)

        # Add share buttons to the footer, if enabled
        if self.config['add_share_buttons']:  # Check if share buttons are enabled
            # page_url = 'https://docs.ultralytics.com/modes/train'
            twitter_share_link = f"https://twitter.com/intent/tweet?url={page_url}"
            linkedin_share_link = f"https://www.linkedin.com/shareArticle?url={page_url}"

            # share_buttons = f'''
            # <div class="share-buttons" style="text-align: right;">
            #     <a href="javascript:void(0);" onclick="window.open('{twitter_share_link}', 'TwitterShare', 'width=550,height=680,menubar=no,toolbar=no'); return false;" style="margin-right: 20px;">
            #         <i class="fa-brands fa-twitter fa-xl"></i> Tweet
            #     </a>
            #     <a href="javascript:void(0);" onclick="window.open('{linkedin_share_link}', 'LinkedinShare', 'width=550,height=730,menubar=no,toolbar=no'); return false;">
            #         <i class="fa-brands fa-linkedin fa-xl"></i> Share
            #     </a>
            # </div>
            # '''

            share_buttons = f'''
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
            '''
            share_buttons = BeautifulSoup(share_buttons, 'html.parser')
            self.insert_content(soup, share_buttons)

        return str(soup)
