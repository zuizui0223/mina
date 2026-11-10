"""Read verified sequential byte ranges without duplicating the large CSV."""
import io

class Blocks(io.RawIOBase):
    def __init__(self, paths):self.paths=iter(paths);self.current=None
    def readable(self):return True
    def readinto(self, buffer):
        view=memoryview(buffer);filled=0
        while filled<len(view):
            if self.current is None:
                try:self.current=next(self.paths).open('rb')
                except StopIteration:break
            n=self.current.readinto(view[filled:])
            if n:filled+=n
            else:self.current.close();self.current=None
        return filled
    def close(self):
        if self.current:self.current.close()
        super().close()
