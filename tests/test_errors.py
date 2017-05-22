from requests.exceptions import ConnectionError


from scrapyd_client.utils import JSONDecodeError


def test_decode_error(mocker, script_runner):
    mock_response = mocker.Mock()
    mock_response.json.side_effect = JSONDecodeError('', '', 0)
    mock_get = mocker.patch('scrapyd_client.utils.requests.get', autospec=True)
    mock_get.return_value = mock_response
    result = script_runner.run('scrapyd-client', 'projects')

    assert not result.success
    assert result.stdout.startswith('Received a malformed response:\n')


def test_projects(mocker, script_runner):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'status': 'error', 'message': 'Something went wrong.'}
    mock_get = mocker.patch('scrapyd_client.utils.requests.get', autospec=True)
    mock_get.return_value = mock_response
    result = script_runner.run('scrapyd-client', 'projects')

    assert not result.success
    assert result.stdout == 'Scrapyd responded with an error:\nSomething went wrong.\n'


def test_connection_error(mocker, script_runner):
    mock_get = mocker.patch('scrapyd_client.utils.requests.get', autospec=True)
    mock_get.side_effect = ConnectionError()
    result = script_runner.run('scrapyd-client', 'projects')

    assert not result.success
    assert result.stdout == 'Failed to connect to target (http://localhost:6800):\n\n'
