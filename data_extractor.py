#from urllib.parse import quote
from urllib.parse import *

__author__ = 'vmladenov'
from http.client import HTTPConnection
from bs4 import BeautifulSoup
from bs4.element import Tag
from data_objects import *


class BaseExtractor:
    site_url = "www.gotvetesmen.com"

    def _parse_description(self, tag):
        return "\n".join(x.replace("\r\n", "") for x in tag.stripped_strings)

    def _get_content(self, url):
        con = HTTPConnection(self.site_url)
        encoded_url = quote(unquote(url), "/=?&")
        print(encoded_url)
        con.request('GET', encoded_url)
        response = con.getresponse()
        return response.read()


class CategoriesExtractor(BaseExtractor):

    def __extract_link_tag(self, link_tag):
        text = link_tag.string
        bracket_index = text.rfind(" (")
        if bracket_index > -1:
            text = text[:bracket_index]
        return text.strip(), link_tag["href"].lower().replace(" ", "%20")

    def __process_list(self, tlist, categories):
        category_tags = tlist.find_all("li")
        for category_tag in category_tags:
            category = Category()
            category_link_tag = category_tag.find("a")
            category.name, category.url = self.__extract_link_tag(category_link_tag)
            categories.append(category)

    def get_categories(self):
        url = "/recipes/categories/"
        content = self._get_content(url)
        soup = BeautifulSoup(content)
        divs = soup.find_all("div", class_='box_bg')
        categories = []
        for div in divs:
            category_tags = div.find_all("h3")
            for category_tag in category_tags:
                category = Category()
                category.name = category_tag.string
                self.__process_list(category_tag.next_sibling, category.sub_categories)
                categories.append(category)
        return categories

    def __get_two_list_categories(self, url):
        content = self._get_content(url)
        soup = BeautifulSoup(content)
        categories = []
        left_list = soup.find("ul", class_="link_list fl")
        self.__process_list(left_list, categories)
        right_list = soup.find("ul", class_="link_list fr")
        self.__process_list(right_list, categories)
        return categories

    def get_international_categories(self):
        url = "/recipes/categories/INTERNATIONALE/Australian_cuisine/"
        return self.__get_two_list_categories(url)

    def get_povod_categories(self):
        url = "/recipes/categories/HOLIDAY/NEW_YEAR/"
        return self.__get_two_list_categories(url)

    def get_10_groups_categories(self):
        url = "/top/no-meat/"
        return self.__get_two_list_categories(url)


class CategoryRecipesExtractor(BaseExtractor):
    def __init__(self, category):
        self.category = category

    def ___get_receipes_in_page(self, url, page_number):
        content = self._get_content(url + str(page_number))
        soup = BeautifulSoup(content)
        recipe_div_tags = soup.find_all("div", class_="box_l alist")
        recipe_site_ids = []
        for recipe_div_tag in recipe_div_tags:
            recipe_link_tag = recipe_div_tag.find("a")
            if not (recipe_link_tag is None):
                href = recipe_link_tag["href"]
                if href.startswith("recipe_"):
                    recipe_site_ids.append(int(href[7:href.find(".")]))
        return recipe_site_ids

    def get_recipes_in_category(self):
        url = self.category.url + "?pageID="
        all_recipe_ids = []
        page_number = 1
        recipe__site_ids = self.___get_receipes_in_page(url, page_number)
        while len(recipe__site_ids) > 0 and not(len(set(recipe__site_ids) | set(all_recipe_ids)) == len(all_recipe_ids)):
            all_recipe_ids = all_recipe_ids + recipe__site_ids
            page_number += 1
            recipe__site_ids = self.___get_receipes_in_page(url, page_number)
        return all_recipe_ids


class RecipeExtractor(BaseExtractor):

    def __parse_timer(self, tag, recipe):
        data = list(tag.stripped_strings)
        header = data[0].lower()
        if header == "подготовка:":
            recipe.prepare_time = data[1]
        elif header == "готвене:":
            recipe.cook_time = data[1]
        elif header == "порции:":
            recipe.portions = data[1]

    def ___get_recipe(self, number):
        url = "/recipes/alphabet_list?id=" + str(number)
        content = self._get_content(url)
        soup = BeautifulSoup(content)
        recipe_div = soup.find("div", id="recipe")
        recipe = Recipe()
        recipe_title_tag = recipe_div.find("h1")
        recipe.title = recipe_title_tag.string
        if recipe.title is None:
            return
        recipe.site_id = number

        timers = recipe_div.find_all("div", class_="r_time")
        for timer in timers:
            self.__parse_timer(timer, recipe)

        products_tag = recipe_div.find("div", class_="products")
        if not(products_tag is None):
            recipe.products = self._parse_description(products_tag)
            if recipe.products.startswith("Продукти:\n"):
                recipe.products = recipe.products[10:]

        description_tag = recipe_div.find("div", class_="description")
        recipe.description = self._parse_description(description_tag)
        if recipe.description.startswith("Приготвяне:\n"):
            recipe.description = recipe.description[12:]

        recipe_image_div = recipe_div.find("div", class_="fl sr")
        recipe_image_link_tag = recipe_image_div.find("a")
        recipe.image_url = recipe_image_link_tag["href"].lower().replace(" ", "%20")
        if recipe.image_url.startswith("javascript"):
            recipe.image_url = ""
            recipe.thumbnail_url = ""
        else:
            if recipe.image_url.startswith("http://"):
                recipe.image_url = recipe.image_url[7:]
            recipe.thumbnail_url = self.site_url + "/images/recipes/thumbs_60/" + recipe.image_url[(recipe.image_url.rfind("/") + 1):]

        return recipe

    def get_recipes(self):
        recipes = []
        for i in range(1, 5500):
            recipe = self.___get_recipe(i)
            if not(recipe is None):
                recipes.append(recipe)
        return recipes

    def get_recipe(self, rid):
        return self.___get_recipe(rid)


class BaseUsefulExtractor(BaseExtractor):

    def _get_useful(self, url, utype):
        factory = UsefulFactory()
        obj = factory.create_useful(utype)
        content = self._get_content(url)
        soup = BeautifulSoup(content)
        main_content_tag = soup.find("div", id="main_content")
        div_tag = main_content_tag.find("div", class_="box_l alist")
        if div_tag is None:
            return None
        image_link_tag = div_tag.find_next("a")
        if not(image_link_tag is None) and isinstance(image_link_tag.next_element, Tag) and image_link_tag.next_element.name == "img":
            obj.image_url = self.site_url + image_link_tag.find("img")["src"].lower()
        title_tag = div_tag.find_next("h1")
        obj.title = title_tag.string.upper()
        obj.description = self._parse_description(title_tag.find_next("div"))
        return obj


class AdvicesExtractor(BaseUsefulExtractor):

    def __get_advices_for_category(self, category_url):
        advices = []
        content = self._get_content(category_url)
        soup = BeautifulSoup(content)
        div_tags = soup.find_all("div", class_="box_l alist")
        for div_tag in div_tags:
            advice_link_tag = div_tag.find_next("a")
            if advice_link_tag["href"].startswith(category_url):
                advice = self._get_useful(advice_link_tag["href"], UsefulType.Advice)
                if advice is None:
                    continue
                img_tag = advice_link_tag.find("img")
                if not(img_tag is None):
                    advice.thumbnail_url = self.site_url + img_tag["src"].lower()
                advices.append(advice)
        return advices

    def __proces_list(self, plist):
        advices = []
        advice_category_tags = plist.find_all("a")
        for advice_category_tag in advice_category_tags:
            if advice_category_tag["href"].startswith("/useful/advices"):
                advices += self.__get_advices_for_category(advice_category_tag["href"])
        return advices

    def get_advices(self):
        url = "/useful/advices/"
        content = self._get_content(url)
        soup = BeautifulSoup(content)
        plist = soup.find("ul", class_="link_list fl")
        advices = self.__proces_list(plist)
        plist = soup.find("ul", class_="link_list fr")
        advices += self.__proces_list(plist)
        return advices


class AlphabetUsefulExtractor(BaseUsefulExtractor):

    def __fetch_page(self, base_url, letter_url, page):
        page_data = []
        page_url = "&pageID=" + str(page)
        content = self._get_content(base_url + letter_url + page_url)
        soup = BeautifulSoup(content)
        main_content_tag = soup.find("div", id="main_content")
        div_tags = main_content_tag.find_all("div", class_="box_l alist")
        if len(div_tags) == 0:
            return page_data
        for div_tag in div_tags:
            image_link_tag = div_tag.find_next("a")
            if image_link_tag["href"].startswith(letter_url):
                useful = self._get_useful(base_url + image_link_tag["href"], self._type())
                image_tag = image_link_tag.next_element
                if not(image_tag is None):
                    useful.thumbnail_url = self.site_url + image_tag["src"].lower()
                page_data.append(useful)
        return page_data

    def __fech_letter(self, base_url, letter_url):
        data = []
        page = 1
        page_data = self.__fetch_page(base_url, letter_url, page)
        while len(page_data) > 0:
            data += page_data
            page += 1
            page_data = self.__fetch_page(base_url, letter_url, page)

        return data

    def _get_alphabet(self, url):
        alphabet_data = []
        content = self._get_content(url)
        soup = BeautifulSoup(content)
        div_alphabeg_tag = soup.find("div", class_="alphabet")
        alphabet_tags = div_alphabeg_tag.find_all("a")
        for alphabet_tag in alphabet_tags:
            alphabet_data += self.__fech_letter(url, alphabet_tag["href"])
        return alphabet_data


class SpiceExtractor(AlphabetUsefulExtractor):

    def _type(self):
        return UsefulType.Spice

    def get_spices(self):
        url = "/useful/spices/"
        return self._get_alphabet(url)


class ProductExtractor(AlphabetUsefulExtractor):

    def _type(self):
        return UsefulType.Product

    def get_products(self):
        url = "/useful/products/"
        return self._get_alphabet(url)