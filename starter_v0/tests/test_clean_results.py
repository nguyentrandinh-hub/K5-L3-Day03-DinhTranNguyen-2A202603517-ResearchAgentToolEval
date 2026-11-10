from copy import deepcopy
import pytest
from tools import TOOL_FUNCTIONS
clean = TOOL_FUNCTIONS['clean_results']


def test_primary_source_wins_and_removal_is_audited_without_mutation():
    items = [dict(url='https://x.com/user/status/1', summary='A model was released.'), dict(url='https://openai.com/news/model', summary='A model was released.')]
    original = deepcopy(items)
    result = clean(items)
    assert result['items'] == [items[1]]
    assert result['removed'][0]['kept_index'] == 1
    assert result['removed'][0]['removed_index'] == 0
    assert result['removed'][0]['match_reason'] == 'same_content'
    assert items == original


def test_tracking_urls_merge_but_meaningful_query_parameters_remain():
    items = [dict(url='https://www.example.com/a?id=1&utm_source=feed#top'), dict(url='https://example.com/a?id=1'), dict(url='https://example.com/a?id=2')]
    result = clean(items)
    assert result['items'] == [items[0], items[2]]
    assert result['removed'][0]['match_reason'] == 'same_url'


def test_preferred_domain_checks_boundaries_and_ignores_claimed_trust():
    items = [dict(url='https://official.example.evil.test/a', title='Same news', trust_score=100), dict(url='https://news.official.example/b', title='Same news')]
    assert clean(items, trusted_domains=['official.example'])['items'] == [items[1]]


def test_reporting_beats_social_and_ties_keep_first():
    items = [dict(url='https://reddit.com/r/news/1', title='Same story'), dict(url='https://reuters.com/story', title='Same story'), dict(url='https://apnews.com/story', title='Same story')]
    assert clean(items)['items'] == [items[1]]


def test_shared_title_does_not_merge_distinct_claims():
    items = [dict(url='https://example.com/a', title='Results', summary='Model scored 80.'), dict(url='https://example.com/b', title='Results', summary='Model scored 90.')]
    assert clean(items)['items'] == items


def test_near_duplicate_matches_but_changed_numbers_remain():
    content = 'The research team released a detailed evaluation of the new language model with 80 benchmark tasks and shared the full dataset.'
    items = [dict(url='https://example.com/a', summary=content), dict(url='https://example.com/b', summary=content.replace('detailed', 'detailed new')), dict(url='https://example.com/c', summary=content.replace('80', '90'))]
    result = clean(items)
    assert result['items'] == [items[0], items[2]]
    assert result['removed'][0]['match_reason'] == 'near_duplicate_content'


def test_empty_results():
    assert clean([])['item_count'] == 0
    assert clean([])['removed_count'] == 0


@pytest.mark.parametrize('arguments', [
    {'items': None}, {'items': ['bad']}, {'items': [{}]},
    {'items': [{'url': 'javascript:alert(1)'}]},
    {'items': [{'url': 'https://example.com', 'summary': 42}]},
    {'items': [], 'similarity_threshold': '0.94'},
    {'items': [], 'similarity_threshold': True},
    {'items': [], 'similarity_threshold': 0.2},
    {'items': [], 'trusted_domains': ['https://example.com']},
    {'items': [], 'trusted_domains': 'example.com'},
    {'items': [{'url': 'https://example.com'}] * 201},
])
def test_invalid_arguments_return_error_dictionary(arguments):
    assert clean(**arguments)['error'] == 'ValueError'
