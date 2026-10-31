import importlib
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('TABLER_DB', str(tmp_path / 'test.sqlite3'))
    from app import main
    importlib.reload(main)
    with TestClient(main.app) as c:
        yield c

def test_page_and_local_resources(client):
    from html.parser import HTMLParser
    class Assets(HTMLParser):
        def __init__(self):
            super().__init__()
            self.urls = []
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag in ('script', 'link'):
                url = attrs.get('src') or attrs.get('href')
                if url:
                    self.urls.append(url)
    response = client.get('/')
    assert response.status_code == 200
    assert "connect-src 'self'" in response.headers['content-security-policy']
    parser = Assets()
    parser.feed(response.text)
    assert parser.urls
    for url in parser.urls:
        assert url.startswith('/static/')
        assert client.get(url).status_code == 200

def test_filters_pagination_and_empty(client):
    first = client.get('/partials/projects').text
    second = client.get('/partials/projects?page=2').text
    assert 'PRJ-018' in first and 'PRJ-018' not in second
    assert 'Ничего не найдено' in client.get('/partials/projects?q=Здесьтакогопроектанет').text
    assert 'Ничего не найдено' in client.get('/partials/projects?q=%25').text
    assert 'База знаний' in client.get('/partials/projects?q=база%20знаний').text
    assert 'На проверке' not in client.get('/partials/projects?status=done').text
    assert client.get('/partials/projects?page=0').status_code == 422
    assert client.get('/partials/projects?sort=DROP%20TABLE').status_code == 200

def test_creation_validation_and_escaping(client):
    invalid = client.post('/projects', data={'name':'x','owner':'88','status':'unknown'})
    assert 'HX-Trigger' not in invalid.headers
    assert 'Проверьте поля' in invalid.text
    response = client.post('/projects', data={'name':'<script>alert(1)</script>', 'owner':'1','status':'active'})
    assert response.headers['HX-Trigger'] == 'projectCreated'
    assert '<script>alert(1)</script>' not in response.text
    assert '&lt;script&gt;' in client.get('/partials/projects').text
    assert client.get('/export.csv').text.startswith('\ufeffID,')
    client.post('/projects',data={'name':'=SUM(1+2)','owner':'0','status':'done'})
    assert "'=SUM(1+2)" in client.get('/export.csv').text

def test_activity(client):
    assert 'Михаил обновил документацию' not in client.get('/partials/activity').text
    assert 'Михаил обновил документацию' in client.get('/partials/activity?expanded=true').text
