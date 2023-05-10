from bs4 import BeautifulSoup
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


class MetaPlugin(BasePlugin):
    # Plugin arguments
    config_scheme = (
        ('verbose', config_options.Type(bool, default=True)),
        ('enabled', config_options.Type(bool, default=True)),
        ('default_image', config_options.Type(str, default=None)),
        ('add_desc', config_options.Type(bool, default=True)),
        ('add_image', config_options.Type(bool, default=True)),
        ('add_share_buttons', config_options.Type(bool, default=True)),  # Add new argument
    )

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

            if md_source_file_div := soup.select_one('.md-source-file'):
                md_source_file_div.insert_before(BeautifulSoup(share_buttons, 'html.parser'))
            elif md_typeset := soup.select_one('.md-typeset'):
                md_typeset.append(BeautifulSoup(share_buttons, 'html.parser'))

        return str(soup)
