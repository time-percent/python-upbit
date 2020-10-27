

class APIException(Exception):
    def __init__(self, response):
        try:
            json_res = response.json()
        except ValueError:
            self.name = None
            self.message = f'Invalid JSON error message from UPBit: {response.text}'
        else:
            self.name = json_res['error']['name']
            self.message = json_res['error']['message']
        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request')

    def __str__(self):
        if self.name:
            return f'[APIError {self.name}] {self.message}'
        return f'[APIError] {self.message}'


class RequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'[RequestException] {self.message}'