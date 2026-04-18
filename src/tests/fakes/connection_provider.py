class FakeTransaction:
    def commit(self):
        ...

    def rollback(self):
        ...


class FakeConnection:
    def begin_nested(self):
        return FakeTransaction()


class FakeConnectionProvider:
    def __call__(self):
        return FakeConnection()
