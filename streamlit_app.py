import streamlit as st
import streamlit_utils as stu
import pandas as pd

st.header("Menu:")
url_fields = st.number_input("Dage: ", min_value=1, value=1)

urls = []
for url_field in range(int(round(url_fields))):
    url = st.text_input(f"Dag {url_field}", value="", placeholder="https://www.valdemarsro.dk/...", key=f"url_field_{url_field}")
    urls.append(url)

basket = {}
for url in urls:
    if url:
        for ingredient in stu.collect_ingredients(url):
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

