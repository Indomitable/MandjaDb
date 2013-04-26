from db import *
from data_objects import *
from data_extractor import *


def build_categories():
    categories_extractor = CategoriesExtractor()

    type_recipe_category = Category()
    type_recipe_category.name = "Тип рецепта"
    type_recipe_category.sub_categories = categories_extractor.get_categories()

    type_cuisine_category = Category()
    type_cuisine_category.name = "Тип кухня"
    type_cuisine_category.sub_categories = categories_extractor.get_international_categories()

    type_povod_category = Category()
    type_povod_category.name = "Спрямо повода"
    type_povod_category.sub_categories = categories_extractor.get_povod_categories()

    type_others_category = Category()
    type_others_category.name = "Други групи"
    type_others_category.sub_categories = categories_extractor.get_10_groups_categories()

    return [type_recipe_category, type_cuisine_category, type_povod_category, type_others_category]


def get_recipe_categories(category_list, recipe_list):
    category_recipe_list = []

    def process_sub_category(parent_category):
        for category in parent_category.sub_categories:
            if len(category.url) > 0:
                extractor = CategoryRecipesExtractor(category)
                recipes_in_category = extractor.get_recipes_in_category()
                for recipe in recipe_list:
                    if recipe.site_id in recipes_in_category:
                        category_recipe_list.append((category.id, recipe.id))
            process_sub_category(category)

    for category in category_list:
        process_sub_category(category)

    return category_recipe_list

if __name__ == "__main__":
    con_str = "cook.db"
    table_creator = TableCreate(con_str)
    table_creator.create_tables()

    data_importer = DataImport(con_str)
    category_list = data_importer.insert_categories(build_categories())

    extractor = RecipeExtractor()
    recipe_list = data_importer.insert_recipes(extractor.get_recipes())

    category_recipe_list = get_recipe_categories(category_list, recipe_list)
    data_importer.insert_category_recipes(category_recipe_list)

    advice_extractor = AdvicesExtractor()
    advice_list = advice_extractor.get_advices()

    spice_extractor = SpiceExtractor()
    spice_list = spice_extractor.get_spices()

    product_extractor = ProductExtractor()
    product_list = product_extractor.get_products()

    data_importer.insert_advices(advice_list)
    data_importer.insert_spices(spice_list)
    data_importer.insert_products(product_list)




