responses = [
    {'projects': ['foo', 'bar', 'peng']},
    {'spiders': ['foo_1']},
    {'spiders': []},
    {'spiders': ['boing', 'boom', 'tschak']}
]
for response in responses:
    response['status'] = 'ok'


def test_spiders(mocker, script_runner):
    mock_response = mocker.Mock()
    mock_response.json.side_effect = responses
    mock_get = mocker.patch('scrapyd_client.utils.requests.get', autospec=True)
    mock_get.return_value = mock_response
    result = script_runner.run('scrapyd-client', 'spiders', '-p', '*')

    assert result.success, result.stdout + '\n' + result.stderr
    assert not result.stderr, result.stderr
    assert result.stdout == """
foo:
  foo_1
bar:
  No spiders.
peng:
  boing
  boom
  tschak
""".strip() + '\n'


def test_spiders_verbose(mocker, script_runner):
    mock_response = mocker.Mock()
    mock_response.json.side_effect = responses
    mock_get = mocker.patch('scrapyd_client.utils.requests.get', autospec=True)
    mock_get.return_value = mock_response
    result = script_runner.run('scrapyd-client', 'spiders', '-v', '-p', '*')

    assert result.success, result.stdout + '\n' + result.stderr
    assert not result.stderr, result.stderr
    assert result.stdout == """
foo foo_1
peng boing
peng boom
peng tschak
""".strip() + '\n'
