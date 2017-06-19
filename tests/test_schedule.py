from itertools import chain


def test_schedule(mocker, script_runner):
    get_responses = [
        {'projects': ['foo']},
        {'spiders': ['bar']},
    ]

    post_responses = [
        {'jobid': '42'}
    ]
    for response in chain(get_responses, post_responses):
        response['status'] = 'ok'

    mock_get_response = mocker.Mock()
    mock_get_response.json.side_effect = get_responses
    mock_get = mocker.patch('scrapyd_client.utils.requests.get', autospec=True)
    mock_get.return_value = mock_get_response

    mock_post_response = mocker.Mock()
    mock_post_response.json.side_effect = post_responses
    mock_post = mocker.patch('scrapyd_client.utils.requests.post', autospec=True)
    mock_post.return_value = mock_post_response

    result = script_runner.run('scrapyd-client', 'schedule', '-p', 'foo', 'bar')

    assert result.success, result.stdout + '\n' + result.stderr
    assert not result.stderr, result.stderr
    assert result.stdout == 'foo / bar => 42\n'
