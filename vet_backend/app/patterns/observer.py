from abc import ABC, abstractmethod


class ChatObserver(ABC):
    @abstractmethod
    async def update(self, event: str, data: dict) -> None: ...


class ChatSubject:
    def __init__(self):
        self._observers: list[ChatObserver] = []

    def subscribe(self, observer: ChatObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: ChatObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    async def notify(self, event: str, data: dict) -> None:
        for obs in list(self._observers):
            await obs.update(event, data)


class WebSocketObserver(ChatObserver):
    def __init__(self, websocket) -> None:
        self.ws = websocket

    async def update(self, event: str, data: dict) -> None:
        try:
            await self.ws.send_json({"event": event, "data": data})
        except Exception:
            pass
