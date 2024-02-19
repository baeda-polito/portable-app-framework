import brickschema
import pandas as pd
from portable_app_framework import Application

from src.portable_app_framework import Application

df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})


def test_always_passes():
    assert True


def test_always_fails():
    assert False


def test_load_app():
    app = Application(
        data=df,
        metadata=brickschema.Graph(),
        app_name='app_test'
    )
    assert app is not None
