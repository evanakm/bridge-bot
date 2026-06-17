from urllib.parse import urlparse

from workers import Response, WorkerEntrypoint

from bridgebot_api import (
    ApiResponse,
    handle_request,
    prepare_training_game_record,
    training_game_response,
)


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        body = None
        if request.method.upper() not in ("GET", "HEAD", "OPTIONS"):
            body = await request.text()

        if request.method.upper() == "POST" and urlparse(request.url).path == "/api/training/games":
            response = await self._training_game_response(body)
            return Response(response.body, status=response.status, headers=response.headers)

        response = handle_request(request.method, request.url, body)
        return Response(response.body, status=response.status, headers=response.headers)

    async def _training_game_response(self, body):
        record = prepare_training_game_record(body)
        if isinstance(record, ApiResponse):
            return record

        bucket = getattr(self.env, "TRAINING_GAMES", None)
        if bucket is None:
            return training_game_response(record)

        await bucket.put(record.storage_key, record.body)
        return training_game_response(record, storage="r2")
