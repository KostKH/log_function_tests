import aiohttp

from function import logs


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


class MockResponse:
    def __init__(self, list_of_bytes, status):
        self._list_of_bytes = list_of_bytes
        self.status = status
        self.content = AsyncIterator(list_of_bytes)

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


async def test_logs(monkeypatch, capsys):
    cont = 'container1'
    name = 'name1'
    list_of_bytes = [b'test_entry', b'test_entry1']
    expected = ('\n'.join(map(lambda line: f'{name} {line}', list_of_bytes))
                + '\n')

    def mock_get(*args, **kwargs):
        return MockResponse(list_of_bytes, 200)

    monkeypatch.setattr(aiohttp.ClientSession, 'get', mock_get)
    await logs(cont, name)
    captured = capsys.readouterr()
    assert captured.out == expected
