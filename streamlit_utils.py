import streamlit as st
import basket_generator

from functools import partial

get_unit_registry = st.cache_resource(basket_generator.get_unit_registry)

@st.cache_resource
def collect_ingredients(url):
    return basket_generator.collect_ingredients(url, ureg=get_unit_registry())
