import os
import config


WORKSPACE_MODES = {
    None: "",
    "e": "INSERT MODE "
}


FORMAT_SIZE = ("B", "kB", "MB", "GB", "TB")
def format_size(size : int) -> str:

    result_size = size
    n = 0
    while result_size >= 1000 and n < len(FORMAT_SIZE) - 1:
        result_size /= 1000
        n += 1

    return f"{result_size}{FORMAT_SIZE[n]}"


INPUTS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()~`_-+={}[]:;\"'\\|,.<>/? \n"


class Workspace:

    def __init__(self, fp : str):

        self.fp = fp
        self.pos : int = 0

        if os.path.exists(self.fp):
            with open(self.fp, "r", encoding = "utf8") as source:
                self.buffer = source.read()
                source.close()

        else:
            with open(self.fp, "w", encoding = "utf8") as source:
                self.buffer = ""
                source.close()

        self.scroll_row : int = 0
        self.scroll_column : int = 0

        self.scroll_size_x : int = 0
        self.scroll_size_y : int = 0
        self.last_key : int = -1

        self.mode : str | None = None

        self.message : str = ""


    @property
    def rows(self) -> list[str]:
        return self.buffer.split("\n")

    @property
    def visible_rows(self) -> list[str]:
        return self.buffer.split("\n")

    @property
    def dir(self) -> str:
        return os.path.abspath(os.path.split(self.fp)[0])

    @property
    def fn(self) -> str:
        return os.path.split(self.fp)[1]

    @property
    def bar(self) -> str:

        bar = config.config.get("bar")
        bar = bar.replace("<dir>", self.dir)
        bar = bar.replace("<fn>", self.fn)
        bar = bar.replace("<pos>", str(self.pos))
        bar = bar.replace("<last-key>", str(self.last_key))
        bar = bar.replace("<mode>", str(self.mode))
        bar = bar.replace("<mode-full>", WORKSPACE_MODES.get(self.mode, "UNKNOWN MODE"))
        return bar


    def adjust_scroll_row(self):

        row, column = self.pos_to_rc(self.pos)
        if row == None or column == None: return
        if row < self.scroll_row:
            self.scroll_row = row
        if row > self.scroll_row + self.scroll_size_y - 1:
            self.scroll_row = row - self.scroll_size_y + 1


    def pos_to_rc(self, pos : int) -> tuple[int, int] | tuple[None, None]:

        rsum = 0
        ridx = 0
        for row in self.buffer.split("\n"):
            if rsum <= pos <= rsum + len(row):
                return (ridx, pos - rsum)
            rsum += len(row) + 1
            ridx += 1
        return (None, None)


    def action_insert(self, char : str):

        self.buffer = self.buffer[:self.pos] + char + self.buffer[self.pos:]
        self.pos += 1


    def action_backspace(self):

        if self.pos == 0: return
        self.buffer = self.buffer[:self.pos - 1] + self.buffer[self.pos:]
        self.pos -= 1


    def action_delete(self):

        if self.pos >= len(self.buffer): return
        self.buffer = self.buffer[:self.pos] + self.buffer[self.pos + 1:]


    def action_write(self):

        try:
            with open(self.fp, "w", encoding = "utf8") as source:
                source.write(self.buffer)
                source.close()
            size = os.path.getsize(self.fp)
            size = round(size, 2)
            size_formatted = format_size(size)
            self.message = f"Wrote {len(self.buffer)} characters ({size_formatted})"

        except:
            self.message = f"Failed to write buffer"