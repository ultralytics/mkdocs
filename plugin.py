from bs4 import BeautifulSoup
from mkdocs.plugins import BasePlugin


class DescriptionImagePlugin(BasePlugin):

    def on_page_content(self, content, page, config, files):
        soup = BeautifulSoup(content, 'html.parser')

        if first_paragraph := soup.find('p'):
            meta_description = first_paragraph.text.strip()
            page.meta['description'] = meta_description

        if first_image := soup.find('img'):
            meta_image = first_image['src']
            page.meta['image'] = meta_image

        return content

    def on_post_page(self, output, page, config):
        if 'description' not in page.meta and 'image' not in page.meta:
            return output

        # Update meta description
        soup = BeautifulSoup(output, 'html.parser')
        if meta_description := soup.find("meta", attrs={"name": "description"}):
            if 'description' in page.meta and (10 < len(page.meta['description']) < 500):
                print(f'START_DESCRIPTION\n{meta_description}\nEND_DESCRIPTION\n\n')
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
