import random
from db import TableCreate, DataImport, DataExport
from main import get_recipe_categories

__author__ = 'vmladenov'

import unittest
from data_extractor import *


class ExtractTests(unittest.TestCase):

    def test_get_categories(self):
        extractor = CategoriesExtractor()
        categories = extractor.get_categories()
        self.assertEqual(len(categories), 27)
        self.assertEqual(categories[1].name, "ПРЕДЯСТИЯ")
        self.assertEqual(len(categories[1].sub_categories), 8)

    def test_get_international_categories(self):
        extractor = CategoriesExtractor()
        categories = extractor.get_international_categories()
        self.assertEqual(len(categories), 42)
        self.assertEqual(len(categories[2].sub_categories), 0)

    def test_get_povod_categories(self):
        extractor = CategoriesExtractor()
        categories = extractor.get_povod_categories()
        self.assertEqual(len(categories), 22)
        self.assertEqual(len(categories[5].sub_categories), 0)

    def test_top_categories(self):
        extractor = CategoriesExtractor()
        categories = extractor.get_10_groups_categories()
        self.assertEqual(len(categories), 93)
        self.assertEqual(categories[1].name, "Рецепти от индийската кухня")
        self.assertEqual(len(categories[1].sub_categories), 0)

    def test_get_recipes_in_category(self):
        category_extractor = CategoriesExtractor()
        categories = category_extractor.get_10_groups_categories()
        category = next(x for x in categories if x.name == "Рецепти от индийската кухня")
        extractor = CategoryRecipesExtractor(category)
        recipes_in_category = extractor.get_recipes_in_category()
        self.assertEqual(len(recipes_in_category), 5)

    def test_get_recipes_in_category1(self):
        category_extractor = CategoriesExtractor()
        categories = category_extractor.get_categories()
        parent_category = next(x for x in categories if x.name == "НАПИТКИ и КОКТЕЙЛИ")
        for category in parent_category.sub_categories:
            extractor = CategoryRecipesExtractor(category)
            recipes_in_category = extractor.get_recipes_in_category()
            print(recipes_in_category)

        self.assertEqual(len(parent_category.sub_categories), 9)

    def test_get_recipe_exists(self):
        extractor = RecipeExtractor()
        recipe = extractor.get_recipe(56)
        self.assertEqual(recipe.title, "Моркови с майонеза")
        self.assertEqual(recipe.products, """500 г моркови
2 ч. л. сол
2 ч. л. захар
2 - 3 с. л. майонеза
3 - 4 с. л. прясно мляко
1 ч. л. горчица
1 ч. л. смлян черен пипер
1 връзка копър
на вкус магданоз
3 -4 стръка зелен лук""")

        self.assertEqual(recipe.description, """• Морковите се обелват и се нарязват на кръгчета.
• 1/2 л вода се кипва заедно със захарта и солта, пускат се морковните кръгчета и се варят около 10-15 минути.
• Изцеждат се и се оставят да изстинат.
• Майонезата, млякото, горчицата, солта, черният пипер се разбъркват добре.
• Добавят се копър, магданоз и зелен лук - ситно нарязани.
• С така приготвена смес се заливат леко топлите моркови.
• Морковите с майонеза се поднасят топли или студени.""")

    def test_get_recipe_not_exists(self):
        extractor = RecipeExtractor()
        recipe = extractor.get_recipe(1)
        self.assertIsNone(recipe)

    def test_get_advices(self):
        extractor = AdvicesExtractor()
        advices = extractor.get_advices()
        self.assertEqual(len(advices), 60)

    def test_get_spices(self):
        extractor = SpiceExtractor()
        spices = extractor.get_spices()
        self.assertEqual(len(spices), 75)

    def test_get_products(self):
        extractor = ProductExtractor()
        products = extractor.get_products()
        self.assertEqual(len(products), 68)

    def test_get_recipe_4215(self):
        extractor = RecipeExtractor()
        recipe = extractor.get_recipe(4215)
        self.assertEqual(recipe.title, "Чийзкейк с пияно грозде")
        self.assertEqual(recipe.prepare_time, "10 мин.")
        self.assertEqual(recipe.portions, "10-12")

    def test_get_recipe_4315(self):
        extractor = RecipeExtractor()
        recipe = extractor.get_recipe(4315)
        self.assertEqual(recipe.title, "Зелева сарма")
        self.assertEqual(recipe.prepare_time, "10 мин.")
        self.assertEqual(recipe.cook_time, "40 мин.")
        self.assertEqual(recipe.portions, "6-8")


class DbTests(unittest.TestCase):

    constr = "../cook.db"

    def setUp(self):
        table_creator = TableCreate(DbTests.constr)
        table_creator.create_tables()
        print("set-up")

    def test_insert_categorie(self):
        category_extractor = CategoriesExtractor()
        categories = category_extractor.get_categories()
        category = random.choice(categories)
        data_importer = DataImport(DbTests.constr)
        data_importer.insert_categories([category])

        data_exporter = DataExport(DbTests.constr)
        inserted_data = data_exporter.get_catetories()

        self.assertEqual(len(inserted_data), len(category.sub_categories) + 1)

    def test_insert_recipes(self):
        recipe_extractor = RecipeExtractor()
        # test 20 recipes
        valid_recipes = []
        for i in range(1, 20):
            recipe_id = random.randrange(10, 5500)
            recipe = recipe_extractor.get_recipe(recipe_id)
            if recipe:
                valid_recipes.append(recipe)

        data_importer = DataImport(DbTests.constr)
        data_importer.insert_recipes(valid_recipes)

        data_exporter = DataExport(DbTests.constr)
        inserted_data = data_exporter.get_recipes()

        self.assertEqual(len(inserted_data), len(valid_recipes))

    def test_insert_category_recipes(self):
        category_extractor = CategoriesExtractor()
        categories = category_extractor.get_categories()
        category = random.choice(categories)
        recipe_ids = []
        records_count = 0
        for sub_category in category.sub_categories:
            recipe_category_extractor = CategoryRecipesExtractor(sub_category)
            recipe_in_categories = recipe_category_extractor.get_recipes_in_category()
            for recipe_in_category in recipe_in_categories:
                records_count += 1
                if not(recipe_in_category in recipe_ids):
                    recipe_ids.append(recipe_in_category)

        recipe_list = []
        recipe_extractor = RecipeExtractor()
        for recipe_id in recipe_ids:
            recipe_list.append(recipe_extractor.get_recipe(recipe_id))

        # table_creator = TableCreate(DbTests.constr)
        # table_creator.create_tables()

        data_importer = DataImport(DbTests.constr)
        data_importer.insert_categories([category])
        data_importer.insert_recipes(recipe_list)

        category_recipe_list = get_recipe_categories([category], recipe_list)
        data_importer.insert_category_recipes(category_recipe_list)

        data_exporter = DataExport(DbTests.constr)
        inserted_data = data_exporter.get_category_recipes()

        self.assertEqual(len(inserted_data), records_count)




if __name__ == '__main__':
    unittest.main()
