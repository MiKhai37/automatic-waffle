from flask_app.db_helpers import get_body_or_400
from werkzeug.exceptions import BadRequest
import pytest

req_params = ['param1', 'param2']
opt_params = ['param3', 'param4']


class FakeRequest:
    def __init__(self, json) -> None:
        self.json = json


def test_valid_body():
    valid_request = FakeRequest({'param1': 'value_1', 'param2': 'value_2'})
    body = get_body_or_400(valid_request, req_params, opt_params)
    assert body is not None
    assert body['param1'] == 'value_1'


def test_uncomplete_body():
    uncomplete_request = FakeRequest({'param2': 'value_2'})
    with pytest.raises(BadRequest):
        body = None
        body = get_body_or_400(uncomplete_request, req_params, opt_params)
    assert body is None


def test_too_much_body():
    too_much__request = FakeRequest(
        {'param1': 'value_1', 'param2': 'value_2', 'param5': 'value_5'})
    with pytest.raises(BadRequest):
        body = None
        body = get_body_or_400(too_much__request, req_params, opt_params)
    assert body is None


def test_opt_params():
    opt_request = FakeRequest(
        {'param1': 'value_1', 'param2': 'value_2', 'param3': 'value_3'})
    body = get_body_or_400(opt_request, req_params, opt_params)
    assert body is not None
    assert body['param3'] == 'value_3'
