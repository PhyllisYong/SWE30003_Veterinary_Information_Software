from abc import ABC, abstractmethod


class ChatObserver(ABC):
    @abstractmethod
    async def update(self, event: str, data: dict) -> None: ...


class ChatSubject:
    _observer_registry: dict[str, list[ChatObserver]] = {}

    def __init__(self):
        self._observers: list[ChatObserver] = []

    def _observer_key(self) -> str:
        return getattr(self, "chatID", str(id(self)))

    def _observer_list(self) -> list[ChatObserver]:
        key = self._observer_key()
        return self._observer_registry.setdefault(key, [])

    def subscribe(self, observer: ChatObserver) -> None:
        observers = self._observer_list()
        if observer not in observers:
            observers.append(observer)

    def unsubscribe(self, observer: ChatObserver) -> None:
        observers = self._observer_list()
        if observer in observers:
            observers.remove(observer)

    async def notify(self, event: str, data: dict) -> None:
        for obs in list(self._observer_list()):
            await obs.update(event, data)


class WebSocketObserver(ChatObserver):
    def __init__(self, websocket) -> None:
        self.ws = websocket

    async def update(self, event: str, data: dict) -> None:
        try:
            await self.ws.send_json({"event": event, "data": data})
        except Exception:
            pass
