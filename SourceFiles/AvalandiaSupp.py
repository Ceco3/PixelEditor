from .Canvas import Canvas

DEEP_WATER = 0
WATER = 1
SAND = 2
PLAINS1 = 3
PLAINS2 = 4
FOREST = 5
MOUNTAINS = 6

data_file_path = "C:\\Program Files (x86)\\Avalandia\\WorldData\\CustomWorld.txt"

terrain_dict = {
    (100, 50, 155, 255): DEEP_WATER,
    (0, 150, 255, 255): WATER,
    (200, 150, 55, 255): SAND,
    (50, 155, 100, 255): PLAINS1,
    (120, 150, 90, 255): PLAINS2,
    (10, 150, 40, 255): FOREST,
    (150, 140, 150, 255): MOUNTAINS
}

def save_avalandia_data():
    with open(data_file_path, "w") as data_file:
        canvas_data = Canvas.lDict[1].get_raw()
        lines = []
        for row in canvas_data:
            line = ""
            for data_point in canvas_data[row]:
                line += str(terrain_dict[data_point]) + " "
            line.rstrip(" ")
            line += "\n"
            lines.append(line)
        data_file.writelines(lines)