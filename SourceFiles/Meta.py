class updater:
    def __init__(self) -> None:
        self.objects = []

    def Update(self):
        "Gets called once every frame"
        for object_ in self.objects:
            object_.Update()

    def Add(self, object_):
        self.objects.append(object_)

Updater = updater()

class registry:
    def __init__(self) -> None:
        "General purpose global spanning registry item"
        self.objects = {}

    def Write(self, name: str, object_):
        self.objects[name] = object_

    def Read(self, name:str):
        return self.objects[name]

Registry = registry()

#  <3

class user_variables:
    def __init__(self) -> None:
        self.variables = {"imageName": "DefaultName",
                          "saveDir": None,
                          "loadDir": None}

    def Set(self, variable, value):
        self.variables[variable] = value

    def Get(self, variable):
        return self.variables[variable]
    
User_variables = user_variables()