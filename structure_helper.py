from bytes_helper import *
from rom_helper import *

# https://github.com/tianocore/edk2/blob/master/MdePkg/Include/Pi/PiFirmwareFile.h

class FirmwareFile:
    HEADER_SIZE = 24

    def __init__(self,
                 offset: int = None,
                 guid: bytes = None,             # 16 bytes
                 header_checksum: bytes = None,  # 1 byte
                 data_checksum: bytes = None,    # 1 byte
                 file_type: bytes = None,        # 1 byte
                 file_attributes: bytes = None,  # 1 byte
                 size: bytes = None,             # 3 bytes
                 file_state: bytes = None,       # 1 byte
                 body: bytes = None):            # x bytes
        # --------------------------------- Total: 24 + x bytes
        self.offset = offset
        self.guid = guid
        self.header_checksum = header_checksum
        self.data_checksum = data_checksum
        self.file_type = file_type
        self.file_attributes = file_attributes
        self.size = size
        self.file_state = file_state
        self.body = body

    def set_from_rom(self, offset: int, data: bytes):
        self.offset = offset
        self.guid = get_guid_from_rom(data[offset:offset+16])
        self.header_checksum = data[offset+16:offset+17]
        self.data_checksum = data[offset+17:offset+18]
        self.file_type = data[offset+18:offset+19]
        self.file_attributes = data[offset+19:offset+20]
        self.size = swap_bytes(data[offset+20:offset+23])
        self.file_state = data[offset+23:offset+24]
        self.body = data[offset+FirmwareFile.HEADER_SIZE:offset+int_from_bytes(self.size)]

    def print_info(self):
        print('[FirmwareFile]')
        print('Offset: 0x' + hex(self.offset)[2:].upper())
        print('GUID: ' + get_guid_for_print(self.guid))
        print('HeaderChecksum: 0x' + bytes_to_str(self.header_checksum))
        print('DataChecksum: 0x' + bytes_to_str(self.data_checksum))
        print('FileType: 0x' + bytes_to_str(self.file_type))
        print('FileAttributes: 0x' + bytes_to_str(self.file_attributes))
        print('Size: 0x' + bytes_to_str(self.size))
        print('FileState: 0x' + bytes_to_str(self.file_state))
        print('Body (size): 0x' + hex(len(self.body))[2:].upper())

    def get_header_checksum(self) -> int:
        return get_checksum(bytes.fromhex(bytes_to_str(self.guid + self.file_type + self.file_attributes + self.size)))

    def set_body(self, body: bytes):
        self.body = body
        self.data_checksum = int_to_bytes(get_checksum(body))
        self.size = int_to_bytes(len(body) + FirmwareFile.HEADER_SIZE)
        self.header_checksum = int_to_bytes(self.get_header_checksum())

    def get_body_start_offset(self) -> int:
        return self.offset + FirmwareFile.HEADER_SIZE

    def get_following_offset(self) -> int:
        return self.offset + int_from_bytes(self.size)

    def get_rom_bytes(self):
        return bytes.fromhex(f'{get_guid_for_rom(bytes_to_str(self.guid))}'
                             f'{"{:02x}".format(int_from_bytes(self.header_checksum))}'
                             f'{"{:02x}".format(int_from_bytes(self.data_checksum))}'
                             f'{"{:02x}".format(int_from_bytes(self.file_type))}'
                             f'{"{:02x}".format(int_from_bytes(self.file_attributes))}'
                             f'{swap("{:06x}".format(int_from_bytes(self.size)))}'
                             f'{"{:02x}".format(int_from_bytes(self.file_state))}') + \
               self.body

class FirmwareFileSection:
    HEADER_SIZE = 4

    def __init__(self,
                 nested_offset: int = None,
                 size: bytes = None,        # 3 bytes
                 type: bytes = None,        # 1 bytes
                 body: bytes = None):       # x bytes
        # ---------------------------- Total: 4 + x bytes
        self.nested_offset = nested_offset
        self.size = size
        self.type = type
        self.body = body

    def set_body(self, body: bytes, type: bytes = None):
        self.body = body
        if type is not None:
            self.type = type
        self.size = int_to_bytes(len(body) + FirmwareFileSection.HEADER_SIZE)

    def set_from_rom(self, nested_offset: int, data: bytes):
        self.nested_offset = nested_offset
        self.size = swap_bytes(data[nested_offset:nested_offset+3])
        self.type = data[nested_offset+3:nested_offset+4]
        self.body = data[nested_offset+4:nested_offset+int_from_bytes(self.size)]

    def print_info(self):
        print('[FirmwareFileSection]')
        print('NestedOffset: 0x' + hex(self.nested_offset)[2:].upper())
        print('Size: 0x' + bytes_to_str(self.size))
        print('Type: 0x' + bytes_to_str(self.type))
        print('Body (size): 0x' + hex(len(self.body))[2:].upper())

    def get_body_start_offset(self) -> int:
        return self.nested_offset + FirmwareFileSection.HEADER_SIZE

    def get_following_offset(self) -> int:
        return self.nested_offset + int_from_bytes(self.size)

    def get_rom_bytes(self):
        return bytes.fromhex(f'{swap("{:06x}".format(int_from_bytes(self.size)))}'
                             f'{"{:02x}".format(int_from_bytes(self.type))}') + \
               self.body

class SectionCompressed:
    HEADER_SIZE = 5

    def __init__(self,
                 nested_offset: int = None,
                 decompressed_size: bytes = None,  # 3 bytes
                 block_size: bytes = None):        # 2 bytes
        # ----------------------------------- Total: 5 bytes
        self.nested_offset = nested_offset
        self.decompressed_size = decompressed_size
        self.block_size = block_size

    def set_from_rom(self, nested_offset: int, data: bytes):
        self.nested_offset = nested_offset
        self.decompressed_size = swap_bytes(data[nested_offset:nested_offset+3])
        self.block_size = swap_bytes(data[nested_offset+3:nested_offset+5])

    def print_info(self):
        print('[SectionCompressed]')
        print('NestedOffset: 0x' + hex(self.nested_offset)[2:].upper())
        print('DecompressedSize: 0x' + bytes_to_str(self.decompressed_size))
        print('BlockSize: 0x' + bytes_to_str(self.block_size))

    def get_following_offset(self) -> int:
        return self.nested_offset + SectionCompressed.HEADER_SIZE

    def get_rom_bytes(self):
        return bytes.fromhex((f'{swap("{:06x}".format(int_from_bytes(self.decompressed_size)))}'
                              f'{swap("{:04x}".format(int_from_bytes(self.block_size)))}'))

class BMP:
    HEADER_SIZE = 54

    def __init__(self,
                 file_type: bytes = None,           # 2 bytes
                 file_size: bytes = None,           # 4 bytes
                 reserved_1: bytes = None,          # 2 bytes
                 reserved_2: bytes = None,          # 2 bytes
                 pixel_data_offset: bytes = None,   # 4 bytes
                 header_size: bytes = None,         # 4 bytes
                 image_width: bytes = None,         # 4 bytes
                 image_height: bytes = None,        # 4 bytes
                 planes: bytes = None,              # 2 bytes
                 bits_per_pixel: bytes = None,      # 2 bytes
                 compression: bytes = None,         # 4 bytes
                 image_size: bytes = None,          # 4 bytes
                 x_pixels_per_meter: bytes = None,  # 4 bytes
                 y_pixels_per_meter: bytes = None,  # 4 bytes
                 total_colors: bytes = None,        # 4 bytes
                 important_colors: bytes = None,    # 4 bytes
                 other: bytes = None,               # x bytes
                 pixel_data: bytes = None):         # y bytes
        # ----------------------------- Total: 54 + x + y bytes
        self.file_type = file_type
        self.file_size = file_size
        self.reserved_1 = reserved_1
        self.reserved_2 = reserved_2
        self.pixel_data_offset = pixel_data_offset
        self.header_size = header_size
        self.image_width = image_width
        self.image_height = image_height
        self.planes = planes
        self.bits_per_pixel = bits_per_pixel
        self.compression = compression
        self.image_size = image_size
        self.x_pixels_per_meter = x_pixels_per_meter
        self.y_pixels_per_meter = y_pixels_per_meter
        self.total_colors = total_colors
        self.important_colors = important_colors
        self.other = other
        self.pixel_data = pixel_data

    def set_from_rom(self, data: bytes):
        self.file_type = data[:2]
        self.file_size = swap_bytes(data[2:6])
        self.reserved_1 = swap_bytes(data[6:8])
        self.reserved_2 = swap_bytes(data[8:10])
        self.pixel_data_offset = swap_bytes(data[10:14])
        self.header_size = swap_bytes(data[14:18])
        self.image_width = swap_bytes(data[18:22])
        self.image_height = swap_bytes(data[22:26])
        self.planes = swap_bytes(data[26:28])
        self.bits_per_pixel = swap_bytes(data[28:30])
        self.compression = swap_bytes(data[30:34])
        self.image_size = swap_bytes(data[34:38])
        self.x_pixels_per_meter = swap_bytes(data[38:42])
        self.y_pixels_per_meter = swap_bytes(data[42:46])
        self.total_colors = swap_bytes(data[46:50])
        self.important_colors = swap_bytes(data[50:54])
        self.other = data[54:int_from_bytes(self.pixel_data_offset)]
        self.pixel_data = data[int_from_bytes(self.pixel_data_offset):int_from_bytes(self.file_size)]

    def get_rom_bytes(self) -> bytes:
        return bytes.fromhex(f'{"{:04x}".format(int_from_bytes(self.file_type))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.file_size)))}'
                             f'{swap("{:04x}".format(int_from_bytes(self.reserved_1)))}'
                             f'{swap("{:04x}".format(int_from_bytes(self.reserved_2)))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.pixel_data_offset)))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.header_size)))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.image_width)))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.image_height)))}'
                             f'{swap("{:04x}".format(int_from_bytes(self.planes)))}'
                             f'{swap("{:04x}".format(int_from_bytes(self.bits_per_pixel)))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.compression)))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.image_size)))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.x_pixels_per_meter)))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.y_pixels_per_meter)))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.total_colors)))}'
                             f'{swap("{:08x}".format(int_from_bytes(self.important_colors)))}') + \
               self.other + \
               self.pixel_data
