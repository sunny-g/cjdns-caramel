class EncodeError(ValueError):
    pass

class DecodeError(ValueError):
    pass

def encode(data):
    if isinstance(data, int):
        return encode_int(data)
    elif isinstance(data, bytes):
        return encode_string(data)
    elif isinstance(data, str):
        return encode_string(data.encode())
    elif isinstance(data, list):
        return encode_list(data)
    elif isinstance(data, dict):
        return encode_dict(data)
    else:
    	raise EncodeError("Only ints, strings, lists and dicts can be bencoded")

def encode_int(data):
    return b'i' + str(data).encode() + b'e'

def encode_string(data):
    return str(len(data)).encode() + b':' + data

def encode_list(data):
    elist = b'l'
    for item in data:
        elist += encode(item)
    return elist + b'e'

def encode_dict(data):
    edict = b'd'
    keys = list(data.keys())
    keys.sort()
    for key in keys:
        ekey  = encode(key)
        eitem = encode(data[key])
        edict += ekey + eitem
    return edict + b'e'

def decode(data):
    if len(data) < 1:
        return None
    else:
        (value, remaining) = decode_next(data)
        return value

def decode_next(data, start=0):
    if isinstance(data, str):
        data = data.encode()

    data_type = chr(data[start])

    if data_type == 'i':
        func = decode_int
    elif data_type == 'l':
        func = decode_list
    elif data_type == 'd':
        func = decode_dict
    elif data_type.isdigit():
        func = decode_string
    else:
        raise DecodeError("Unknown data type: " + data_type)
    
    return func(data, start)

def decode_int(data, start=0):
    if chr(data[start]) != 'i':
        raise DecodeError("Not an int")

    start += 1
    end = data.find(b'e', start)
    if end < 0: raise DecodeError("Improperly terminated int")

    try:
        value = int(data[start:end])
    except ValueError:
        raise DecodeError("Invalid int format")

    return (value, end + 1)

def decode_string(data, start=0):
    colon = data.find(b':', start)
    if colon < 0: raise DecodeError("String length not terminated with a colon")

    try:
        length = int(data[start:colon])
    except ValueError:
        raise DecodeError("Invalid string length")

    if length < 0:
        raise DecodeError("Negative string length")

    start = colon + 1
    end = start + length

    if end > len(data):
        raise DecodeError("Incorrect string length")

    value = data[start:end].decode('utf-8')
    return (value, end)

def decode_list(data, start=0):
    def end_of_list(data, index):
        try:
            return data[index] == ord('e')
        except IndexError:
            raise DecodeError("Improperly terminated list")

    if chr(data[start]) != 'l':
        raise DecodeError("Not a list")

    start += 1
    value = []

    while not end_of_list(data, start):
        item, start = decode_next(data, start)
        value.append(item)

    return (value, start+1)

def decode_dict(data, start=0):
    def end_of_dict(data, index):
        try:
            return data[index] == ord('e')
        except IndexError:
            raise DecodeError("Improperly terminated dict")

    if chr(data[start]) != 'd':
        raise DecodeError("Not a dict")

    start += 1
    value = {}

    while not end_of_dict(data, start):
        k, start = decode_next(data, start)

        if end_of_dict(data, start):
            raise DecodeError("Dict contained odd number of elements")

        v, start = decode_next(data, start)

        try:
            value[k] = v
        except TypeError:
            raise DecodeError("Dict keys must be either strings or ints")

    return (value, start+1)

if __name__ == '__main__':
	assert(encode(4) == b'i4e')
	assert(encode(0) == b'i0e')
	assert(encode(-22) == b'i-22e')

	assert(encode('') == b'0:')
	assert(encode('Mmph') == b'4:Mmph')
	assert(encode(b'snowman') == b'7:snowman')

	assert(encode([]) == b'le')
	assert(encode([0, 'c', 'vm']) == b'li0e1:c2:vme')

	assert(encode({}) == b'de')
	assert(encode({'z': 1, 'a': 'true'}) == b'd1:a4:true1:zi1ee')
	assert(encode({'b': [1, 2], '00': {}}) == b'd2:00de1:bli1ei2eee')
	