from bs4 import BeautifulSoup
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


class MetaPlugin(BasePlugin):
    # Plugin arguments
    config_scheme = (
        ('verbose', config_options.Type(bool, default=True)),
        ('enabled', config_options.Type(bool, default=True)),
        ('default_image', config_options.Type(str, default=None)),
    )

    def on_page_content(self, content, page, config, files):
        if not self.config['enabled']:
            return content

        soup = BeautifulSoup(content, 'html.parser')

        # Check if custom description is already defined in the Markdown header
        if 'description' not in page.meta:
            if first_paragraph := soup.find('p'):
                meta_description = first_paragraph.text.strip()
                page.meta['description'] = meta_description

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
            if 'description' in page.meta and (10 < len(page.meta['description']) < 500):
                if self.config['verbose']:
                    print(f'File: {page.file.src_path}, Description: {page.meta["description"]}')
                meta_description['content'] = page.meta['description']

        # Update meta image
        if 'image' in page.meta:
            if meta_image := soup.find("meta", attrs={"property": "og:image"}):
                meta_image['content'] = page.meta['image']

            else:
                meta_image = soup.new_tag("meta")
                meta_image.attrs.update({'property': 'og:image', 'content': page.meta['image']})
                soup.head.append(meta_image)
        return str(soup)
