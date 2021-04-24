def bytes_to_str(data: bytes) -> str:
    return ''.join('{:02x}'.format(x) for x in data).upper()

def print_hex(msg, space=' '):
    i = 0
    while i < len(msg) - 3:
        print(msg[i:i + 2], end=space)
        i += 2
    print(msg[-2:])

def print_bytes(data: bytes, space=' '):
    print_hex(bytes_to_str(data), space)

def read_bytes(fname: str) -> bytes:
    with open(fname, 'rb') as file:
        data = file.read()
        file.close()
    return data

def write_bytes(fname: str, data: bytes):
    with open(fname, 'wb') as file:
        file.write(data)
        file.close()

def swap(s: str) -> str:
    if len(s) % 2 != 0:
        raise Exception('(swap) invalid len')
    sn = ''
    i = len(s)
    while i > 1:
        sn += s[i - 2: i]
        i -= 2
    return sn

def swap_bytes(b: bytes) -> bytes:
    return bytes.fromhex(swap(bytes_to_str(b)))

def get_checksum(data: bytes) -> int:
    return 256 - (sum(data) % 256)

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')

class BytesHelper:
    def __init__(self, fname: str = None, data: bytes = None):
        self.fname = fname
        if self.fname is None:
            if self.data is None:
                raise Exception('(BytesHelper) No filename or data provided')
            self.data = data
        else:
            with open(fname, 'rb') as file:
                self.data = file.read()
                file.close()

    def write(self, fname: str = None):
        write_bytes(fname if fname else self.fname, self.data)

    def get_blocks(self, start_offset, end_offset=-1) -> bytes:
        if end_offset == -1:
            return self.data[start_offset:]
        return self.data[start_offset:end_offset + 1]

    def write_blocks(self, start_offset: int, data: bytes, end_offset: int = None):
        if end_offset is not None:  # we can use end_offset as a check to make sure end_offset is as expected
            size = end_offset - start_offset + 1
            if len(data) != size:
                raise Exception(f'(write_blocks) Data size {len(data)} does not match size {size}')
        self.data = self.data[:start_offset] + data + self.data[start_offset + len(data):]

    def fill_blocks(self, start_offset: int, end_offset: int, data: bytes):
        offset_size = end_offset - start_offset + 1
        if offset_size < len(data):
            raise Exception('(fill) Data size is smaller than offset size')
        elif offset_size % len(data) != 0:
            raise Exception('(fill) Data does not fit between offsets')
        m = int(offset_size / len(data))
        self.data = self.data[:start_offset] + data * m + self.data[end_offset + 1:]
