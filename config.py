import json
import os


DEFAULT_CONFIG = {
	"theme": "default",
	"bar-left": " <mode-full>",
	"bar-center": "<fn>",
	"bar-right": "<last-key> "
}

DEFAULT_THEME = {
	"kitti.bg": -1,
	"kitti.fg": -1,
	"kitti.bar.bg": 15,
	"kitti.bar.fg": 0
}

with open("config.json", "r", encoding = "utf8") as source:
	config = DEFAULT_CONFIG | json.load(source)
	source.close()

path = "ext/themes/" + config.get("theme", "default")
if not os.path.exists(path):
	theme : dict = DEFAULT_THEME
else:
	with open(path, "r", encoding = "utf8") as source:
		theme : dict = DEFAULT_THEME | json.load(source)
		source.close()
