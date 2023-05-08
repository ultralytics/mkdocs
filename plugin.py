from bs4 import BeautifulSoup
from mkdocs.plugins import BasePlugin


class DescriptionImagePlugin(BasePlugin):

    def on_page_content(self, content, page, config, files):
        soup = BeautifulSoup(content, 'html.parser')

        # Extract the first paragraph text
        first_paragraph = soup.find('p')
        if first_paragraph:
            meta_description = first_paragraph.text.strip()
            page.meta['description'] = meta_description

        # Extract the first image URL
        first_image = soup.find('img')
        if first_image:
            meta_image = first_image['src']
            page.meta['image'] = meta_image

        return content

    def on_post_page(self, output, page, config):
        if 'description' not in page.meta and 'image' not in page.meta:
            return output

        # Update meta description
        soup = BeautifulSoup(output, 'html.parser')
        if 'description' in page.meta and (10 < len(page.meta['description']) < 500):
            meta_description = soup.find("meta", attrs={"name": "description"})

            if meta_description:
                print(f'START_DESCRIPTION\n{meta_description}\nEND_DESCRIPTION\n\n')
                meta_description['content'] = page.meta['description']

        # Update meta image
        if 'image' in page.meta:
            meta_image = soup.find("meta", attrs={"property": "og:image"})

            # If the meta image tag is not found, create and add it
            if not meta_image:
                meta_image = soup.new_tag("meta")
                meta_image.attrs.update({'property': 'og:image', 'content': page.meta['image']})
                soup.head.append(meta_image)
            else:
                meta_image['content'] = page.meta['image']

        return str(soup)
