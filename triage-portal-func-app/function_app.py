import logging
import azure.functions as func
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    path = req.route_params.get('file', 'index.html')
    file_path = os.path.join(os.getenv('HOME'), 'site', 'wwwroot', 'frontend', path)
    
    if not os.path.isfile(file_path):
        return func.HttpResponse("File not found", status_code=404)

    with open(file_path, 'r') as f:
        content = f.read()

    return func.HttpResponse(content, mimetype="text/html")