"""Who comes in, what they want, and what they say about what they get.

Each ticket is a different *kind* of puzzle rather than a different list of
ingredients, so the night keeps teaching you something:

  kaki      an exact order            (learn to stack)
  starcat   a shape, not a recipe     (height, contents free)
  vesper    a count, not a list
  rockstar  an adjective you decode
  never     the one thing nobody else will eat
  mermaid   a category with a joke in it
  chii      changes her mind mid-build
  brasil    a themed set
  kitty     a callback to the first order of the weekend
"""

# Camper's shirt reads I WOULD NEVER EAT MOLD, and she orders the mold. Put it in
# anyone else's burger and you get the same line back in her voice — nobody at this
# counter will eat it except the one wearing the shirt about it.
MOLD_LINE = "I would never eat mold."

# id, label, the sprite's cell in the atlas
INGREDIENTS = [
    ('bun_b', 'bottom bun'), ('patty', 'patty'), ('cheese', 'cheese'), ('mold', 'the blue cheese'),
    ('lettuce', 'lettuce'), ('tomato', 'tomato'), ('pickle', 'pickles'),
    ('onion', 'onion'), ('bacon', 'bacon'), ('egg', 'fried egg'),
    ('shroom', 'mushroom'), ('ice', 'ice shard'), ('bun_t', 'top bun'),
]

# Three nights, three customers each. `tod` tints the diner: the art is a night
# diner, so 1.0 is it left alone and lower values lift it a little. Friday still
# has some evening left in it; by Sunday the room is as dark as the art gets.
SERVICES = [
    dict(key='friday', name='Friday night', hours='21:00 – 23:30', tod=0.74,
         blurb='The weekend starts here. Three of them are already outside and the grill is cold.'),
    dict(key='saturday', name='Saturday night', hours='20:30 – late', tod=0.90,
         blurb='The big one. Everyone wants something specific and nobody wants to explain it.'),
    dict(key='sunday', name='Sunday night', hours='19:00 – 22:45', tod=1.0,
         blurb='Last night of the weekend. The ones who come in this late come in for a reason.'),
]

CUSTOMERS = [
    dict(
        key='kaki',
        service='friday',
        poke="Mm. Hello.",
        aside="...if that's okay.", name='Kaki', clock='21:10',
        order="Bottom bun, patty, a mushroom, top bun. That's the whole thing.",
        ticket='patty · mushroom · nothing else',
        rule=dict(require=['patty', 'shroom'], forbid=['cheese', 'lettuce', 'tomato', 'pickle',
                                                       'onion', 'bacon', 'egg', 'ice']),
        lines=dict(
            perfect="That's it. That's the one. I'll be back tomorrow and I'll ask for it again.",
            okay="Close. I'll eat it. I'm not going to say I loved it.",
            wrong="This isn't what I said. It's fine. I'll eat around it."),
    ),
    dict(
        key='starcat',
        service='saturday',
        poke="Boop back.", name='Star Cat', clock='20:40',
        order="I don't care what's in it. I want it TALLER THAN ME.",
        ticket='six things or more · anything goes',
        rule=dict(min_fill=6),
        lines=dict(
            perfect="LOOK AT IT. I can't even get my mouth around it. Best night of my life.",
            okay="That's a normal burger. I asked for a monument.",
            wrong="That's a snack. I'm a cat, not a bird."),
    ),
    dict(
        key='rockstar',
        service='sunday',
        poke="Do that again and you're on the guest list.", name='Rockstar', clock='19:25',
        order="Give me whatever's loudest on that counter. Surprise me, but make it LOUD.",
        ticket='the loud ones: onion, pickles, bacon',
        rule=dict(require=['onion', 'pickle', 'bacon']),
        lines=dict(
            perfect="Onion, pickle, bacon. Yeah. That's a set list.",
            okay="Half of it's loud. The other half is a ballad.",
            wrong="This is elevator music in a bun."),
    ),
    dict(
        key='never',
        service='saturday',
        poke="Don't. I'm reading the board.",
        name='Camper', clock='22:15',
        order="Do you have the cheese with the blue in it? The one that has gone a bit "
              "interesting. That one. On its own is fine.",
        ticket='the blue cheese',
        rule=dict(require=['mold'], forbid=['cheese']),
        lines=dict(
            perfect=MOLD_LINE,
            okay="This is the ordinary cheese. I can see the difference from here.",
            wrong="There is no blue in this whatsoever."),
    ),
    dict(
        key='vesper',
        service='sunday',
        poke="Careful. The halo is decorative.",
        name='Vesper', clock='20:50',
        order="One thing. Not two, not a pile. One thing between the buns and I will be "
              "very nice about it.",
        ticket='exactly one filling',
        rule=dict(max_fill=1),
        lines=dict(
            perfect="One thing. You understood. Everyone else brings me a heap.",
            okay="It is one thing, but you have built it strangely.",
            wrong="That is a heap. I asked for one thing."),
    ),
    dict(
        key='mermaid',
        service='saturday',
        poke="Oh! ...hello.", name='Mermaid', clock='23:55',
        order="Something from the sea, please.",
        follow="...you don't have anything from the sea. Fine. Green things, then. Only green things.",
        ticket='green only: lettuce and pickles',
        rule=dict(require=['lettuce', 'pickle'],
                  forbid=['patty', 'cheese', 'tomato', 'onion', 'bacon', 'egg', 'shroom', 'ice']),
        lines=dict(
            perfect="It's not the sea. But it's the colour of the sea. Thank you for trying.",
            okay="There's something brown in here and we both know it.",
            wrong="I asked for green. This is a landfill."),
    ),
    dict(
        key='chii',
        service='friday',
        poke="Eep — sorry, was I in the way?",
        aside="Is that okay? Sorry. It's fine if it isn't.", name='Chii', clock='23:20',
        order="Cheese and tomato please. Simple. I know exactly what I want tonight.",
        change="Actually — sorry — actually can it be egg instead of tomato? Sorry. Sorry.",
        ticket='cheese · tomato',
        ticket2='cheese · egg (she changed it)',
        rule=dict(require=['cheese', 'tomato']),
        rule2=dict(require=['cheese', 'egg'], forbid=['tomato']),
        lines=dict(
            perfect="You changed it. You actually changed it. Nobody ever changes it.",
            okay="This is the first one. I did say. It's alright, I'll have it.",
            wrong="I'm sorry, I know I'm difficult. I'll eat it. Really."),
    ),
    dict(
        key='brasil',
        service='friday',
        poke="Ha! Bom dia to you too.",
        aside="If that's okay! It doesn't have to be.", name='Bom Dia', clock='22:05',
        order="Breakfast. I know it's the middle of the night. I want breakfast: egg, bacon, cheese.",
        ticket='egg · bacon · cheese',
        rule=dict(require=['egg', 'bacon', 'cheese']),
        lines=dict(
            perfect="Bom dia! It is morning somewhere and that somewhere is inside this burger.",
            okay="It's brunch. I asked for breakfast, you gave me brunch.",
            wrong="This is dinner food. I am a morning person in a night place."),
    ),
    dict(
        key='kitty',
        service='sunday',
        poke="I wan borgir... if that's okay.",
        aside="...if that's okay. She said you'd know it.", name='Kitty', clock='22:35',
        order="I want the one my friend had. The first one, Friday, right at the start. She said it was the one.",
        ticket="whatever the first customer ordered",
        rule=dict(require=['patty', 'shroom'], forbid=['cheese', 'lettuce', 'tomato', 'pickle',
                                                       'onion', 'bacon', 'egg', 'ice']),
        lines=dict(
            perfect="That's hers. You remembered a thing somebody said hours ago. I'm going to stop crying now.",
            okay="It's near. It's not hers.",
            wrong="That isn't it at all. Were you even listening to her?"),
    ),
]

RANKS = [
    (27, "COOK OF THE YEAR", "Nine for nine, breakfast through dinner. Every one of them got the thing they asked for."),
    (20, "GOOD HANDS", "Most of them left happy. The ones who didn't will be back anyway."),
    (11, "OPEN ALL DAY", "You fed everybody. Nobody has said anything nice about it."),
    (0, "THE GRILL IS ON, AT LEAST", "It was a long day and the burgers were structures."),
]
