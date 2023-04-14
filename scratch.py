from recipe_scrapers import scrape_me
from recipe_scrapers import valdemarsro
import re
from babel.numbers import parse_decimal
from pint import UnitRegistry
import pandas as pd


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

ingredient_blacklist = {"Derudover"}


urls = [
    "https://www.valdemarsro.dk/hjemmelavede-burgere/",
    "https://www.valdemarsro.dk/kyllingelasagne-med-spinat/?antal=2",
    "https://www.valdemarsro.dk/pizza-med-stenbiderrogn/?antal=2",
    "https://www.valdemarsro.dk/vodka-pasta/?antal=2",
    "https://madensverden.dk/kyllingebryst-med-frossen-spinat/"
]

ingredient_pattern = re.compile("(?:(?P<amount>\d*(?:[\.,]\d*)?)\s*(?:(?P<unit>(dl|l|dL|L|tsk|spsk|ds|dåse|g|kg|bk|bakke|fed|håndfuld))\s+)?)?(?P<item>.*)")
all_ingredients = []
for url in urls:
    scrape = scrape_me(url)
    language = scrape.language().split("-")[0]

    ingredients = []
    for ingredient in scrape.ingredients():
        if ingredient in ingredient_blacklist:
            continue

        items = ingredient.strip().split(" ", 2)
        
        try:
            amount = float(parse_decimal(items[0], locale=language))
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
        
    all_ingredients.extend(ingredients)

def combine_sorted_ingredients(ingredients):
    iter_ = iter(ingredients)
    last = next(iter_)
    for ingredient in iter_:
        if ingredient["item"] == last["item"]:
            try:
                last["amount"] += ingredient["amount"]
            except TypeError:
                yield last
                last = ingredient
                # Not able to combine
        else:
            yield last
            last = ingredient
    yield last

basket = {}
for ingredient in all_ingredients:
    basket.setdefault(ingredient["item"], []).append(ingredient["amount"])

combined_basket = {}
for item, amounts in basket.items():
    s_amounts = sorted(amounts, key=lambda x: str(x.to_base_units().u))
    c_amounts = [s_amounts[0]]
    for amount in s_amounts[1:]:
        try:
            c_amounts[-1] = c_amounts[-1] + amount
        except TypeError:
            c_amounts.append(amount)
    combined_basket[item] = c_amounts

combined_basket = pd.DataFrame(combined_basket.items(), columns=["item", "amounts"])
combined_basket["amounts"] = combined_basket["amounts"].apply(
    lambda a: " + ".join(map(lambda x: f"{round(x,2):~P}", a))
)
combined_basket["basis"] = combined_basket.item.str.match(".*(oregano|salt|peber|paprika|olivenolie|timian).*") | combined_basket.item.isin({"vand"})


fmtstr = f'{{:<{combined_basket["item"].str.len().max()}}}'
print(combined_basket.sort_values(["basis", "item"]).to_string(index=False, columns=["amounts", "item"], header=False, formatters={'item': (lambda x: fmtstr.format(x))}))

a = 1+1
