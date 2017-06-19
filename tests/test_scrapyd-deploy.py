import os


def test_not_in_project(script_runner):
    ret = script_runner.run('scrapyd-deploy', '-l')
    assert not ret.success
    assert ret.stdout == ''
    assert 'Error: no Scrapy project found in this location' in ret.stderr


def test_build_egg(tmpdir, script_runner):
    p = tmpdir.mkdir("myhome")
    p.chdir()

    ret = script_runner.run('scrapy', 'startproject', 'myproj')
    assert ret.success
    assert "New Scrapy project 'myproj'" in ret.stdout
    assert ret.stderr == ''

    # move into the scrapy project directory
    os.chdir('myproj/')

    ret = script_runner.run('scrapyd-deploy', '--build-egg', 'myproj.egg')
    assert ret.success
    assert ret.stdout == ''
    assert 'Writing egg to myproj.egg' in ret.stderr
