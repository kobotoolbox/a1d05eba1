import string
import random

def anchor_generator():
    length = 9
    alphabet = string.ascii_lowercase + string.digits
    return ''.join([
        random.choice(string.ascii_lowercase),
    ] + [
        random.choice(alphabet) for _ in range(length - 1)
    ])
