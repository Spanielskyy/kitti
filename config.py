import json
import os


DEFAULT_CONFIG = {
	"theme": "default",
	"bar-left": " <mode-full>",
	"bar-center": "<fn>",
	"bar-right": "<modified><last-key> ",
	"tab-size": 4,
	"feedback": {
		"buffer-modified-true": "MODIFIED",
		"buffer-modified-false": "",
		"buffer-modified-warning": "WARNING: Buffer was modified, but not written. `Mod+x` to exit anyway.",
		"buffer-write": "Wrote buffer successfully (<buffer-length> characters, <buffer-size>)",
		"buffer-write-fail": "Failed to write buffer"
	}
}

DEFAULT_THEME = {
	"kitti.bg": -1,
	"kitti.fg": -1,
	"kitti.bar.bg": 15,
	"kitti.bar.fg": 0
}

with open("/usr/share/kitti/config.json", "r", encoding = "utf8") as source:
	config = DEFAULT_CONFIG | json.load(source)
	source.close()

path = "/usr/share/kitti/ext/themes/" + config.get("theme", "default")
if not os.path.exists(path):
	theme : dict = DEFAULT_THEME
else:
	with open(path, "r", encoding = "utf8") as source:
		theme : dict = DEFAULT_THEME | json.load(source)
		source.close()
