from main import *
from rom_helper import *
import tableprint

def patch_archive():
    archive_helper = BytesHelper(fname=f'{ARCHIVE_PATH}archive')

    # find guid file offset
    guid_fw_file_offset = find_formatted_guid(guid=SPLASH_GUID, data=archive_helper.data)
    if guid_fw_file_offset == -1:
        print(f'Unable to find {SPLASH_GUID}')
        exit(1)

    # read and extract guid file
    guid_file = FirmwareFile()
    guid_file.set_from_rom(offset=guid_fw_file_offset, data=archive_helper.data)
    guid_fw_file_following_offset = guid_file.get_following_offset()

    # file section
    guid_file_section = FirmwareFileSection()
    guid_file_section.set_from_rom(nested_offset=0, data=guid_file.body)

    # find bmp magic bytes offsets
    bmp_offsets = find_magic_bytes(magic_bytes=b'\x42\x4d', data=guid_file_section.body)
    if len(bmp_offsets) == 0:
        print('')
        exit(1)

    # prepare bmp folder
    if os.path.exists(BMP_PATH):
        shutil.rmtree(BMP_PATH)
    os.mkdir(BMP_PATH)

    # get info
    write_bytes(fname=f'{BMP_PATH}bmp_archive', data=guid_file_section.body)
    bmp_infos = []
    for i in range(len(bmp_offsets)):
        bmp = BMP()
        bmp.set_from_rom(data=guid_file_section.body[bmp_offsets[i]:])
        bmp_infos.append([i+1,
                          hex(bmp_offsets[i]),
                          f'{int_from_bytes(bmp.image_width)}x{int_from_bytes(bmp.image_height)}'])
        write_bytes(fname=f'{BMP_PATH}{i+1}.bmp', data=bmp.get_rom_bytes())  # extract image
    print('BMP images extracted.')

    # let the user choose which to patch
    # option = 0
    tableprint.table(bmp_infos, headers=['Option', 'Offset', 'Resolution'], align='center')
    while True:
        try:
            option = int(input('Option: '))
        except:
            print('Number is needed.')
            continue
        if 0 < option < len(bmp_infos):
            option -= 1
            break
        print('Invalid.')

    # let the use choose new image
    # new_image_path = 'splash_patch.bmp'
    while True:
        new_image_path = input('Replacement path: ')
        if os.path.exists(new_image_path):
            break
        print('Unable to find.')

    # replace bmp
    old_bmp = BMP()
    old_bmp.set_from_rom(guid_file_section.body[bmp_offsets[option]:])
    guid_file_section.set_body(body=guid_file_section.body[:bmp_offsets[option]] +
                                    read_bytes(new_image_path) +
                                    guid_file_section.body[bmp_offsets[option]+int_from_bytes(old_bmp.file_size):])
    guid_file.set_body(body=guid_file_section.get_rom_bytes())
    guid_file_new_bytes = guid_file.get_rom_bytes()

    # replace splash guid file
    if guid_fw_file_offset + len(guid_file_new_bytes) != guid_fw_file_following_offset:
        print(f'{SPLASH_GUID} size changed! Make sure the replacement image has the same size!')
        exit(1)
    archive_helper.write_blocks(start_offset=guid_fw_file_offset, end_offset=guid_fw_file_following_offset-1, data=guid_file_new_bytes)

    # save
    archive_helper.write(fname=f'{ARCHIVE_PATH}archive_patched')
