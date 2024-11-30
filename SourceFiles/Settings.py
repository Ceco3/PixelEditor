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
def Set(settings_name: str, attr: str, val):
    setattr(settings_object_dict[settings_name][0], attr, val)

def Get(settings_name: str, attr: str):
    return getattr(settings_object_dict[settings_name][0], attr)

settings_object_dict = load_all_settings('Settings')
# Fix Home Path


#___USE___#
# class_object_dict["User"][0].deep_show()
# set_attribute("User", "Design", "Moss")
# save_specified_settings("User")
# load_specified_settings("User")
# class_object_dict["User"][0].deep_show()
