import json
import os

def generate_class(json_settings_file_name):
    def constructor(self, json_settings_file):
        set_attributes(self, json_settings_file)

    def set_attributes(self, json_settings_file):
        for attribute_name in json_settings_file.keys():
            setattr(self, attribute_name, json_settings_file[attribute_name])

    def show(self):
        print(type(self).__name__)
        for atrribute in vars(self):
            print("    " + atrribute)

    def deep_show(self):
        print(type(self).__name__)
        for atrribute in vars(self):
            print("    " + atrribute + "  ->  " + str(getattr(self, atrribute)))

    return type(json_settings_file_name, (object, ), {"__init__": constructor, "show": show, "deep_show": deep_show})

def load_all_settings(settings_directory_path):
    """Returns a dictionary with values as instances of python class representation
        of json files in specified settings directory"""
    settings_object_dict = {}
    for file_sub_path in os.listdir(settings_directory_path):
        with open(settings_directory_path + "\\" + file_sub_path) as json_file:
            new_class = generate_class(file_sub_path.rstrip(".json"))
            settings_object_dict[file_sub_path.rstrip(".json")] = (new_class(json.load(json_file)), new_class)
    
    return settings_object_dict

def save_specified_settings(name):
    with open("Settings\\" + name + ".json", "w") as f:
        json.dump(settings_object_dict[name][0].__dict__, f, indent=4)

def load_specified_settings(name):
    with open("Settings\\" + name + ".json", "r") as json_file:
        obj_, class_ = settings_object_dict[name]
        settings_object_dict[name] = (settings_object_dict[name][1](json.load(json_file)), class_)


#___accessories___#
def Set(settings_name: str, attrs: list[str] | str, val):
    if isinstance(attrs, str):
        setattr(settings_object_dict[settings_name][0], attrs, val)
        return
    if len(attrs) == 1:
        setattr(settings_object_dict[settings_name][0], attrs[0], val)
        return
    if len(attrs) == 2:
        dct = Get(settings_name, attrs[0])
        dct[attrs[1]] = val
        setattr(settings_object_dict[settings_name][0], attrs[0], dct)
        return
    print("I'm sorry I don't support this yet :( (Message called from Set in Settings)")

def Get(settings_name: str, attr: str):
    return getattr(settings_object_dict[settings_name][0], attr)

settings_object_dict = load_all_settings('Settings')
# Fix Home Path

#__Wiev_of_<settings_object_dict>_example__#
#
#{ "User"    :  (<__main__.User object at 0x000001E6B86CA250>, <class '__main__.User'>)       
#  "Project" : (<__main__.Project object at 0x000001DF64B4CD50>, <class '__main__.Project'>)}

#___USE___#
# class_object_dict["User"][0].deep_show()
# save_specified_settings("User")
# load_specified_settings("User")
# settings_object_dict["User"][0].deep_show()
# print(settings_object_dict["User"][0].Paths)