import logging
import azure.functions as func
from .main import handle_request

def main(req: func.HttpRequest) -> func.HttpResponse:
    return handle_request(req)