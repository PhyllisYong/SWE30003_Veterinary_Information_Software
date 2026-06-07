from abc import ABC, abstractmethod


class ChatObserver(ABC):
    @abstractmethod
    async def update(self, event: str, data: dict) -> None: ...


class ChatSubject:
    _observerRegistry: dict[str, list["ChatObserver"]] = {}

    def __init__(self):
        self._observers: list["ChatObserver"] = []

    def _observerKey(self) -> str:
        return getattr(self, "chatID", str(id(self)))

    def _observerList(self) -> list["ChatObserver"]:
        key = self._observerKey()
        return self._observerRegistry.setdefault(key, [])

    def subscribe(self, observer: "ChatObserver") -> None:
        observers = self._observerList()
        if observer not in observers:
            observers.append(observer)

    def unsubscribe(self, observer: "ChatObserver") -> None:
        observers = self._observerList()
        if observer in observers:
            observers.remove(observer)

    async def notify(self, event: str, data: dict) -> None:
        for obs in list(self._observerList()):
            await obs.update(event, data)


class WebSocketObserver(ChatObserver):
    def __init__(self, websocket) -> None:
        self._websocket = websocket

    async def update(self, event: str, data: dict) -> None:
        try:
            await self._websocket.send_json({"event": event, "data": data})
        except Exception:
            pass
