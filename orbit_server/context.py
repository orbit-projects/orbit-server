from starlette.requests import Request


class RequestContext:
    def __init__(self, request: Request):
        self.request = request

    @property
    def headers(self):
        return dict(self.request.headers)

    @property
    def query_params(self):
        return dict(self.request.query_params)

    @property
    def method(self):
        return self.request.method

    @property
    def path(self):
        return self.request.url.path

    @property
    def client_ip(self):
        return self.request.client.host if self.request.client else None
