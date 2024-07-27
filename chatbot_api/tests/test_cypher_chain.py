from src.langchain_custom.graph_qa.cypher import remove_keys_from_dicts


def test_remove_keys_from_dicts():
    """
    Test function that removes keys from dictionaries
    """
    input_list = [
        {"a": 1, "b": 2, "c": {"d": 4, "e": 5}},
        {"a": 10, "b": 20, "f": {"g": 30, "h": 40}},
        {"i": 100, "j": {"k": 200, "l": 300, "m": {"n": 400}}},
    ]
    keys_to_remove = ["b", "d", "k"]

    expected_output = [
        {"a": 1, "c": {"e": 5}},
        {"a": 10, "f": {"g": 30, "h": 40}},
        {"i": 100, "j": {"l": 300, "m": {"n": 400}}},
    ]

    assert remove_keys_from_dicts(input_list, keys_to_remove) == expected_output
