import random

possible_words = {
    "adjective": ["Crunchy", "Cheesy", "Double Decker", "7-Layer", "1/2 lb", "Spicy", "Beefy", "Doritos", "Cantina", "Hard", "Crispy", "Volcano", "Supreme", "Fresco", "Soft", "Baja", "Fiesta", "Mexican", "Zesty", "Stuft", "XXL"],
    "prefix": ["Enchi", "Gor", "Nacho", "Cha", "Mexi", "Quesa", "Soft", "Hard", "Steak"],
    "suffix": ["rito", "dita", "grande", "ito", "lupa", "melt", "wrap", "dilla" ],
    "postword": ["Bellgrande", "Bowl", "Burrito", "Chalupa", "Crunch", "Crunchwrap", "Fiesta", "Gordita", "Griller", "Locos", "Melt", "Nachos", "Quesadilla", "Roll-up", "Salad", "Stacker", "Supreme", "Taco", "Taquito", "Wrap"]
}

def new_word(part):
    new_word = random.choice(possible_words[part])
    while 'current_words' in globals() and new_word == current_words[part]:
        new_word = random.choice(possible_words[part])
    return new_word

def generate_menu_item():
    global current_words
    current_words = {part: new_word(part) for part in possible_words}
    return f"{current_words['adjective']}-{current_words['prefix']}{current_words['suffix']}-{current_words['postword']}"
