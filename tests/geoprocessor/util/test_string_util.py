import pytest
import geoprocessor.util.string_util as string_util


# Tests for delimited_string_to_list()
def test_delimited_string_to_list_simple_example():
    """ Test that basic usage of this function works properly. """
    string = "a,b,c,d"
    delimiter = ","
    assert string_util.delimited_string_to_list(string, delimiter) == ['a', 'b', 'c', 'd']


def test_delimited_string_to_list_ending_with_delimiter():
    """ Test a string ending with delimiter. """
    string = "a,b,c,d,"
    delimiter = ","
    assert string_util.delimited_string_to_list(string, delimiter) == ['a', 'b', 'c', 'd', '']


# Test that this function works with different types of delimiters
@pytest.mark.parametrize("string, delimiter, expected", [
    ("a,b,c,d", ",", ['a', 'b', 'c', 'd']),  # test delimiter ","
    ("a.b.c.d", ".", ['a', 'b', 'c', 'd']),  # test delimiter "."
    ("azbzczd", "z", ['a', 'b', 'c', 'd']),  # test delimiter "z"
])
def test_delimited_string_to_list_with_different_delimiters(string, delimiter, expected):
    """ Using parametrized function above to test function with different types of delimiters. """
    assert string_util.delimited_string_to_list(string, delimiter) == expected


def test_delimited_string_to_list_empty_string():
    """ Test the function with an empty string. """
    string = ""
    # assert string_util.delimited_string_to_list(list) == None
    assert string_util.delimited_string_to_list(string) == ['']


# Test stripping whitespace v. not stripping white space
@pytest.mark.parametrize("string,delimiter,whitespace,expected", [
    ("a,  b,  c   ,d  ", ',', True, ['a', 'b', 'c', 'd']),  # test removing whitespace
    ("a,  b,  c   ,d  ", ',', False, ['a', '  b', '  c   ', 'd  ']),  # test leaving whitespace
])
def test_delimited_string_to_list_whitespace(string, delimiter, whitespace, expected):
    """ Test function with strip whitespace = True and strip whitespace = False. """
    assert string_util.delimited_string_to_list(string, delimiter, whitespace) == expected


# Tests for delimited_string_to_dictionary_one_value
def test_delimited_string_to_dictionary_one_value_simple_example():
    """ Test a basic example of this function. """
    string = "key1=a;key2=b;key3=c"
    entry_delimiter = ";"
    key_delimiter = "="
    assert string_util.delimited_string_to_dictionary_one_value(string, entry_delimiter, key_delimiter) \
            == {'key1': 'a', 'key2': 'b', 'key3': 'c'}


def test_delimited_string_to_dictionary_one_value_ending_with_delimiter_raises_exception():
    """ Test what happens when passing an invalid string format. Should return ValueError. """
    string = "key1=a;key2=b;key3=c;"
    entry_delimiter = ";"
    key_delimiter = "="
    with pytest.raises(ValueError):
        string_util.delimited_string_to_dictionary_one_value(string, entry_delimiter, key_delimiter)


# Test multiple kinds of delimiter combinations
@pytest.mark.parametrize("string,entry_delimiter,key_delimiter,expected", [
    ("key1=a,key2=b,key3=c", ",", "=", {'key1': 'a', 'key2': 'b', 'key3': 'c'}),
    ("key1=a.key2=b.key3=c", ".", "=", {'key1': 'a', 'key2': 'b', 'key3': 'c'}),
    ("key1.a;key2.b;key3.c", ";", ".", {'key1': 'a', 'key2': 'b', 'key3': 'c'})
])
def test_delimited_string_to_dictionary_one_value_with_different_delimiters(string, entry_delimiter, key_delimiter,
                                                                            expected):
    """ Test different combination of delimiters. """
    assert string_util.delimited_string_to_dictionary_one_value(string, entry_delimiter, key_delimiter) == expected


# Test multiple kinds of delimiter combinations
@pytest.mark.parametrize("string,entry_delimiter,key_delimiter", [
    ("key1=a,key2=b,key3=c", ";", "="),
    ("key1=a;key2=b;key3=c", ";", "==")
])
def test_delimited_string_to_dictionary_one_value_with_bad_delimiter_format(string, entry_delimiter, key_delimiter):
    """ Test passing invalid delimiters to the function. Should return ValueError. """
    with pytest.raises(ValueError):
        string_util.delimited_string_to_dictionary_one_value(string, entry_delimiter, key_delimiter)


def test_delimited_string_to_dictionary_one_value_empty_string():
    """ Test function with an empty string. """
    string = ""
    assert string_util.delimited_string_to_dictionary_one_value(string) == {}


def test_delimited_string_to_dictionary_one_value_none_string():
    """ Test function with None string. """
    string = None
    assert string_util.delimited_string_to_dictionary_one_value(string) == None


# Test trimming whitespace or not
@pytest.mark.parametrize("string,entry_delimiter,key_delimiter,whitespace,expected", [
    ("key1=a;key2=  b;key3=  c  ;key4=d  ", ";", "=", True, {'key1': 'a', 'key2': 'b', 'key3': 'c', 'key4': 'd'}),
    ("key1=a;key2=  b;key3=  c  ;key4=d  ", ";", "=", False,
     {'key1': 'a', 'key2': '  b', 'key3': '  c  ', 'key4': 'd  '})
])
def test_delimited_string_to_dictionary_one_value_whitespace(string, entry_delimiter, key_delimiter, whitespace,
                                                             expected):
    """ Test trimming whitespace or not. """
    assert string_util.delimited_string_to_dictionary_one_value(string, entry_delimiter, key_delimiter, whitespace) \
           == expected


# Tests for delimited_string_to_dictionary_list_value()
def test_delimited_string_to_dictionary_list_value_simple_example():
    """ Test the basic functionality of this function. """
    string = "key1=value1,value1b,value1c;key2=value2"
    entry_delimiter = ";"
    key_delimiter = "="
    list_delimiter = ","
    assert \
        string_util.delimited_string_to_dictionary_list_value(string, entry_delimiter, key_delimiter, list_delimiter) \
           == {'key1': ['value1', 'value1b', 'value1c'], 'key2': ['value2']}


@pytest.mark.parametrize("string,entry_delimiter,key_delimiter,list_delimiter,expected", [
    ("key1=a,b,c;key2=d", ";", '=', ',', {'key1': ['a', 'b', 'c'], 'key2': ['d']}),
    ("key1=a,b,c.key2=d", ".", '=', ',', {'key1': ['a', 'b', 'c'], 'key2': ['d']}),
    ("key1.a,b,c;key2.d", ";", '.', ',', {'key1': ['a', 'b', 'c'], 'key2': ['d']}),
    ("key1=a.b.c;key2=d", ";", '=', '.', {'key1': ['a', 'b', 'c'], 'key2': ['d']}),
])
def test_delimited_string_to_dictionary_list_value_with_different_delimters(string, entry_delimiter, key_delimiter,
                                                                            list_delimiter, expected):
    """ Test this function using different combinations of delimiters. """
    assert string_util.delimited_string_to_dictionary_list_value(string, entry_delimiter, key_delimiter,
                                                                 list_delimiter) == expected


def test_delimited_string_to_dictionary_list_value_none_string():
    """ Test with a string set to None. """
    string = None
    assert string_util.delimited_string_to_dictionary_list_value(string) == None


def test_delimited_string_to_dictionary_list_value_empty_string():
    """ Test with an empty string. """
    string = ""
    assert string_util.delimited_string_to_dictionary_list_value(string) == {}


# Test trim whitespace v do not trim whitespace
@pytest.mark.parametrize("string,entry_delimiter,key_delimiter,list_delimiter,whitespace,expected", [
    ("key1=a,  b,  c  ;key2=d  ", ';', '=', ',', True, {'key1': ['a', 'b', 'c'], 'key2': ['d']}),
    ("key1=a,  b,  c  ;key2=d  ", ';', '=', ',', False, {'key1': ['a', '  b', '  c  '], 'key2': ['d  ']})
])
def test_delimited_string_to_dictionary_list_value_whitespace(string, entry_delimiter, key_delimiter, list_delimiter,
                                                              whitespace, expected):
    """ Test trimming whitespace versus not trimming whitespace. """
    assert string_util.delimited_string_to_dictionary_list_value(string, entry_delimiter, key_delimiter, list_delimiter,
                                                                 whitespace) \
           == expected


def test_delimited_string_to_dictionary_list_value_invalid_string_format():
    """ Test passing an invalid string to function. Should return ValueError. """
    string = "key1=a,b,c;key=d;"
    with pytest.raises(ValueError):
        string_util.delimited_string_to_dictionary_list_value(string, ";", "=", ",")


# Test passing incorrect delimiter's to function
@pytest.mark.parametrize("string,entry_delimiter,key_delimiter,list_delimiter", [
    ("key1=a,b,c;key2=d", ".", "=", ","),
    ("key1=a,b,c;key2=d", ";", ".", ","),
    # ("key1=a,b,c;key2=d", ";", "=", ".") this seems like it should produce an error
])
def test_delimited_string_to_dictionary_list_value_invalid_dilimiter_format(string, entry_delimiter, key_delimiter,
                                                                            list_delimiter):
    """ Test what happens when passing an incorrect delimiter to a function. """
    with pytest.raises(ValueError):
        string_util.delimited_string_to_dictionary_list_value(string, entry_delimiter, key_delimiter, list_delimiter)


def test_delimited_string_to_dictionary_list_value_single_values_only():
    """ Test passing a single value to each key. """
    string = "key1=a;key2=b"
    entry_delimiter = ";"
    key_delimiter = "="
    assert string_util.delimited_string_to_dictionary_list_value(string, entry_delimiter, key_delimiter) \
           == {'key1': ['a'], 'key2': ['b']}


# TODO @jurentie 02/26/2019 - cannot figure out how to test this function
# Tests for filter_list_of_strings functions
# def test_filter_list_of_strings_simple_example():
#     input_list = ["hello_world", "hello_susan", "hello", "goodbye"]
#     include_glob_patterns = ["*"]
#     print(str(string_util.filter_list_of_strings(input_list, include_glob_patterns)))

# Tests for format_dict function
def test_format_dict_simple_example():
    """ Test this function with a simple example. """
    dictionary = {'key1': 'a', 'key2': 'b'}
    assert string_util.format_dict(dictionary) == 'key1="a",key2="b"'


# Test function with different value_quote's
@pytest.mark.parametrize("dictionary,value_quote,expected", [
    ({'key1': 'a', 'key2': 'b'}, "'", "key1='a',key2='b'"),
    ({'key1': 'a', 'key2': 'b'}, ".", "key1=.a.,key2=.b."),
])
def test_format_dict_different_value_quotes(dictionary, value_quote, expected):
    """ Test the function with different value_quote's. """
    assert string_util.format_dict(dictionary, value_quote) == expected


def test_format_dict_invalid_format():
    """ Test function with an invalid dictionary format. """
    dictionary = {'key1': ['a', 'b'], 'key2': ['c']}
    with pytest.raises(TypeError):
        string_util.format_dict(dictionary)


# TODO @jurentie 02/26/2019 - need to figure out how to test this function
# Tests for glob2re
# def test_glob2re_basic_example():
#     glob = "hello*"
#     assert string_util.glob2re(glob) == 'hello[^/]*\\Z(?ms)'

# Tests for function is_bool
@pytest.mark.parametrize("string,expected", [
    ("true", True),
    ("TRUE", True),
    ("tRuE", True),
    ("false", True),
    ("FALSE", True),
    ("fAlSe", True),
])
def test_is_bool_returns_true(string, expected):
    """ Test function with values that are booleans. Should return true. """
    assert string_util.is_bool(string) == expected


@pytest.mark.parametrize("string,expected", [
    ("t", False),
    ("f", False),
    ("hello_world", False)
])
def test_is_bool_returns_false(string, expected):
    """ Test function with values that are not booleans. Should return false. """
    assert string_util.is_bool(string) == expected


# Tests for is_float
@pytest.mark.parametrize("string,expected", [
    ("12.5", True),
    ("14.77", True),
    ("-0.63", True),
])
def test_is_float_true(string, expected):
    """ Test function with values that are float values. Should return true. """
    assert string_util.is_float(string) == expected


# TODO @jurentie 02/26/2019 should these 'integers' be considered float or not? currently evaluated to True
# @pytest.mark.parametrize("string,expected", [
#     ("12", False),
#     ("15", False),
#     ("1", False),
# ])

@pytest.mark.parametrize("string,expected", [
    ("hello_world", False),
    ("yes", False),
    ("123hello", False),
])
def test_is_float_false(string, expected):
    """ Test function with values that are not float values. Should return false. """
    assert string_util.is_float(string) == expected


# Tests for function is_int
@pytest.mark.parametrize("string,expected", [
    ("1", True),
    ("10560", True),
    ("-50", True),
])
def test_is_int_true(string, expected):
    """ Test function with values that are integers. Should return true. """
    assert string_util.is_int(string) == expected


@pytest.mark.parametrize("string,expected", [
    ("1.5", False),
    ("40.67", False),
    ("-10.899", False),
])
def test_is_int_false(string, expected):
    """ Test function with values that are not integers. Should return false. """
    assert string_util.is_int(string) == expected


# Tests for function key_value_pair_list_to_dictionary()
def test_key_value_pair_list_to_dictionary_simple_example():
    """ Test a simple example with this function. """
    key_value_list = ["key1=a", "key2=b", "key3=c"]
    assert string_util.key_value_pair_list_to_dictionary(key_value_list) == {'key1': 'a', 'key2': 'b', 'key3': 'c'}


def test_key_value_pair_list_to_dictonary_multiple_values():
    """ Test what happens when passing a list of multiple values as the key value list. """
    key_value_list = ["key1=a,b,c", "key2=d"]
    assert string_util.key_value_pair_list_to_dictionary(key_value_list) == {'key1': 'a,b,c', 'key2': 'd'}


def test_key_value_pair_list_to_dictonary_invalid_delimiters():
    """ Test this function with invalid delimiters that are not "=". """
    key_value_list = ["key1,a", "key2,b"]
    with pytest.raises(UnboundLocalError):
        assert string_util.key_value_pair_list_to_dictionary(key_value_list)


# Tests for pattern_count
def test_pattern_count_single_pattern():
    """ Test a single pattern being searched for. """
    string = "aaabcde"
    pattern = "a"
    assert string_util.pattern_count(string, pattern) == 3


def test_pattern_count_pattern_list():
    """ Test a list of patterns being searched for. """
    string = "aaabcddde"
    pattern_list = ['a', 'd']
    assert string_util.pattern_count(string, None, pattern_list) == 6


@pytest.mark.parametrize("string,expected", [
    ("True", True),
    ("TRUE", True),
    ("tRuE", True),
])
# These functions test str_to_bool
def test_str_to_bool_true(string, expected):
    """ Test string to boolean = True. """
    assert string_util.str_to_bool(string) == expected


@pytest.mark.parametrize("string,expected", [
    ("False", False),
    ("FALSE", False),
    ("fAlSe", False),
])
def test_str_to_bool_false(string, expected):
    """ Test string to boolean = False. """
    assert string_util.str_to_bool(string) == expected


def test_str_to_bool_none():
    """ Test a non boolean string that returns None. """
    string = "not a bool"
    assert string_util.str_to_bool(string) is None
