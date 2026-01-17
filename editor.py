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


def log(msg : str):
	with open("log.txt", "a", encoding = "utf8") as logfile:
		logfile.write(msg + "\n")
		logfile.close()


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
		self.cached_column : int = 0

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
	def bar_left(self) -> str:
		return self.bar_generate(config.config.get("bar-left"))

	@property
	def bar_center(self) -> str:
		return self.bar_generate(config.config.get("bar-center"))

	@property
	def bar_right(self) -> str:
		return self.bar_generate(config.config.get("bar-right"))


	def bar_generate(self, bar : str) -> str:

		bar = bar.replace("<dir>", self.dir)
		bar = bar.replace("<fn>", self.fn)
		bar = bar.replace("<pos>", str(self.pos))
		bar = bar.replace("<last-key>", str(self.last_key))
		bar = bar.replace("<mode>", str(self.mode))
		bar = bar.replace("<mode-full>", WORKSPACE_MODES.get(self.mode, "UNKNOWN MODE"))
		return bar


	def set_cached_column(self):

		row, column = self.pos_to_rc(self.pos)
		if row == None or column == None: return
		self.cached_column = column


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


	def rc_to_pos(self, rc : tuple[int, int]) -> int | None:

		return len("".join(n + "\n" for n in self.buffer.split("\n")[:rc[0]])) + rc[1]


	def action_insert(self, char : str):

		self.buffer = self.buffer[:self.pos] + char + self.buffer[self.pos:]
		self.pos += 1
		self.set_cached_column()


	def action_backspace(self):

		if self.pos == 0: return
		self.buffer = self.buffer[:self.pos - 1] + self.buffer[self.pos:]
		self.pos -= 1
		self.set_cached_column()


	def action_delete(self):

		if self.pos >= len(self.buffer): return
		self.buffer = self.buffer[:self.pos] + self.buffer[self.pos + 1:]
		self.set_cached_column()


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


	def action_move_left(self):

		if self.pos <= 0: return
		self.pos -= 1
		self.set_cached_column()


	def action_move_right(self):

		if self.pos >= len(self.buffer): return
		self.pos += 1
		self.set_cached_column()


	def action_move_up(self):

		row, column = self.pos_to_rc(self.pos)
		if row == None or column == None: return
		target_row = row - 1
		if target_row < 0: return

		target_length = len(self.buffer.split("\n")[target_row])
		target_column = min(column, target_length)
		if self.cached_column > column:
			target_column = self.cached_column
		if target_column > target_length:
			target_column = target_length

		target_pos = self.rc_to_pos((target_row, target_column))
		if target_pos == None: return
		self.pos = target_pos


	def action_move_down(self):

		row, column = self.pos_to_rc(self.pos)
		if row == None or column == None: return
		target_row = row + 1
		if target_row > len(self.buffer.split("\n")) - 1: return

		target_length = len(self.buffer.split("\n")[target_row])
		target_column = min(column, target_length)
		if self.cached_column > column:
			target_column = self.cached_column
		if target_column > target_length:
			target_column = target_length

		target_pos = self.rc_to_pos((target_row, target_column))
		if target_pos == None: return
		self.pos = target_pos
