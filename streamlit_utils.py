import streamlit as st
import basket_generator
import pandas as pd
from functools import partial
from dataclasses import dataclass
from typing import List

get_unit_registry = st.cache_resource(basket_generator.get_unit_registry)

@st.cache_resource
def get_recipe(url):
    return basket_generator.get_recipe(url)


@st.cache_resource
def collect_ingredients(url, servings=None):
    recipe = get_recipe(url)
    return basket_generator.collect_ingredients(recipe, servings=servings, ureg=get_unit_registry())


@st.cache_resource
def recipe_csv(file):
    return pd.read_csv(file)


def suggest_recipe():
    return recipe_csv("recipes.csv").sample().recipe.values[0]


@dataclass
class State:
    recipes: List[str]
    servings: int


def state():
    if 'session_state_object' not in st.session_state:
        st.session_state['session_state_object'] = State(
            recipes=[suggest_recipe()],
            servings=4,
        )
    return st.session_state['session_state_object']
