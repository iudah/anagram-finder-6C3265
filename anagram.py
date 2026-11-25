import re
from collections import Counter

common_words_anagram=['cab', 'abc', 'scab', 'abcs', 'abet', 'beat', 'bale', 'able', 'abroad', 'aboard', 'abridge', 'brigade', 'ache', 'each', 'cane', 'acne', 'race', 'acre', 'care', 'cat', 'act', 'da', 'ad', 'add', 'dad', 'married', 'admirer', 'admonition', 'domination', 'adorn', 'radon', 'adroitly', 'idolatry', 'ages', 'sage', 'agree', 'eager', 'ha', 'ah', 'aide', 'idea', 'said', 'aids', 'ira', 'air', 'alarming', 'marginal', 'alarmingly', 'marginally', 'alert', 'later', 'alter', 'allergy', 'largely', 'gallery', 'alloy', 'loyal', 'laurel', 'allure', 'ally', 'yall', 'alms', 'slam', 'float', 'aloft', 'anglo', 'along', 'latitude', 'altitude', 'alumna', 'manual', 'ma', 'am', 'amble', 'blame', 'mean', 'mane', 'amen', 'name', 'amenity', 'anytime', 'maid', 'amid', 'among', 'mango', 'map', 'amp', 'ample', 'maple', 'and', 'dna', 'anemic', 'cinema', 'anew', 'wean', 'wane', 'angle', 'glean', 'angel', 'range', 'anger', 'nation', 'anoint', 'ant', 'tan', 'stagnation', 'antagonist', 'ante', 'neat', 'antler', 'rental', 'pea', 'ape', 'apr', 'par', 'rap', 'tap', 'apt', 'pat', 'car', 'arc', 'arch', 'char', 'are', 'ear', 'era', 'raid', 'arid', 'arise', 'raise', 'aries', 'arm', 'ram', 'mar', 'dream', 'armed', 'impart', 'armpit', 'arms', 'mars', 'art', 'rat', 'tar', 'recital', 'article', 'artist', 'strait', 'star', 'arts', 'artsy', 'stray', 'ascent', 'stance', 'has', 'ash', 'hoarse', 'ashore', 'elapse', 'please', 'asleep', 'aspire', 'praise', 'statue', 'astute', 'ta', 'at', 'eat', 'ate', 'tea', 'mat', 'atm', 'atom', 'moat', 'tentative', 'attentive', 'attentively', 'tentatively', 'tacit', 'attic', 'caution', 'auction', 'aunt', 'tuna', 'wary', 'awry', 'drawback', 'backward', 'bad', 'dab', 'bead', 'bade', 'bag', 'gab', 'gable', 'bagel', 'beak', 'bake', 'brake', 'break', 'baker', 'lamb', 'balm', 'nab', 'ban', 'nba', 'bane', 'bean', 'bra', 'bar', 'bare', 'bear', 'bleary', 'barely', 'barley', 'bran', 'barn', 'bat', 'tab', 'battle', 'tablet', 'beard', 'bread', 'beater', 'berate', 'rebate', 'bedroom', 'boredom', 'being', 'begin', 'binge', 'bowel', 'elbow', 'below', 'binary', 'brainy', 'binder', 'inbred', 'brazier', 'bizarre', 'blearily', 'reliably', 'bristle', 'blister', 'blot', 'bolt', 'bowl', 'blow', 'broad', 'board', 'gob', 'bog', 'bolster', 'lobster', 'robe', 'bore', 'brag', 'grab', 'garb', 'rabid', 'braid', 'braille', 'liberal', 'rabies', 'braise', 'bridal', 'ribald', 'brief', 'fiber', 'throb', 'broth', 'brunt', 'burnt', 'brush', 'shrub', 'rebut', 'brute', 'dub', 'bud', 'budge', 'debug', 'rebuff', 'buffer', 'bugle', 'bulge', 'rebuild', 'builder', 'snub', 'buns', 'ruby', 'bury', 'sub', 'bus', 'bust', 'stub', 'bustle', 'subtle', 'sublet', 'but', 'tub', 'cedar', 'cadre', 'face', 'cafe', 'cellar', 'recall', 'caller', 'calligraphy', 'graphically', 'calm', 'clam', 'came', 'mace', 'canoe', 'ocean', 'trance', 'recant', 'nectar', 'canter', 'cap', 'cpa', 'pace', 'cape', 'recap', 'caper', 'capitol', 'optical', 'topical', 'upscale', 'capsule', 'caring', 'racing', 'coral', 'carol', 'crap', 'carp', 'cartel', 'rectal', 'carve', 'crave', 'carving', 'craving', 'sack', 'cask', 'testcase', 'cassette', 'crate', 'cater', 'react', 'trace', 'caterer', 'terrace', 'retrace', 'cause', 'sauce', 'dc', 'cd', 'center', 'recent', 'rectify', 'certify', 'chain', 'china', 'charm', 'march', 'charts', 'starch', 'peach', 'cheap', 'cheat', 'teach', 'cheater', 'teacher', 'checkin', 'chicken', 'inch', 'chin', 'itch', 'chit', 'much', 'chum', 'circle', 'cleric', 'rustic', 'citrus', 'scalp', 'clasp', 'clay', 'lacy', 'lance', 'clean', 'cleaners', 'cleanser', 'cobbler', 'clobber', 'cold', 'clod', 'clot', 'colt', 'cloud', 'could', 'velcro', 'clover', 'coal', 'cola', 'coat', 'taco', 'oceanic', 'cocaine', 'code', 'coed', 'icon', 'coin', 'comics', 'cosmic', 'polemic', 'compile', 'complaint', 'compliant', 'recondition', 'conditioner', 'condor', 'cordon', 'once', 'cone', 'conversation', 'conservation', 'conserve', 'converse', 'considerate', 'desecration', 'unnoticed', 'continued', 'coordinate', 'decoration', 'cork', 'rock', 'corny', 'crony', 'coroner', 'crooner', 'crop', 'corp', 'sector', 'escort', 'corset', 'oct', 'cot', 'trounce', 'counter', 'recount', 'source', 'course', 'scrap', 'craps', 'tracer', 'crater', 'creation', 'reaction', 'creator', 'reactor', 'credit', 'direct', 'director', 'creditor', 'credo', 'decor', 'creep', 'crepe', 'crocus', 'succor', 'crud', 'curd', 'cruel', 'ulcer', 'cutlery', 'cruelty', 'curtsy', 'crusty', 'ragged', 'dagger', 'diary', 'dairy', 'dam', 'mad', 'made', 'dame', 'madden', 'damned', 'demand', 'garden', 'danger', 'gander', 'read', 'dear', 'dare', 'dawdle', 'waddle', 'dawn', 'wand', 'deaf', 'fade', 'deal', 'lead', 'leader', 'dealer', 'dealership', 'leadership', 'leading', 'dealing', 'delta', 'dealt', 'hatred', 'dearth', 'thread', 'death', 'hated', 'decimal', 'medical', 'decree', 'recede', 'reed', 'deer', 'defrost', 'frosted', 'deli', 'idle', 'maddening', 'demanding', 'demeanor', 'enamored', 'dome', 'demo', 'mode', 'den', 'end', 'needs', 'dense', 'destiny', 'density', 'tend', 'dent', 'depress', 'pressed', 'scented', 'descent', 'designer', 'resigned', 'desire', 'reside', 'dilate', 'detail', 'redevelop', 'developer', 'dew', 'wed', 'laid', 'dial', 'repaid', 'diaper', 'dice', 'iced', 'diet', 'tide', 'edit', 'dying', 'dingy', 'ride', 'dire', 'directions', 'discretion', 'discern', 'rescind', 'seaside', 'disease', 'disk', 'skid', 'tiredness', 'dissenter', 'drive', 'diver', 'od', 'do', 'doe', 'ode', 'does', 'dose', 'stoned', 'doesnt', 'dog', 'god', 'done', 'node', 'mood', 'doom', 'odor', 'door', 'downer', 'wonder', 'woodland', 'download', 'wordy', 'rowdy', 'dowry', 'dr', 'rd', 'grad', 'drag', 'padre', 'drape', 'spread', 'drapes', 'draw', 'ward', 'reward', 'drawer', 'redress', 'dresser', 'redid', 'dried', 'drier', 'rider', 'prod', 'drop', 'dues', 'used', 'dune', 'nude', 'dust', 'stud', 'study', 'dusty', 'dynamo', 'monday', 'layer', 'relay', 'early', 'near', 'earn', 'eastern', 'earnest', 'earth', 'heart', 'hearty', 'earthy', 'easel', 'lease', 'east', 'seat', 'segregate', 'easteregg', 'elf', 'efl', 'he', 'eh', 'eighth', 'height', 'toenail', 'elation', 'em', 'me', 'mire', 'emir', 'mite', 'emit', 'item', 'time', 'english', 'shingle', 'general', 'enlarge', 'tinsel', 'silent', 'enlist', 'listen', 'enrage', 'genera', 'enraged', 'grenade', 'eternity', 'entirety', 'entrap', 'parent', 'pique', 'equip', 'er', 're', 'etal', 'tale', 'late', 'ether', 'three', 'there', 'veer', 'ever', 'vile', 'live', 'veil', 'evil', 'wee', 'ewe', 'exalt', 'latex', 'expect', 'except', 'fare', 'fear', 'frat', 'raft', 'fart', 'feat', 'fate', 'fbi', 'fib', 'feel', 'flee', 'feet', 'fete', 'felt', 'left', 'fidget', 'gifted', 'fiendish', 'finished', 'fighter', 'freight', 'file', 'life', 'trifle', 'filter', 'finder', 'friend', 'finger', 'fringe', 'fri', 'fir', 'fire', 'rife', 'sift', 'fist', 'flair', 'frail', 'flea', 'leaf', 'shelf', 'flesh', 'flier', 'rifle', 'flit', 'lift', 'golf', 'flog', 'flow', 'wolf', 'fowl', 'flue', 'fuel', 'loaf', 'foal', 'for', 'fro', 'foster', 'forest', 'tollfree', 'foretell', 'forge', 'gofer', 'from', 'form', 'former', 'reform', 'froth', 'forth', 'reef', 'free', 'fretful', 'truffle', 'lag', 'gal', 'gap', 'gpa', 'gape', 'page', 'garret', 'garter', 'grater', 'gas', 'sag', 'gateway', 'getaway', 'gear', 'rage', 'gel', 'leg', 'genital', 'gelatin', 'gem', 'meg', 'neg', 'gen', 'teenager', 'generate', 'genre', 'green', 'manger', 'german', 'ginger', 'nigger', 'glider', 'girdle', 'girth', 'right', 'large', 'regal', 'glare', 'toga', 'goat', 'goldmine', 'modeling', 'negro', 'goner', 'ogre', 'gore', 'orgy', 'gory', 'regard', 'grader', 'grape', 'pager', 'grate', 'great', 'ring', 'grin', 'groan', 'organ', 'grown', 'wrong', 'rugged', 'grudge', 'plug', 'gulp', 'gum', 'mug', 'gunshot', 'shotgun', 'guts', 'gust', 'gusty', 'gutsy', 'tug', 'gut', 'heal', 'hale', 'halter', 'lather', 'overhang', 'hangover', 'hear', 'hare', 'heat', 'hate', 'shade', 'heads', 'heinous', 'inhouse', 'heir', 'hire', 'sphere', 'herpes', 'hes', 'she', 'when', 'hewn', 'hinge', 'neigh', 'thin', 'hint', 'hmo', 'ohm', 'uphold', 'holdup', 'hornet', 'nother', 'throne', 'horse', 'shore', 'hose', 'shoe', 'shot', 'host', 'who', 'how', 'however', 'whoever', 'hug', 'ugh', 'hustle', 'sleuth', 'region', 'ignore', 'mi', 'im', 'permission', 'impression', 'impressive', 'permissive', 'impure', 'umpire', 'incest', 'insect', 'intend', 'indent', 'iridescent', 'indiscreet', 'inter', 'inert', 'infidel', 'infield', 'kin', 'ink', 'sin', 'ins', 'insult', 'sunlit', 'integral', 'triangle', 'reduction', 'introduce', 'untried', 'intrude', 'irs', 'sir', 'isnt', 'snit', 'itll', 'lilt', 'till', 'sit', 'its', 'itself', 'stifle', 'vie', 'ive', 'junta', 'jaunt', 'keel', 'leek', 'knee', 'keen', 'peek', 'keep', 'link', 'kiln', 'kitchen', 'thicken', 'naked', 'knead', 'ko', 'ok', 'kw', 'wk', 'lain', 'nail', 'liar', 'lair', 'rail', 'leak', 'lake', 'male', 'lame', 'meal', 'mantle', 'mental', 'lament', 'mantel', 'lamp', 'palm', 'lane', 'lean', 'lap', 'pal', 'slat', 'salt', 'last', 'latent', 'talent', 'reliant', 'latrine', 'latter', 'rattle', 'layout', 'outlay', 'plea', 'leap', 'pale', 'peal', 'plate', 'petal', 'leapt', 'pleat', 'steal', 'least', 'slate', 'stale', 'leer', 'reel', 'lemon', 'melon', 'repel', 'leper', 'lever', 'revel', 'lewd', 'weld', 'silence', 'license', 'lien', 'line', 'lime', 'mile', 'lisp', 'slip', 'slit', 'silt', 'list', 'tile', 'lite', 'outlook', 'lookout', 'loop', 'pool', 'polo', 'tool', 'loot', 'lope', 'pole', 'role', 'lore', 'sole', 'lose', 'lost', 'lots', 'slot', 'lovely', 'volley', 'owl', 'low', 'lumber', 'rumble', 'plum', 'lump', 'lure', 'rule', 'lust', 'slut', 'rustle', 'luster', 'result', 'maam', 'mama', 'magenta', 'magnate', 'median', 'maiden', 'roman', 'manor', 'ramble', 'marble', 'mare', 'ream', 'marine', 'remain', 'martial', 'marital', 'remark', 'marker', 'scam', 'masc', 'sham', 'mash', 'master', 'stream', 'meat', 'mate', 'tame', 'team', 'may', 'yam', 'meet', 'teem', 'mete', 'megaton', 'montage', 'remit', 'timer', 'merit', 'meteor', 'remote', 'ragtime', 'migrate', 'mindless', 'mildness', 'slime', 'miles', 'smile', 'reclaim', 'miracle', 'molar', 'moral', 'moon', 'mono', 'moor', 'room', 'mope', 'poem', 'tm', 'mt', 'smut', 'must', 'ultimate', 'mutilate', 'pan', 'nap', 'nape', 'pane', 'neither', 'therein', 'none', 'neon', 'nerd', 'rend', 'nerve', 'never', 'nest', 'sent', 'net', 'ten', 'tenure', 'neuter', 'tureen', 'sewn', 'news', 'went', 'newt', 'thing', 'night', 'things', 'nights', 'pin', 'nip', 'tin', 'nit', 'on', 'no', 'noon', 'nono', 'peon', 'open', 'nope', 'thorn', 'north', 'ton', 'not', 'note', 'tone', 'stone', 'onset', 'notes', 'now', 'own', 'won', 'nuclear', 'unclear', 'stun', 'nuts', 'verbose', 'observe', 'oiled', 'oldie', 'oils', 'soil', 'silo', 'opt', 'top', 'pot', 'optic', 'topic', 'option', 'potion', 'roe', 'ore', 'relation', 'oriental', 'sour', 'ours', 'outer', 'route', 'tedious', 'outside', 'overeat', 'overate', 'overpass', 'passover', 'voter', 'overt', 'overtake', 'takeover', 'overturn', 'turnover', 'woe', 'owe', 'oyster', 'storey', 'pertain', 'painter', 'paltry', 'partly', 'plane', 'penal', 'panel', 'reap', 'rape', 'pare', 'pear', 'parental', 'prenatal', 'paternal', 'trap', 'rapt', 'tarp', 'part', 'taps', 'past', 'spat', 'spate', 'paste', 'pastel', 'staple', 'peat', 'pate', 'tape', 'portal', 'patrol', 'yap', 'pay', 'plead', 'pedal', 'penis', 'snipe', 'spine', 'per', 'rep', 'percussion', 'supersonic', 'perse', 'spree', 'perverse', 'preserve', 'sept', 'pest', 'step', 'shape', 'phase', 'pier', 'ripe', 'pierce', 'recipe', 'tip', 'pit', 'plains', 'spinal', 'plaster', 'stapler', 'player', 'replay', 'protein', 'pointer', 'pore', 'rope', 'report', 'porter', 'shop', 'posh', 'stop', 'post', 'spot', 'redtape', 'predate', 'tapered', 'teardrop', 'predator', 'serpent', 'present', 'supreme', 'presume', 'prey', 'pyre', 'stripe', 'priest', 'printer', 'reprint', 'procedure', 'reproduce', 'prom', 'romp', 'proton', 'pronto', 'super', 'purse', 'quiet', 'quite', 'rare', 'rear', 'rasp', 'spar', 'spray', 'raspy', 'rate', 'tear', 'rationalize', 'realization', 'raw', 'war', 'resource', 'recourse', 'rode', 'redo', 'revile', 'relive', 'remains', 'seminar', 'secure', 'rescue', 'reverse', 'reserve', 'singer', 'resign', 'risen', 'rinse', 'resin', 'siren', 'sister', 'resist', 'roster', 'resort', 'respect', 'specter', 'restrain', 'strainer', 'retina', 'retain', 'trader', 'retard', 'thinker', 'rethink', 'retinue', 'reunite', 'retrial', 'trailer', 'viewer', 'review', 'rework', 'worker', 'trio', 'riot', 'sire', 'rise', 'squire', 'risque', 'rite', 'tier', 'tire', 'viral', 'rival', 'rouge', 'rogue', 'torso', 'roost', 'roots', 'sore', 'rose', 'tore', 'rote', 'tour', 'rout', 'urn', 'run', 'ruse', 'sure', 'user', 'sacred', 'scared', 'satin', 'stain', 'saint', 'sale', 'seal', 'slave', 'salve', 'same', 'seam', 'sang', 'snag', 'sanity', 'satiny', 'satan', 'santa', 'spa', 'sap', 'save', 'vase', 'was', 'saw', 'sawn', 'swan', 'selves', 'vessel', 'senator', 'treason', 'serve', 'sever', 'verse', 'trestle', 'settler', 'setup', 'upset', 'share', 'shear', 'sheet', 'these', 'shit', 'this', 'soothing', 'shooting', 'south', 'shout', 'show', 'whos', 'tush', 'thus', 'shut', 'sidle', 'slide', 'sign', 'sing', 'singing', 'signing', 'silver', 'sliver', 'swine', 'sinew', 'sink', 'skin', 'skate', 'stake', 'steak', 'skater', 'streak', 'snail', 'slain', 'sleet', 'steel', 'spelt', 'slept', 'smother', 'thermos', 'sneak', 'snake', 'snap', 'span', 'stanch', 'snatch', 'spin', 'snip', 'snoop', 'spoon', 'tons', 'snot', 'snow', 'sown', 'sung', 'snug', 'spear', 'spare', 'stoplight', 'spotlight', 'stupor', 'sprout', 'stalk', 'talks', 'upstart', 'startup', 'state', 'taste', 'statement', 'testament', 'steer', 'terse', 'west', 'stew', 'wrest', 'strew', 'trust', 'strut', 'use', 'sue', 'wasp', 'swap', 'ways', 'sway', 'swear', 'wares', 'waste', 'sweat', 'wings', 'swing', 'swore', 'worse', 'teak', 'take', 'teens', 'tense', 'trainer', 'terrain', 'what', 'thaw', 'thirst', 'tshirt', 'worth', 'throw', 'trot', 'tort', 'tow', 'two', 'wrote', 'tower', 'wont', 'town', 'trade', 'tread', 'trained', 'tradein', 'trail', 'trial', 'trout', 'tutor', 'untie', 'unite', 'vein', 'vine', 'vote', 'veto', 'virgo', 'vigor', 'weak', 'wake', 'wander', 'warden', 'ware', 'wear', 'wrap', 'warp', 'wired', 'weird', 'wither', 'writhe']

def clean_input(text):
    cleaned=  re.sub(r"[\W_ ]", r"", text.lower())
    return cleaned, sorted(cleaned)

def analyse_anagram(text1,text2):
    clean1,sort1=clean_input(text1)
    clean2,sort2=clean_input(text2)
    is_anagram,sort= sort1==sort2 and clean1!=clean2, "".join(sort1) if sort1==sort2 else None

    s1missing=None
    s2missing=None
    if (not is_anagram) and (sort is  None):
        c2 = None
        c1=Counter(sort1)
        # print(c1)
        c2=Counter(sort2)
        # print(c2)
        c1.subtract(c2)
        s1missing = {c: -c1[c] for c in c1 if c1[c]<0}#[c for c in sort2 if c not in sort1]
        s2missing = {c: c1[c] for c in c1 if c1[c]>0}#[c for c in sort1 if c not in sort2]
    return is_anagram, sort, s1missing, s2missing


def load_file(filepath, filecallback):
    try :
        with open(filepath) as f:
            return filecallback(f)
    except Exception as e:
        print(e)

def sort_dict(f):
    sort_word={}
    for word in f:
        clean, sort = clean_input(word)
        sort ="".join(sort)
        if sort not in sort_word:
            sort_word[sort]={clean}
        else:
            sort_word[sort].add(clean)
    return sort_word

def analyse_anagram_file(path):
    dicts= load_file(path, sort_dict)
    if not dicts:
      return None, None, None, 0, None
    largest_family = max(dicts.values(), key=len)
    words = [w for fam in dicts.values() for w in fam]
    longest = max(words, key=len)
    most_common_counter = Counter(c for w in words for c in w)
    return dicts,len(words),largest_family, longest, len(dicts), most_common_counter

def cache_dict(source=common_words_anagram):
    def decorator(fn):
        def wrapper(*arg, **kwarg):
            return fn(*arg,**kwarg)
        
        return wrapper
    return decorator

# @cache_dict()
# def anagram_from_list(word):
#     clean, sort = clean_input(word)
#     sort="".join(sort)
#     if sort in anagram_from_list.dicts:
#         return anagram_from_list.dicts[sort]


# @cache_dict("3of6all.txt")
# def anagram_from_default_file(word):
#     clean, sort = clean_input(word)
#     sort="".join(sort)
#     if sort in anagram_from_default_file.dicts:
#         return anagram_from_default_file.dicts[sort]

def make_anagram_lookup(source):
    index =None 
    if isinstance(source, str):
        index=load_file(source, sort_dict)
    if isinstance(source, (list,tuple,set)):
        index= sort_dict(source)
    if not isinstance(source, (str,list,tuple,set)):
        raise RuntimeError(f"Unsupported type {type(source)!r} for anagram source")
    if index is None:
        raise RuntimeError("Could not load anagram source")
    def lookup(word):
        return index.get("".join(clean_input(word)[1]))
    return lookup

anagram_from_list = make_anagram_lookup(common_words_anagram)
anagram_from_default_file = make_anagram_lookup("3of6all.txt")


if __name__ =="__main__":
    print(clean_input("There are some people we ususally don't like to meet in life. A number of them are crazy, foolish, or unwise."))
    str1, str2 = "Is a Dormitory", "Isa Dirty room"
    print(analyse_anagram(str1, str2))
    print(analyse_anagram(str1, str1))
    print(analyse_anagram("scarred", "racecar"))
    # print([m for w in load_file("3esl.txt", sort_dict).values() if len(w)>1 for m in w])
    print(anagram_from_list("cab"))
    print(anagram_from_default_file("cab"))
    stats = analyse_anagram_file("3of6all.txt")
    print(stats)
    # dicts,largest_anagram_family, largest_word, len(dicts), most_common
    # print(f"Words: {stats[]}  Families: {stats[]}")
    # print(f"Largest family ({len(stats.largest_family)}): {sorted(stats.largest_family)}")
    # print(f"Longest word: {stats.longest_word}")
    # print(f"Most common letters: {stats.most_common_letters[:5]}")
