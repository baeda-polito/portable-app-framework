import os

import pandas as pd
from brickschema import Graph

from src.portable_app_framework import Application

df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})


def load_ttl(name: str) -> Graph:
    """
    Load a ttl file into a graph
    :param name: The ttl name
    :return graph: The graph object
    """
    graph = Graph()
    local_file_path = os.path.join("test", "data", name)
    graph.parse(local_file_path, format="ttl")
    return graph


def test_always_passes():
    assert True


# def test_always_fails():
#     assert False


def test_qualify_pass():
    """
    Test that the qualify returns True
    :return:
    """
    app = Application(
        metadata=load_ttl("test_qualify_pass.ttl"),
        app_name='app_test'
    )
    res = app.qualify()

    assert res is True


def test_qualify_fail():
    """
    Test that the qualify returns False
    :return:
    """
    app = Application(
        metadata=load_ttl("test_qualify_fail.ttl"),
        app_name='app_test'
    )
    res = app.qualify()

    assert res is False


def test_fetch_dict():
    """
    Test that the fetch returns dictionary
    :return:
    """
    app = Application(
        metadata=load_ttl("test_fetch_dict.ttl"),
        app_name='app_test'
    )
    res = app.fetch()

    assert type(res) == type({})


def test_remap():
    """
    Test that the fetch returns dictionary
    :return:
    """
    app = Application(
        metadata=load_ttl("test_fetch_dict.ttl"),
        app_name='app_test'
    )
    res = app.fetch()
    fetch_mapping_dictionary = res[0]

    # create a dataframe
    df_mock = pd.DataFrame({'t_mix': [1, 2, 3], 'ahu': [1, 1, 1]})
    
    # remap the dataframe to external
    df_to_external = app.remap(data=df_mock, fetch_map_dict=fetch_mapping_dictionary, mode='to_external')
    print(df_to_external)
    first_check = list(df_to_external.columns).sort() == list(fetch_mapping_dictionary.values()).sort()

    # remap the dataframe to internal
    df_to_internal = app.remap(data=df_to_external, fetch_map_dict=fetch_mapping_dictionary, mode='to_internal')
    print(df_to_internal)
    second_check = list(df_to_internal.columns).sort() == list(fetch_mapping_dictionary.keys()).sort()

    assert all([first_check, second_check]) is True

# def test_change_name():
#     """
#     Test that if name change the fetch doesnt fail
#     :return:
#     """
#     app = Application(
#         metadata=load_ttl("test_fetch_dict.ttl"),
#         app_name='app_test'
#     )
#     res = app.fetch()
#
#     assert type(res) == type({})
