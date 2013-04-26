__author__ = 'vmladenov'


class Category:

    def __init__(self):
        self.id = -1
        self.name = ""
        self.url = ""
        self.sub_categories = []

    def __str__(self):
        return self.name


class Recipe:

    def __init__(self):
        self.id = -1
        self.title = ""
        self.site_id = -1
        self.products = ""
        self.description = ""
        self.image_url = ""
        self.thumbnail_url = ""
        self.prepare_time = ""
        self.cook_time = ""
        self.portions = ""

    def __str__(self):
        return self.title


class Useful:

    def __init__(self):
        self.id = -1
        self.title = ""
        self.description = ""
        self.image_url = ""
        self.thumbnail_url = ""

    def __str__(self):
        return self.title


class Advice(Useful):
    pass


class Spice(Useful):
    pass


class Product(Useful):
    pass


class UsefulType:
    Advice, Spice, Product = range(3)


class UsefulFactory:

    def create_useful(self, type):
        if type == UsefulType.Advice:
            return Advice()
        elif type == UsefulType.Product:
            return Product()
        else:
            return Spice()