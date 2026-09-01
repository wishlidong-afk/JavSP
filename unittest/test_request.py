import pytest
from curl_cffi import requests as curl_requests

from javsp.web import base, javdb
from javsp.web.exceptions import CredentialError


def test_scraper_request_uses_a_chrome_impersonating_curl_session():
    request = base.Request(use_scraper=True)

    assert isinstance(request.scraper, curl_requests.Session)
    assert request.scraper.impersonate == 'chrome'


def test_scraper_request_syncs_cookies_before_sending_request(monkeypatch):
    request = base.Request(use_scraper=True)
    request.cookies = {'locale': 'zh'}
    monkeypatch.setattr(request, '_Request__get', lambda *args, **kwargs: object())

    request.get('https://example.test', delay_raise=True)

    assert request.scraper.cookies.get('locale') == 'zh'


def test_get_resp_text_does_not_require_requests_apparent_encoding():
    class Response:
        encoding = None
        text = '繁體中文頁面'

        @property
        def apparent_encoding(self):
            raise AssertionError('curl_cffi response has no apparent_encoding')

    response = Response()

    assert base.get_resp_text(response) == '繁體中文頁面'
    assert response.encoding == 'utf-8'


def test_javdb_replacement_request_preserves_cookie_and_chinese_locale(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.cookies = {}

    class FakeRequest:
        def __init__(self, use_scraper):
            assert use_scraper is True
            self.headers = {}
            self.cookies = {}
            self.scraper = FakeSession()

    monkeypatch.setattr(javdb, 'Request', FakeRequest)

    request = javdb.create_request({'locale': 'zh', '_jdb_session': 'token'})

    assert request.headers['Accept-Language'].startswith('zh-CN')
    assert request.cookies == {'locale': 'zh', '_jdb_session': 'token'}
    assert request.scraper.cookies == request.cookies


def test_manual_javdb_cookie_must_specify_chinese_locale():
    assert javdb.parse_manual_cookie('locale=zh; _jdb_session=token') == {
        'locale': 'zh',
        '_jdb_session': 'token',
    }

    with pytest.raises(CredentialError, match='locale=zh'):
        javdb.parse_manual_cookie('_jdb_session=token')
