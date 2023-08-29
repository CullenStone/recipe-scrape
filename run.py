import requests
from bs4 import BeautifulSoup
import pandas as pd

main_url = "https://kindredcocktails.com"
landing_page = "https://kindredcocktails.com/cocktail?scope=0"


# Grab max number of items/pages
# Loop through each page and open recipe
# Parse recipe (return recipe)
# Prettify dataframe

def parse_recipe(recipe_url: str):
    # Parse the page for useful information
    print(f"Navigating to: {recipe_url}")
    html_content = requests.get(recipe_url)
    soup = BeautifulSoup(html_content.text, 'html5lib')
    
    # Drink name
    name = soup.title.text.split('|')[0].strip()

    # Ingredients
    ingredients = dict()
    for i in soup.find_all(property="schema:recipeIngredient"):
        ingredients.update({
            i.find(class_='ingredient-name').text: i.find(class_='quantity-unit').text
        })
    
    # Instructions
    instructions = soup.find(property="schema:recipeInstructions").text

    # History
    #TODO

    # Similar Cocktails
    similar_cocktails = dict()
    for s in soup.find_all(title="Similar cocktail"):
        similar_cocktails.update({
            s.text: f"{main_url}{s.get('href')}"
        })

    # Summary (needs more work)
    summary = soup.find(class_="col-xs-12 col-sm-4 pull-right").find(class_='panel-body')  
    key_ = [x.text.lower() for x in summary.find_all(class_='field--label')]
    value_ = [x.text for x in summary.find_all(class_='field--item')]
    about = dict(zip(key_, value_))
    
    recipe = {
        'name': name,
        'url': recipe_url,
        'ingredients': '\n'.join([f"{v} {k}" for k, v in ingredients.items()]),
        'instructions': instructions,
        'similar_cocktails': '\n'.join([f"{k}: {v}" for k, v in similar_cocktails.items()]),
        **about 
    }

    return recipe

    
    

def get_html_page(url:str) -> list:
    # Returns a dataframe of all the recipes
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    print(f"Page: {url}")
    
    page_recipes = list()
    # Loop through the actual recipes
    for idx, rec in enumerate(soup.find_all('div', {"class": "col-md-2"})):
        try:
            recipe_url = f"{main_url}{rec.find('a').get('href')}"
            recipe = parse_recipe(recipe_url) 
            page_recipes.append(recipe)
        except AttributeError as e:
            print(rec, 'href link doesnt work')
    
    return page_recipes

def format_df(all_recipes:list) -> pd.DataFrame():
    with_idx = {idx: x for idx, x in enumerate(all_recipes)}

    return pd.DataFrame().from_dict(with_idx, orient='index')

if __name__ == '__main__':
    r = requests.get(landing_page)
    soup = BeautifulSoup(r.text, 'html.parser')
    #num_items = int(soup.find('span', {'class': 'pull-right'}).text.split(' ')[0])
    MAX_PAGES = 849
    
    all_recipes = list()
    # Paginate through all the recipes
    for p in range(3):
        print(f"page={p}")
        format_str = f"{landing_page}&page={p}"
        all_recipes.extend(get_html_page(format_str))

    df = format_df(all_recipes)

    df.to_csv('recipes.csv', index=False)
    
    

