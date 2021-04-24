from bytes_helper import *

def find_magic_bytes(magic_bytes: bytes, data: bytes):
    offsets = []
    offset = 0
    while offset <= len(data) - len(magic_bytes):
        offset_res = data.find(magic_bytes, offset)
        if offset_res == -1:
            break
        offsets.append(offset_res)
        offset = offset_res + len(magic_bytes)
    return offsets

def find_formatted_guid(guid: str, data: bytes) -> int:
    guid_rom = bytes.fromhex(get_guid_for_rom(guid.replace('-', '')))
    offset = data.find(b'\xff\xff' + guid_rom)
    if offset != -1:
        return offset + 2
    offset = data.find(b'\x00\x00' + guid_rom)
    return offset + 2 if offset != -1 else -1

def get_guid_from_rom(guid: bytes) -> bytes:
    s = bytes_to_str(guid)
    return bytes.fromhex(f'{swap(s[:8])}{swap(s[8:12])}{swap(s[12:16])}{s[16:32]}')

def get_guid_for_rom(guid: str) -> str:
    return f'{swap(guid[:8])}{swap(guid[8:12])}{swap(guid[12:16])}{guid[16:32]}'

def get_guid_for_print(guid: bytes) -> str:
    s = bytes_to_str(guid)
    return f'{s[:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:32]}'

def find_empty_end(offset: int, data: bytes, fill_type: bytes = b'\xff'):
    if data[offset:offset+1] != fill_type:
        return -1
    current_offset = offset + 1
    while current_offset < len(data):
        if data[current_offset:current_offset+1] != fill_type:
            break
        current_offset += 1
    return current_offset - 1
