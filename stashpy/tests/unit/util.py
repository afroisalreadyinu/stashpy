sentinel = object()

class MockESConn:
    def __init__(self, *args):
        self.puts = []

    def put(self, index, type, uid, contents, callback):
        self.puts.append((index, type, uid, contents))
        return sentinel
