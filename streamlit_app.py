import streamlit as st
import streamlit_utils as stu
import pandas as pd

def set_recipe(i, url):
    state.recipes[i] = url
    
def timefmt(minutes):
    hours = minutes//60
    if hours:
        minutes = minutes%60
        if minutes:
            return f"{hours} {'timer' if hours>1 else 'time'} {minutes}min"
        else:
            return f"{hours} {'timer' if hours>1 else 'time'}"
    else:
        return f"{minutes}min"


def build_menu_ui(state):
    st.header("Menu:")
    state.servings = st.number_input("Kuverter:", min_value=1.0, value=2.5, step=0.5)
    recipe_divs = []
    urls = []
    for i, recipe in enumerate(state.recipes):
        recipe_divs.append(st.container())
        columns = st.columns([10,1,1])
        url = columns[0].text_input(f"recipe url", value=recipe, placeholder="https://www.valdemarsro.dk/...", key=f"url_field_{i}", label_visibility="collapsed")
        columns[1].button("↻", use_container_width=True, key=f"rerun_{i}", on_click=lambda i=i: set_recipe(i, stu.suggest_recipe()))
        columns[2].button("❌", use_container_width=True, key=f"delete_{i}", on_click=lambda i=i: state.recipes.pop(i))
        urls.append(url)
    state.recipes = urls
    st.button("Tilføj måltid", on_click=lambda: state.recipes.append(stu.suggest_recipe()))
    return recipe_divs

state = stu.state()
recipe_divs = build_menu_ui(state)


# Build content
basket = {}
for div, recipe_url in zip(recipe_divs, state.recipes):
    if recipe_url:
        recipe = stu.get_recipe(recipe_url)
        ingredient_count = len(recipe.ingredients())
        with div:
            columns = st.columns([10,2])
            columns[0].markdown(f"#### [{recipe.title()}]({recipe_url}) [{timefmt(recipe.total_time())}] {'' if ingredient_count else '!Ingredients missing!'}")
            columns[1].markdown(f'<img src="{recipe.image()}" width="100%" style="padding: 8px 0px 8px 0px;" />', unsafe_allow_html=True)
        for ingredient in stu.collect_ingredients(recipe_url, servings=state.servings):
            basket.setdefault(ingredient["item"], []).append(ingredient["amount"])

if basket:
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
    combined_basket["købt"] = combined_basket.item.str.match(".*(oregano|paprika|olivenolie|timian).*") | combined_basket.item.isin({"vand", "salt og peber", "salt", "peber"})
    combined_basket.sort_values(["købt", "item"], inplace=True)
    combined_basket.set_index("amounts", drop=True, inplace=True)

    st.header("Inkøbsliste:")
    n_rows = len(combined_basket)
    edit_combined_basket = st.experimental_data_editor(combined_basket, use_container_width=True, num_rows="dynamic", height=int(35*(n_rows+8)))

#st.write(str(ingredients))
#st.dataframe(edit_combined_basket, use_container_width=True)

