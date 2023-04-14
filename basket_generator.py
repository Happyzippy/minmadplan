from recipe_scrapers import scrape_me
from recipe_scrapers import valdemarsro
import re
from babel.numbers import parse_decimal
from pint import UnitRegistry
import pandas as pd

def get_unit_registry():
    ureg = UnitRegistry()
    ureg.define('teske = 1 teaspoon = tsk')
    ureg.define('spiseske = 1 tablespoon = spsk')
    ureg.define('bakke = 1 = bk')
    ureg.define('@alias bakke = bakker = bk')
    ureg.define('dåse = 1 = ds')
    ureg.define('@alias dåse = dåser = dåser')
    ureg.define('fed = 1 = fed')
    ureg.define('håndfuld = 1 = håndfuld')
    ureg.define('@alias håndfuld = håndfulde = håndfulde')
    ureg.define('@alias teske = teskefulde = tsk')
    ureg.define('styk = count = stk')
    ureg.define('@alias styk = styk = stk.')
    ureg.define('person = 1 = pers')
    return ureg

ingredient_blacklist = {"Derudover"}

def get_recipe(url):
    return scrape_me(url)

def collect_ingredients(recipe, servings=None, ureg: UnitRegistry = None):
    language = recipe.language().split("-")[0]
    if servings is not None:
        multiplier = servings / ureg(recipe.yields()).m
    else:
        multiplier = 1

    ingredients = []
    for ingredient in recipe.ingredients():
        if ingredient in ingredient_blacklist:
            continue

        items = ingredient.strip().split(" ", 2)
        
        try:
            amount = multiplier * float(parse_decimal(items[0], locale=language))
            try:
                amount = amount * ureg(items[1])
                item = items[2]
            except Exception:
                amount = amount * ureg.dimensionless
                item = " ".join(items[1:])
        except Exception:
            amount = 1.0 * ureg.dimensionless
            item = ingredient
        
        
        ingredients.append({
            "amount": amount,
            "item": item,
        })
    
    return ingredients
