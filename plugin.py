import sublime
import sublime_plugin
import os
import json
import yaml

syntax_pathes = {"tick":os.path.realpath(__file__)[:-9]+"syntaxes\\mcfunction_tick.sublime-syntax", 
				 "load":os.path.realpath(__file__)[:-9]+"syntaxes\\mcfunction_load.sublime-syntax"}

def clear_tick_n_load():
	def clear_file_exts(func_type):
		with open(syntax_pathes[func_type]) as syntax_file:
			syntax_data =  yaml.safe_load(syntax_file)
		syntax_data["file_extensions"] = None
		with open(syntax_pathes[func_type], "w") as syntax_file:
			syntax_file.write("%YAML 1.2\n---\n")
		with open(syntax_pathes[func_type], "a") as syntax_file:
			yaml.dump(syntax_data, syntax_file)
	clear_file_exts("tick")
	clear_file_exts("load")

def update_tick_n_load(view):
	# Setup vars
	window = view.window()
	project_path = window.extract_variables()["folder"]
	# Walk through the project folder and its subfolders to find tick.json and load.json files
	pathes = {"tick": False, "load": False}
	for root, dirs, files in os.walk(project_path):
		if 'tick.json' in files:
			pathes["tick"] = os.path.join(root, 'tick.json')
		if 'load.json' in files:
			pathes["load"] = os.path.join(root, 'load.json')
		if pathes["tick"] and pathes["load"]:
			break
	def add_functions(func_type):
		full_syntax_path = syntax_pathes[func_type]
		with open(pathes[func_type], "r") as file:
			type_functions = json.load(file)
		with open(full_syntax_path, "r") as syntax_file:
			syntax_data = yaml.safe_load(syntax_file)
		syntax_data["file_extensions"] = [function_path.split(":")[-1].split("/")[-1]+".mcfunction" for function_path in type_functions["values"]]
		with open(full_syntax_path, "w") as syntax_file:
			syntax_file.write("%YAML 1.2\n---\n")
		with open(full_syntax_path, "a") as syntax_file:
			yaml.dump(syntax_data, syntax_file)
	add_functions("tick")
	add_functions("load")
	window.run_command("focus_side_bar")

class DynamicFunctions(sublime_plugin.EventListener):
	def on_init(self, views):
		clear_tick_n_load()
		update_tick_n_load(views[0])
		
	def on_post_save_async(self, view):
		if view.file_name().split("\\")[-1] in ("tick.json", "load.json"):
			update_tick_n_load(view)
