import requests

def request(name: str, metadata: dict) -> requests.Response:

    ports = {
        "auth-service": "5007",
        "comment-service": "5002",
        "favourite-service": "5004",
        "media-service": "5005",
        "posts-service": "5009",
        "user-service": "5003",
    }

    file = metadata.get("file")
    json = metadata.get("json")
    data = metadata.get("data")