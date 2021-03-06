import random
import string

def generate_pwd():
    chars = list('{}{}'.format(string.ascii_letters, string.digits))
    random.shuffle(chars)
    grps = []

    for i in range(random.randint(4,6)):
        grp = ''.join(random.choices(chars,k=random.randint(3,5)))
        grps.append(grp)
        
    return '-'.join(grps)

