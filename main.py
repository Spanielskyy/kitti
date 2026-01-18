import curses
import sys
import os

import editor

if len(sys.argv) < 2:
	print(f"ERROR: File path not specified.")
	sys.exit(67)

else:
	PATH = sys.argv[1]


def app(screen : curses.window):

	curses.raw()
	curses.use_default_colors()
	curses.curs_set(0)

	curses.init_pair(1, editor.config.theme.get("kitti.fg"), editor.config.theme.get("kitti.bg"))
	THEME_DEFAULT = curses.color_pair(1)

	curses.init_pair(2, editor.config.theme.get("kitti.bar.fg"), editor.config.theme.get("kitti.bar.bg"))
	THEME_BAR = curses.color_pair(2)


	workspace = editor.Workspace(PATH)

	LANG_THEMES = {}
	if workspace.lang:

		n = 1
		for token_id in workspace.lang_data.get("tokens", {}).keys():

			fg = editor.config.theme.get(f"lang.{workspace.lang}.{token_id}.fg", editor.config.theme.get(f"lang.*.{token_id}.fg", editor.config.theme.get("kitti.fg")))
			bg = editor.config.theme.get(f"lang.{workspace.lang}.{token_id}.bg", editor.config.theme.get(f"lang.*.{token_id}.bg", editor.config.theme.get("kitti.bg")))

			curses.init_pair(2 + n, fg, bg)
			LANG_THEMES[token_id] = curses.color_pair(2 + n)
			n += 1

	pregenerate = False


	while True:

		h, w = screen.getmaxyx()
		workspace.scroll_size_x = w
		workspace.scroll_size_y = h - 2
		screen.clear()

		if not pregenerate:
			for row in range(workspace.scroll_size_y):
				workspace.generate_tokens(row)
				editor.log(f"{row} {workspace.tokens.get(row)}")
			pregenerate = True
			continue

		CENTER_LEN = len(workspace.bar_center)
		RIGHT_LEN = len(workspace.bar_right)

		screen.addstr(h - 2, 0, " " * w, THEME_BAR)
		screen.addstr(h - 2, 0, workspace.bar_left, THEME_BAR)
		screen.addstr(h - 2, int(w / 2 - CENTER_LEN / 2), workspace.bar_center, THEME_BAR)
		screen.addstr(h - 2, w - RIGHT_LEN - 1, workspace.bar_right, THEME_BAR)
		screen.addstr(h - 1, 0, workspace.message)

		for y in range(h - 2):

			row_id = workspace.scroll_row + y
			if row_id < 0 or row_id > len(workspace.rows) - 1:
				screen.addstr(y, 0, "~")
				continue

			row = workspace.rows[row_id]
			row = row.replace("\t", " " * editor.config.config.get("tab-size", 4))
			screen.addstr(y, 0, row)


		for token_row, tokens in workspace.tokens.items():
			for token in tokens:

				tabcount = workspace.rows[token.row][:token.column].count("\t")
				screen.addstr(token_row - workspace.scroll_row, token.column - workspace.scroll_column + tabcount * (editor.config.config.get("tab-size", 4) - 1), token.value, LANG_THEMES.get(token.id))


		cursor_row, cursor_column = workspace.pos_to_rc(workspace.pos)
		if cursor_row != None and cursor_column != None:
			try:
				curses.curs_set(1)
				tabcount = workspace.rows[cursor_row][:cursor_column].count("\t")
				screen.move(cursor_row - workspace.scroll_row, cursor_column - workspace.scroll_column + tabcount * (editor.config.config.get("tab-size", 4) - 1))
			except curses.error:
				curses.curs_set(0)

		screen.refresh()


		key = screen.getch()
		workspace.last_key = key

		if key == 260:
			workspace.action_move_left()

		elif key == 261:
			workspace.action_move_right()

		elif key == 259:
			workspace.action_move_up()

		elif key == 258:
			workspace.action_move_down()


		match workspace.mode:

			case "e":

				if key == 24:
					workspace.mode = None

				elif chr(key) in editor.INPUTS:
					workspace.action_insert(chr(key))

				elif key == 263:
					workspace.action_backspace()

				elif key == 330:
					workspace.action_delete()

				elif key == 9:
					workspace.action_tab()

			case _:

				if key == 24:
					workspace.action_exit()
					if workspace.quit: break

				elif key in (101, 105):
					workspace.mode = "e"

				elif key == 119:
					workspace.action_write()

curses.wrapper(app)
