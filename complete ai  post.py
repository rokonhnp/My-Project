import os
from requests import post
from dotenv import load_dotenv

load_dotenv()
import openai
import base64

from amazon_paapi import AmazonApi

KEY = os.getenv('KEY')
SECRET = os.getenv('SECRET')
TAG = os.getenv('TAG')
COUNTRY = os.getenv('COUNTRY')

amazon = AmazonApi(KEY, SECRET, TAG, COUNTRY)

openai.api_key = os.getenv('openai_api')

wp_user = os.getenv('user')
wp_pass = os.getenv('pass')
wp_credential = f'{wp_user}:{wp_pass}'
wp_token = base64.b64encode(wp_credential.encode('utf-8'))
wp_headers = {'Authorization': 'Basic ' + wp_token.decode()}

file = open('keyword.text')
keywords = file.readlines()
file.close()


def openai_answer(prompt):
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    ai_data = response.get('choices')[0].get('text').strip('\n')
    return ai_data


def wp_heading_two(text):
    heading = f'<!-- wp:heading --><h2>{text}</h2><!-- /wp:heading -->'
    return heading


def wp_heading_three(text):
    heading = f'<!-- wp:heading {"level":3} --><h3>{text}</h3><!-- /wp:heading -->'
    return heading


def wp_paragraph(text):
    pragraph = f'<!-- wp:paragraph --><p>{text}</p><!-- /wp:paragraph -->'
    return pragraph


def slugify(text):
    code = text.strip().replace(' ', '-')
    return code


def product_image(url, product_name):
    code = f'<!-- wp:image {{"align":"center","sizeSlug":"large"}} --><figure class="wp-block-image aligncenter size-large"><img src="{url}" alt="{product_name}"/><figcaption class="wp-element-caption"></figcaption></figure><!-- /wp:image -->'
    return code


def product_button(link):
    code = f'<!-- wp:buttons --><div class="wp-block-buttons"><!-- wp:button {{"align":"center"}} --><div class="wp-block-button aligncenter"><a class="wp-block-button__link wp-element-button" href="{link}" target="_blank" rel="noreferrer noopener">Buy Now</a></div><!-- /wp:button --></div><!-- /wp:buttons -->'
    return code


for keyword in keywords:
    keyword = keyword.strip('\n')

    # amazon features items
    search_result = amazon.search_items(keywords=keyword, item_count=2)
    for item in search_result.items:
        title = item.item_info.title.display_value
        product_image_url = item.images.primary.large.url
        wp_image = product_image(product_image_url, title)
        features = item.item_info.features.display_values

        ai_features = f'write a paragraph about {features}'
        ai_features_item = openai_answer(ai_features)
        features_text = wp_paragraph(ai_features_item)

        button_url = item.detail_page_url
        button = product_button(button_url)

        final_features = wp_heading_three(title) + wp_image + features_text + button

    post_intro = f'write 50 words about {keyword}'
    post_bottom = f'write 50 words conclusion about {keyword}'

    # Buying guide prompt
    intro_prompt = f'write a short description about {keyword}'
    important_prompt = f'write why {keyword} is important'
    how_prompt = f"write a paragraph about 'how to choose best' {keyword}"
    consider_prompt = f"write a 200 word about '5 things to Consider while buying' {keyword}"
    conclusion_prompt = f'Write a 100 word blog conclusion on {intro_prompt}'

    slug = slugify(keyword)
    wp_title = f'Best {keyword.title()} in 2023'

    buying_title = f'Best {keyword.title()} Buying Guide and More'
    h3_important = f'Why {keyword.title()} Is Important'
    h3_how = f'How to Choose The Best {keyword.title()}'
    h3_consider = f'Things to Consider While Buying {keyword.title()}'

    post_introduction = wp_paragraph(openai_answer(post_intro))
    post_conclusion = wp_heading_two('Conclusion') + wp_paragraph(openai_answer(post_bottom))

    buying_guide_title = wp_heading_two(buying_title)
    header_intro = wp_paragraph(openai_answer(intro_prompt))
    pra_one = wp_heading_three(h3_important) + wp_paragraph(openai_answer(important_prompt))
    pra_two = wp_heading_three(h3_how) + wp_paragraph(openai_answer(how_prompt))
    pra_three = wp_heading_three(h3_consider) + wp_paragraph(openai_answer(consider_prompt))
    content = f'{buying_guide_title}{header_intro}{pra_one}{pra_two}{pra_three}'

    final_content = post_introduction + final_features + content + post_conclusion


    def wp_posting(wp_title, slug, final_content):
        api_url = 'https://localhost/mobile-phone/wp-json/wp/v2/posts'
        data = {
            'title': wp_title,
            'slug': slug,
            'content': final_content
        }
        res = post(url=api_url, data=data, headers=wp_headers, verify=False)
        print(res)


    wp_posting(wp_title, slug, final_content)
