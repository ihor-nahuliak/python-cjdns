# Written by Petru Paler
# see LICENSE.txt for license information
# http://cvs.degreez.net/viewcvs.cgi/*checkout*/bittornado/LICENSE.txt?rev=1.2
# "the MIT license"


def decode_int(x, f):
    f += 1
    newf = x.index('e', f)
    try:
        n = int(x[f:newf])
    except (OverflowError, ValueError):
        n = long(x[f:newf])
    if x[f] == '-':
        if x[f + 1] == '0':
            raise ValueError
    elif x[f] == '0' and newf != f+1:
        raise ValueError
    return (n, newf+1)


def decode_string(x, f):
    colon = x.index(':', f)
    try:
        n = int(x[f:colon])
    except (OverflowError, ValueError):
        n = (x[f:colon])
# Leading zeros are FINE --cjd
#    if x[f] == '0' and colon != f+1:
#        raise ValueError
    colon += 1
    return (x[colon:colon+n], colon+n)


def decode_list(x, f):
    r, f = [], f+1
    while x[f] != 'e':
        v, f = decode_func[x[f]](x, f)
        r.append(v)
    return (r, f + 1)


def decode_dict(x, f):
    r, f = {}, f+1
    lastkey = None
    while x[f] != 'e':
        k, f = decode_string(x, f)
        if lastkey >= k:
            raise ValueError
        lastkey = k
        r[k], f = decode_func[x[f]](x, f)
    return (r, f + 1)

decode_func = {}
decode_func['l'] = decode_list
decode_func['d'] = decode_dict
decode_func['i'] = decode_int
decode_func['0'] = decode_string
decode_func['1'] = decode_string
decode_func['2'] = decode_string
decode_func['3'] = decode_string
decode_func['4'] = decode_string
decode_func['5'] = decode_string
decode_func['6'] = decode_string
decode_func['7'] = decode_string
decode_func['8'] = decode_string
decode_func['9'] = decode_string


def bdecode_stream(x):
    return decode_func[x[0]](x, 0)


def bdecode(x):
    try:
        r, l = bdecode_stream(x)
    except (IndexError, KeyError):
        raise ValueError
    if l != len(x):
        raise ValueError
    return r


class Bencached(object):
    __slots__ = ['bencoded']

    def __init__(self, s):
        self.bencoded = s


def encode_bencached(x, r):
    r.append(x.bencoded)


def encode_int(x, r):
    r.extend(('i', str(x), 'e'))


def encode_string(x, r):
    r.extend((str(len(x)), ':', x))


def encode_list(x, r):
    r.append('l')
    for i in x:
        encode_func[type(i)](i, r)
    r.append('e')


def encode_dict(x, r):
    r.append('d')
    ilist = x.items()
    ilist.sort()
    for k, v in ilist:
        r.extend((str(len(k)), ':', k))
        encode_func[type(v)](v, r)
    r.append('e')

encode_func = {}
encode_func[type(Bencached(0))] = encode_bencached
encode_func[int] = encode_int
#encode_func[] = encode_int
encode_func[str] = encode_string
encode_func[list] = encode_list
encode_func[tuple] = encode_list
encode_func[dict] = encode_dict

try:
    from types import BooleanType
    encode_func[BooleanType] = encode_int
except ImportError:
    pass


def bencode(x):
    r = []
    encode_func[type(x)](x, r)
    return ''.join(r)


try:
    import psyco
    psyco.bind(bdecode)
    psyco.bind(bencode)
except ImportError:
    pass
