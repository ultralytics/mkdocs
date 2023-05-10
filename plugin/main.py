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
        if not self.config['enabled']:
            return output

        if 'description' not in page.meta and 'image' not in page.meta:
            return output

        # Update meta description
        soup = BeautifulSoup(output, 'html.parser')
        if meta_description := soup.find("meta", attrs={"name": "description"}):
            if self.config['add_desc'] and 'description' in page.meta and (10 < len(page.meta['description']) < 500):
                if self.config['verbose']:
                    print(f'File: {page.file.src_path}, Description: {page.meta["description"]}')
                meta_description['content'] = page.meta['description']

        if self.config['add_image'] and 'image' in page.meta:
            if meta_image := soup.find("meta", attrs={"property": "og:image"}):
                meta_image['content'] = page.meta['image']

            else:
                meta_image = soup.new_tag("meta")
                meta_image.attrs.update({'property': 'og:image', 'content': page.meta['image']})
                soup.head.append(meta_image)

        # Add share buttons to the footer, if enabled
        if self.config['add_share_buttons']:  # Check if share buttons are enabled
            page_url = config['site_url'] + page.url
            twitter_share_link = f"https://twitter.com/intent/tweet?url={page_url}"
            linkedin_share_link = f"https://www.linkedin.com/shareArticle?url={page_url}"

            share_buttons = f'''
            <div class="share-buttons" style="text-align: right;">
                <a href="{twitter_share_link}" target="_blank" rel="noopener noreferrer" style="margin-right: 20px;">
                    <i class="fa-brands fa-twitter fa-xl"></i> Share on Twitter
                </a>
                <a href="{linkedin_share_link}" target="_blank" rel="noopener noreferrer">
                    <i class="fa-brands fa-linkedin fa-xl"></i> Share on LinkedIn
                </a>
            </div>
            '''

            if md_source_file_div := soup.select_one('.md-source-file'):
                md_source_file_div.insert_before(BeautifulSoup(share_buttons, 'html.parser'))
            elif md_typeset := soup.select_one('.md-typeset'):
                md_typeset.append(BeautifulSoup(share_buttons, 'html.parser'))

        return str(soup)
