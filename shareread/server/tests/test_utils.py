from ..utils import parse_webkitform
import json

def gen_parse_webkitform():
    mock_request_body = file('mock_request.txt', 'r').read()
    output = parse_webkitform(mock_request_body)
    with open('correct_response.txt', 'w') as f:
        json.dump(output, f)

def test_parse_webkitform():
    mock_request_body = file('mock_request.txt', 'r').read()
    output = parse_webkitform(mock_request_body)
    with open('correct_response.txt', 'r') as f:
        truth = json.load(f)
    for key in truth:
        if key == 'boundary':
            output[key] = list(output[key]) # json does not save tuple.
        assert(truth[key] == output[key])

