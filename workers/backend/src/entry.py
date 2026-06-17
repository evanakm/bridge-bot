from workers import Response, WorkerEntrypoint

from bridgebot_api import handle_request


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        body = None
        if request.method.upper() not in ("GET", "HEAD", "OPTIONS"):
            body = await request.text()

        response = handle_request(request.method, request.url, body)
        return Response(response.body, status=response.status, headers=response.headers)
