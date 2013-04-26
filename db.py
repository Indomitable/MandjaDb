import sqlite3 as lite
import os


class TableCreate:

    def __init__(self, constr):
        self.constr = constr
        self.del_db()
        self.con = lite.connect(self.constr)

    def del_db(self):
        if os.path.exists(self.constr):
            os.remove(self.constr)

    def create_tables(self):
        self.create_advice()
        self.create_categories()
        self.create_db_version()
        self.create_products()
        self.create_spices()
        self.create_recipes()
        self.create_favorite_recipes()
        self.create_recipe_category()
        self.create_recipe_notes()
        self.create_recipe_of_the_day()
        self.create_meta_data_table()
        self.con.close()

    def create_advice(self):
        self.con.execute("""CREATE TABLE ADVICES (
    ID            INTEGER PRIMARY KEY
                          NOT NULL,
    THUMBNAIL_URL TEXT,
    IMAGE_URL     TEXT,
    TITLE         TEXT,
    DESCRIPTION   TEXT
)""")

    def create_categories(self):
        self.con.execute("""CREATE TABLE CATEGORIES (
    ID        INTEGER PRIMARY KEY
                      NOT NULL,
    TITLE     TEXT,
    PARENT_ID INTEGER,
    CONSTRAINT 'parent_category_fk' FOREIGN KEY ( PARENT_ID ) REFERENCES CATEGORIES ( ID )
)""")

    def create_db_version(self):
        self.con.execute("""CREATE TABLE DB_VERSION (
    VERSION INT
)""")

    def create_products(self):
        self.con.execute("""CREATE TABLE PRODUCTS (
    ID            INTEGER PRIMARY KEY
                          NOT NULL,
    THUMBNAIL_URL TEXT,
    IMAGE_URL     TEXT,
    TITLE         TEXT,
    DESCRIPTION   TEXT
)""")

    def create_spices(self):
        self.con.execute("""CREATE TABLE SPICES (
    ID            INTEGER PRIMARY KEY
                          NOT NULL,
    THUMBNAIL_URL TEXT,
    IMAGE_URL     TEXT,
    TITLE         TEXT,
    DESCRIPTION   TEXT
)""")

    def create_recipes(self):
        self.con.execute("""CREATE TABLE RECIPES (
    ID            INTEGER PRIMARY KEY
                          NOT NULL,
    THUMBNAIL_URL TEXT,
    IMAGE_URL     TEXT,
    TITLE         TEXT,
    PRODUCTS      TEXT,
    DESCRIPTION   TEXT,
    PREPARE_TIME  TEXT,
    COOK_TIME     TEXT,
    PORTIONS      TEXT
)""")

    def create_favorite_recipes(self):
        self.con.execute("""CREATE TABLE FAVORITE_RECIPES (
    RECIPE_ID INTEGER PRIMARY KEY
                      NOT NULL,
    CONSTRAINT 'favorite_recipe_fk' FOREIGN KEY ( RECIPE_ID ) REFERENCES RECIPES ( ID )
)""")

    def create_recipe_category(self):
        self.con.execute("""CREATE TABLE RECIPE_CATEGORY (
    RECIPE_ID   INTEGER NOT NULL
                        CONSTRAINT 'category_recipe_fk' REFERENCES RECIPES ( ID ),
    CATEGORY_ID INTEGER NOT NULL
                        CONSTRAINT 'recipe_category_fk' REFERENCES CATEGORIES ( ID ),
    CONSTRAINT 'RECIPE_CATEGORY_PK' PRIMARY KEY ( RECIPE_ID, CATEGORY_ID )
)""")

    def create_recipe_notes(self):
        self.con.execute("""CREATE TABLE RECIPE_NOTES (
    RECIPE_ID INTEGER PRIMARY KEY
                      NOT NULL,
    NOTE      TEXT,
    CONSTRAINT 'note_recipe_fk' FOREIGN KEY ( RECIPE_ID ) REFERENCES RECIPES ( ID )
)""")

    def create_recipe_of_the_day(self):
        self.con.execute("""CREATE TABLE RECIPE_OF_THE_DAY (
    DAY       DATE    PRIMARY KEY
                      NOT NULL,
    RECIPE_ID INTEGER NOT NULL
)""")

    def create_meta_data_table(self):
        self.con.execute("CREATE TABLE \"android_metadata\" (\"locale\" TEXT DEFAULT 'en_US')");
        self.con.execute("INSERT INTO \"android_metadata\" VALUES ('en_US')")

class DataImport:

    def __init__(self, constr):
        self.constr = constr

    def __insert_data(self, sql, data):
        con = lite.connect(self.constr)
        with con:
            cur = con.cursor()
            cur.executemany(sql, data)

    def insert_categories(self, category_list):
        id = 1
        temp_category_list = []
        for category in category_list:
            category.id = id
            temp_category_list.append((category.id, category.name, 0))
            id = self.__build_sub_categories(id, category, temp_category_list)
            id += 1

        self.__insert_data("INSERT INTO CATEGORIES VALUES(?, ?, ?)", temp_category_list)
        return category_list

    def __build_sub_categories(self, id, parent_category, temp_category_list):
        for category in parent_category.sub_categories:
            id += 1
            category.id = id
            temp_category_list.append((category.id, category.name, parent_category.id))
            id = self.__build_sub_categories(id, category, temp_category_list)
        return id

    def insert_recipes(self, recipe_list):
        id = 1
        temp_recipe_list = []
        for recipe in recipe_list:
            recipe.id = id
            temp_recipe_list.append((id, recipe.thumbnail_url, recipe.image_url, recipe.title, recipe.products, recipe.description, recipe.prepare_time, recipe.cook_time, recipe.portions))
            id += 1

        self.__insert_data("INSERT INTO RECIPES (ID, THUMBNAIL_URL, IMAGE_URL, TITLE, PRODUCTS, DESCRIPTION, PREPARE_TIME, COOK_TIME, PORTIONS) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", temp_recipe_list)
        return recipe_list

    def insert_category_recipes(self, category_recipe_list):
        self.__insert_data("INSERT INTO RECIPE_CATEGORY(CATEGORY_ID, RECIPE_ID) VALUES (?, ?)", category_recipe_list)

    def process_useful(self, useful_list):
        id = 1
        temp_useful_list = []
        for useful in useful_list:
            useful.id = id
            temp_useful_list.append((id, useful.thumbnail_url, useful.image_url, useful.title, useful.description))
            id += 1
        return temp_useful_list

    def insert_advices(self, advice_list):
        self.__insert_data("INSERT INTO ADVICES (ID, THUMBNAIL_URL, IMAGE_URL, TITLE, DESCRIPTION) VALUES (?, ?, ?, ?, ?)", self.process_useful(advice_list))

    def insert_spices(self, spice_list):
        self.__insert_data("INSERT INTO SPICES (ID, THUMBNAIL_URL, IMAGE_URL, TITLE, DESCRIPTION) VALUES (?, ?, ?, ?, ?)", self.process_useful(spice_list))

    def insert_products(self, product_list):
        self.__insert_data("INSERT INTO PRODUCTS (ID, THUMBNAIL_URL, IMAGE_URL, TITLE, DESCRIPTION) VALUES (?, ?, ?, ?, ?)", self.process_useful(product_list))


class DataExport:

    def __init__(self, constr):
        self.constr = constr

    def __get_data(self, sql):
        con = lite.connect(self.constr)
        try:
            with con:
                cur = con.cursor()
                cur.execute(sql)
                return cur.fetchall()
        finally:
            if con:
                con.close()

    def get_category_recipes(self):
        sql = "select * from RECIPE_CATEGORY"
        return self.__get_data(sql)

    def get_catetories(self):
        sql = "select * from CATEGORIES"
        return self.__get_data(sql)

    def get_recipes(self):
        sql = "select * from RECIPES"
        return self.__get_data(sql)