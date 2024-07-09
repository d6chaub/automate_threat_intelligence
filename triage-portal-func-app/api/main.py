import json
import azure.functions as func

def handle_request(req: func.HttpRequest) -> func.HttpResponse:
    # Example API logic
    data = {
        "message": "Hello from the API backend!",
        "status": "success"
    }
    return func.HttpResponse(
        json.dumps(data),
        mimetype="application/json",
        status_code=200
    )
