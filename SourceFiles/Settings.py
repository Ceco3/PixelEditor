import json
import os

settings_directory_path = "Settings"

def load_all_settings(folder_path: str = settings_directory_path) -> dict[str, dict]:
    """Returns a (nested) dictionary containing loaded settings (again as dictionaries)
       with their keys being the names of the specific setting.
       (i. e. {"User": <Setting-dict>})"""
    all_settings: dict[str, dict] = {}
    for file_sub_path in os.listdir(folder_path):
        with open(folder_path + "\\" + file_sub_path) as json_file:
            all_settings[file_sub_path.replace(".json", "")] = json.load(json_file)
            # Make sure <file_sub_path> doesn't contain (.json) twice
    return all_settings

settings_dict = load_all_settings()

def aux_save_specified_setting(setting_name: str, indent):
    with open(settings_directory_path + "\\" + setting_name + ".json", "w") as json_file:
        json.dump(settings_dict[setting_name], json_file, indent=indent)

def save_specified_setting(setting_name: str, single_line: bool = False) -> None:
    # Writes json to file under <settings_directory_path> names <settings_name>
    if not single_line:
        aux_save_specified_setting(setting_name, 4)
    else:
        aux_save_specified_setting(setting_name, None)

def load_specified_setting(setting_name: str) -> None:
    # Updates settings_dict[<setting_name>] with current json file
    with open(settings_directory_path + "\\" + setting_name + ".json", "r") as json_file:
        settings_dict[setting_name] = json.load(json_file)



def aux_get(inner_dict: dict, arg_list: list[str]):
    if len(arg_list) == 1:
        return inner_dict[arg_list.pop()]
    return aux_get(inner_dict[arg_list.pop()], arg_list)

def aux_set(inner_dict: dict, arg_list: list[str], value):
    if len(arg_list) == 1:
        inner_dict[arg_list.pop()] = value
        return
    aux_set(inner_dict[arg_list.pop()], arg_list, value)

def aux_add(inner_dict: dict, arg_list: list[str], value: tuple[str, dict | object]):
    if len(arg_list) == 1:
        object_name, item = value
        inner_dict[arg_list.pop()][object_name] = item
        return
    aux_add(inner_dict[arg_list.pop()], arg_list, value)

def aux_del(inner_dict: dict, arg_list: list[str]):
    if len(arg_list) == 1:
        del inner_dict[arg_list.pop()]
        return
    aux_del(inner_dict[arg_list.pop()], arg_list)

#______Accesories______#
def Get(setting_name, arg_list: list[str] | str | None): # -> Any
    if arg_list is None:
        return settings_dict[setting_name]
    if isinstance(arg_list, str):
        return settings_dict[setting_name][arg_list]
    arg_list.reverse()
    return aux_get(settings_dict[setting_name], arg_list)

def Set(setting_name, arg_list: list[str] | str, value) -> None:
    if isinstance(arg_list, str):
        settings_dict[setting_name][arg_list] = value
        return
    arg_list.reverse()
    aux_set(settings_dict[setting_name], arg_list, value)

def Add(setting_name, arg_list: list[str] | str | None, value: tuple[str, dict | object]):
    object_name, item = value
    if arg_list is None:
        settings_dict[setting_name][object_name] = item
        save_specified_setting(setting_name)
        return
    if isinstance(arg_list, str):
        settings_dict[setting_name][arg_list][object_name] = item
        save_specified_setting(setting_name)
        return
    arg_list.reverse()
    aux_add(settings_dict[setting_name], arg_list, value)
    save_specified_setting(setting_name)

def Del(setting_name, arg_list: list[str] | str):
    if isinstance(arg_list, str):
        del settings_dict[setting_name][arg_list]
        save_specified_setting(setting_name)
        return
    arg_list.reverse()
    aux_del(settings_dict[setting_name], arg_list)
    save_specified_setting(setting_name)




#_____Debugging_____#
def aux_show(inner_dict: dict, indent: int):
    for key, value in inner_dict.items():
        if not isinstance(value, dict):
            print(indent * " " + key + " : " + str(value))
            continue
        print(indent * " " + key)
        aux_show(inner_dict[key], indent + 4)

def Show(setting_name: str | None) -> None:
    if setting_name is None:
        aux_show(settings_dict, 0)
        return
    aux_show(settings_dict[setting_name], 0)

#____________Showcase_Use___________#
# Set("User", ["Designs", "Light", "Panel"], [[10, 10, 10]]))
# Show(None)
# Show("User")

#______Design_Pattern______#        (Found in User.json)
#
# Designs : {
#   "<Desing Name (e.g. "Light")>" : {
#       "Template"   : [<Color>, <fColor>],
#       "Panel"      : [<Color>],
#       "Button"     : [<Color>, <fColor>, <tColor>]
#       "Icon"       : [<Color>, <fColor>]
#       "Text"       : [<Color>, <tColor>]
#       "TextButton" : [<Color>, <fColor>, <tColor>]
#       }
# }
#
# Where Color, fColor, tColor are [r, g, b] triples

#______Layout_Pattern______#        (Found in Layout.json)
#
# <Template name> (e. g. "Attelier") : {
#       "order"      : int
#       "position"   : [x, y] (relative 0-100)
#       "toggle"     : bool
#       "components" : {
#           "component_ord" : {       (int)
#                 "type"     : int    (translation map of int <-> Component type is located in Constants.py)
#                 "localPos" : [x, y] (relative to parent Template 0-100)  
#             }
#
#       }
# }

#______Dev_Tools______#
def dev_add_layout_template_atr(atr_name: str, value, affected_orders: list[int] = None):
    for template_item in settings_dict["Layout"].values():
        if affected_orders is None or template_item["order"] in affected_orders:
            template_item[atr_name] = value
    save_specified_setting("Layout")

def dev_add_atr2all_comps(atr_name: str, value, affected_template_ords: list[int] = None):
    for template_item in settings_dict["Layout"].values():
        if affected_template_ords is not None and template_item["order"] not in affected_template_ords:
            continue
        for Component in template_item["components"].values():
            Component[atr_name] = value
    save_specified_setting("Layout")

if __name__ == "__main__":
    dev_add_atr2all_comps("components", {})
    #dev_add_layout_template_atr("type", None)