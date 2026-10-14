"""Shared vocabulary for displayed text. Internal progression IDs stay stable."""
import re

WORKINGS = {
    1: 'Grovecraft', 2: 'Mana Quickening', 3: 'Verdant Grafting',
    4: 'Gateweaving', 5: 'Elementium Alloy Binding', 6: 'Fey Sinew Binding',
    7: 'Ember Tempering', 8: 'Frost-Memory Inscription',
    9: 'Ancestral Threadbinding', 10: 'World-Tree Crownweaving',
}
NUMBERS = dict(zip(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'], range(1, 11)))
NUMBERS.update(dict(zip(['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN'], range(1, 11))))
NUMBER = r'(10|[1-9]|VIII|VII|III|VI|IV|IX|II|V|X|I|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten)'


def player_text(text):
    """Expand legacy references at display boundaries, never in keys or IDs."""
    text = re.sub(r'\bERA:\s*' + NUMBER + r'\b',
                  lambda m: 'Working: ' + WORKINGS[int(m[1]) if m[1].isdigit() else NUMBERS[m[1].upper()]], text,
                  flags=re.I)
    text = re.sub(r'\bEra\s*' + NUMBER + r'\b',
                  lambda m: WORKINGS[int(m[1]) if m[1].isdigit() else NUMBERS[m[1].upper()]], text,
                  flags=re.I)
    replacements = {
        '3,000 x era': '3,000–24,000 mana, depending on the bloom; check its recipe',
        '8,000 x era': '8,000–64,000 mana, depending on the bloom; check its recipe',
        '60,000 x era': '60,000–480,000 mana, depending on the bloom; check its recipe',
        'the next four eras': 'the alloy, fey-binding, tempering and inscription workings ahead',
        'six eras away': 'made through World-Tree Crownweaving',
        'three eras': 'several further workings',
        'two eras': 'the earlier workings',
        'nine eras': 'our restoration of Alfheim',
        'the next era': 'the next working',
        'the first era': 'the first working',
        'the last era': 'the final working',
        'the era before it': 'the preceding working',
        'an era milestone': 'a magical mastery milestone',
        'era milestone': 'magical mastery milestone',
    }
    for old, new in replacements.items():
        text = re.sub(re.escape(old), lambda m: new, text, flags=re.I)
    text = re.sub(r'\beras\b', 'workings', text, flags=re.I)
    text = re.sub(r'\bera\b', 'working', text, flags=re.I)
    return text
