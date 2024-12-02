import pygame
"Init Pygame in Main"


anomalies = {
    "I" : 6,
    "M" : 10,
    "T" : 10,
    "V" : 10,
    "W" : 10,
    "Y" : 10,
    "'" : 2,
    " " : 6,
    "[" : 6,
    "]" : 6
}

overlay_surf = pygame.Surface((10, 10))
overlay_surf.fill((255, 200, 0))

color_surf = pygame.Surface((10, 10))

def char_converter(char: str):
    match char:
        case "\\":
            return "'"
        case " ":
            return ","
    
    return char

def count_pixels(line):
    length = 0
    for char in line:
        if char not in anomalies:
            length += 8
        if char in anomalies:
            length += anomalies[char]
        length += 2
    return length

def make_word(word: str, color: tuple[int, int, int]) -> pygame.Surface:
    color_surf.fill(color)
    images = []
    for letter in word:
        if letter.isupper():
            letter_im = pygame.image.load("Alphabet\{letter}.png".format(letter = char_converter(letter.capitalize()))).convert_alpha()
            letter_im.blit(overlay_surf, (0, 0), special_flags=pygame.BLEND_MULT)
            images.append(letter_im)
            continue
        letter_im = pygame.image.load("Alphabet\{letter}.png".format(letter = char_converter(letter.capitalize()))).convert_alpha()
        letter_im.blit(color_surf, (0, 0), special_flags=pygame.BLEND_MULT)
        images.append(letter_im)
    pix_count = count_pixels(word)
    surf = pygame.Surface((pix_count, 12), pygame.SRCALPHA, 32)
    current = 0
    for index in range(len(images)):
        surf.blit(images[index], (current, 0))
        if word[index] not in anomalies:
            current += 8
        else:
            current += anomalies[word[index]]
        current += 2
    return surf