from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, ParseResult, parse_qsl

"""
@author Cory Forward
"""

def parse(value: str):
    parsed = parse_qsl(value)
    return dict(parsed)

def get(path):
    def wrapper(method):
        SimpleServer.register_get(path, method)
        return method
    return wrapper

def post(path):
    def wrapper(method):
        SimpleServer.register_post(path, method)
        return method
    return wrapper

class SimpleServer(BaseHTTPRequestHandler):

    GET_ROUTES = {}
    POST_ROUTES = {}

    @staticmethod
    def register_get(path, method):
        SimpleServer.GET_ROUTES[path] = method

    @staticmethod
    def register_post(path, method):
        SimpleServer.POST_ROUTES[path] = method

    def __load_request__(self):
        """
        Loads basic information from the request,
        such as query parameters
        """
        self.raw_body = None
        self.str_body = None
        self.form_body = None
        self.parsed = urlparse(self.path)
        self.query_parameters = parse(self.parsed.query)

    def do_POST(self):
        self.__load_request__()
        if "Content-Length" in self.headers:
            size = int(self.headers["Content-Length"])
            self.raw_body = self.rfile.read(size)
            try:
                self.str_body = self.raw_body.decode("utf-8")
            except:
                pass

        if self.path in SimpleServer.POST_ROUTES:
            return SimpleServer.POST_ROUTES[self.path](self)
        else:
            return self.on_post(self.path)

    def do_GET(self):
        self.__load_request__()

        if self.path in SimpleServer.GET_ROUTES:
            return SimpleServer.GET_ROUTES[self.path](self)
        else:
            return self.on_get(self.path)

    def send_success(self, message):
        return self.send_response(200, message)

    def send(self, status_code: int, message: str = None, headers: dict = None):
        self.send_response(status_code)

        if headers is not None:
            for key, value in headers:
                self.send_header(key, value)
        self.end_headers()

        if message is not None:
            self.wfile.write(bytes(message, "utf8"))

    def has_form_value(self, param: str):
        """
        Returns whether or not a form value
        was present in the POST body.
        :param param:
        :return:
        """
        return param in self.get_body_as_form()

    def has_form_values(self, names: str):
        """
        Checks for multiple form values
        :param names: A list of form value names to check for
        :return: True if all of the form values are present, otherwise false
        """
        return all([self.has_form_value(value) for value in names])

    def form_value(self, name: str):
        if self.has_form_value(name):
            return self.get_body_as_form()[name]
        else:
            return None

    def has_query_param(self, param: str):
        """
        Returns whether or not a query parameter
        was present.
        :param param: The param to check for
        :return: True if it is set, otherwise False
        """
        return param in self.query_parameters

    def has_query_params(self, params: [str]):
        """
        :param params: A list of query parameters to check for
        :return: True if all of the parameters exist
        """
        return all([self.has_query_param(param) for param in params])

    def query_param(self, param: str):
        """
        Returns a query parameter
        :param param: The query parameter
        :return: The query parameter if it exists, otherwise None
        """
        if self.has_query_param(param):
            return self.query_parameters[param]
        else:
            return None

    def get_body_as_str(self):
        return self.str_body

    def get_body_as_form(self):
        if self.form_body is not None:
            return self.form_body
        self.form_body = parse(self.str_body)
        return self.form_body

    def on_get(self, path: str):
        """
        To be overridden in subclasses.
        :param path: The path of the request
        """
        raise NotImplementedError()

    def on_post(self, path: str):
        """
        To be overridden in subclasses.
        :param path: The path of the request
        :param body: The body of the POST request if it exists
        """
        raise NotImplementedError()