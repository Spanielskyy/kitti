import re
import os
import json
import config


def log(msg : str):
	with open("/usr/share/kitti/log.txt", "a", encoding = "utf8") as logfile:
		logfile.write(msg + "\n")
		logfile.close()


class Token:

	def __init__(self, id : str, row : int, column : int, value : str):

		self.id = id
		self.row = row
		self.column = column
		self.value = value

	def __repr__(self) -> str:

		return f"Token({self.id}, {self.row}, {self.column}, '{self.value}')"


def load_language(ext : str) -> tuple[str | None, dict]:

	for lang_fn in os.listdir("/usr/share/kitti/ext/lang"):

		if not lang_fn.endswith(".json"): continue
		with open(f"/usr/share/kitti/ext/lang/{lang_fn}", "r", encoding = "utf8") as source:
			lang = json.load(source)
			source.close()

		if ext in lang.get("ext", []):
			return lang_fn.removesuffix(".json"), lang

	return None, {}


def generate_tokens(lang : dict, row : int, string : str) -> list[Token]:

	tokens = []

	for token_id, token_rules in lang.get("tokens", {}).items():

		regex = token_rules.get("match", None)
		if not regex: return
		matches = re.finditer(regex, string)

		for match in matches:
			#log(str(type(match.start)) + " " + str(type(match.end)))
			tokens.append(
				Token(token_id, row, match.start(), string[match.start():match.end()])
			)

	return tokens
