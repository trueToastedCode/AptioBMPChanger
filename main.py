from structure_helper import *
import os
import shutil
import subprocess
import requests
from patch_archive import *
from message_helper import *

ROM_PATH = 'Roms/AmericanMegatrendsInc.-207-Unlocked-Microcode-VBIOS.rom'
FV_MAIN_NESTED_GUID = 'AE717C2F-1A42-4F2B-8861-78B79CA07E07'
SPLASH_GUID = 'EF9F35A7-BC6E-4F10-961F-9A492D471A45'

ARCHIVE_PATH = 'Archive/'
LZMA_BIN_PATH = 'lzma\\lzma.exe'
BMP_PATH = 'BMP/'

TEST_MAIN_ONLY_HEADER_CREATION = False  # debugging option

"""
LZMA Non-Streamed Compression
Source: https://tukaani.org/lzma/

----------------------------------------------------------------

(1) Linux/MacOS:
Dependencies: automake, libtoolize, probably more
Install: git clone https://git.tukaani.org/lzma.git && cd lzma && ./autogen.sh && ./configure && make && cd ..
         -> You also need to update

./lzma/src/lzma/lzma -9 -c -z in >out.lzma
./lzma/src/lzma/lzma -d in.lzma >out

!!! You would also need to update the code for this !!!

----------------------------------------------------------------

-> RECOMMENDED : Compressed archives are the smallest so you can add more content.
-> My test: (1) 1108992 vs (2) 1094768
            (2) was ~1.23% smaller than (1)

(2) Windows/MacOS with Wineskin/Linux with Wine
https://www.7-zip.org/sdk.html
Install: Install python (+ flask pip package) windows version in wine, open wine cmd, navigate to this projects folder and run the execution server
Usage: cd /Users/lennard/PycharmProjects/Bios7 && python execution_server.py
       This script then makes http requests to execute the commands
Info: Open Wineskin (MacOS) cmd: Navigate to the .app wine wrapper in finder, show pkg info, open Wineskin.app, choose tools, then cmd

lzma d in.lzma out
lzma e in out.lzma -d23

!!! Currently implemented !!!

----------------------------------------------------------------
"""

# execute system command / will call the Wine/skin server
def execute(command: str):
    return requests.post('http://localhost:8080/execute', data=command)

def check_agree():
    if not os.path.exists('.agree'):
        res = input('I agree to the warnings above (Yes/No): ')
        if res.lower() == 'y' or res.lower() == 'yes':
            open('agree', 'a').close()
        else:
            print('You need to agree if you wan\'t to use this script!')
            exit(1)

if __name__ == '__main__':
    print("""
  ╭━━━┳━━━┳━━━━┳━━┳━━━╮╭━━┳╮╱╱╭╮
  ┃╭━╮┃╭━╮┃╭╮╭╮┣┫┣┫╭━╮┃╰┫┣┫╰╮╭╯┃
  ┃┃╱┃┃╰━╯┣╯┃┃╰╯┃┃┃┃╱┃┃╱┃┃╰╮┃┃╭╯
  ┃╰━╯┃╭━━╯╱┃┃╱╱┃┃┃┃╱┃┃╱┃┃╱┃╰╯┃
  ┃╭━╮┃┃╱╱╱╱┃┃╱╭┫┣┫╰━╯┃╭┫┣╮╰╮╭╯
  ╰╯╱╰┻╯╱╱╱╱╰╯╱╰━━┻━━━╯╰━━╯╱╰╯""")

    lines = 'by trueToastedCode\n' \
            '### Warning ###\n' \
            'I am not responsible for damages of any kind.\n' \
            'Use it at your own risk!'
    print_msg(lines)
    print('')
    check_agree()

    # prepare archive folder
    if os.path.exists(ARCHIVE_PATH):
        shutil.rmtree(ARCHIVE_PATH)
    os.mkdir(ARCHIVE_PATH)

    # read rom
    rom_helper = BytesHelper(fname=ROM_PATH)

    # find fv_main_nested
    fv_main_nested_offset = find_formatted_guid(guid=FV_MAIN_NESTED_GUID, data=rom_helper.data)
    if fv_main_nested_offset == -1:
        print(f'Unable to find {FV_MAIN_NESTED_GUID}')
        exit(1)

    # read and extract fv_main_nested
    fv_main_nested_file = FirmwareFile()
    fv_main_nested_file.set_from_rom(offset=fv_main_nested_offset, data=rom_helper.data)
    fv_main_nested_file_following_offset_initial = fv_main_nested_file.get_following_offset()
    print(f'FV_MAIN_NESTED found at {hex(fv_main_nested_offset)} - {hex(fv_main_nested_file_following_offset_initial - 1)}')

    # file section
    fv_main_nested_file_section = FirmwareFileSection()
    fv_main_nested_file_section.set_from_rom(nested_offset=0, data=fv_main_nested_file.body)

    # compressed body
    fv_main_nested_file_section_compressed = SectionCompressed()
    fv_main_nested_file_section_compressed.set_from_rom(
        nested_offset=fv_main_nested_file_section.get_body_start_offset(),
        data=fv_main_nested_file.body)

    # extract
    print('Decompressing...', end='')
    write_bytes(fname=f'{ARCHIVE_PATH}archive.lzma',
                data=fv_main_nested_file.body[fv_main_nested_file_section_compressed.get_following_offset():])
    if not execute(f'{LZMA_BIN_PATH} d {ARCHIVE_PATH}archive.lzma {ARCHIVE_PATH}archive'):
        print(' FAIL')
        print(f'Unable to extract the (expected) compressed body of {FV_MAIN_NESTED_GUID}')
        exit(1)
    print(' OK')

    if not TEST_MAIN_ONLY_HEADER_CREATION:
        patch_archive()

        # compress
        print('Compressing...', end='')
        if not execute(f'{LZMA_BIN_PATH} e {ARCHIVE_PATH}archive_patched {ARCHIVE_PATH}archive_patched.lzma -d23'):
            print(' FAIL')
            exit(1)
        print(' OK')

    # rewrite header and bodys
    fv_main_nested_file_section_compressed.decompressed_size = int_to_bytes(os.path.getsize(f'{ARCHIVE_PATH}archive_patched' if not TEST_MAIN_ONLY_HEADER_CREATION else f'{ARCHIVE_PATH}archive'))
    fv_main_nested_file_section.set_body(body=fv_main_nested_file_section_compressed.get_rom_bytes() +
                                              read_bytes(fname=f'{ARCHIVE_PATH}archive_patched.lzma' if not TEST_MAIN_ONLY_HEADER_CREATION else f'{ARCHIVE_PATH}archive.lzma'))
    fv_main_nested_file.set_body(body=fv_main_nested_file_section.get_rom_bytes())

    # check / correct padding
    if fv_main_nested_file.get_following_offset() > fv_main_nested_file_following_offset_initial:
        # new fv_main_nested_file got bigger, check if enough padding
        # find after fv_main_nested_file empty space
        fv_main_nested_file_following_empty_end_offset = find_empty_end(
            offset=fv_main_nested_file.get_following_offset(),
            data=rom_helper.data)
        if fv_main_nested_file_following_empty_end_offset == -1:
            print('No padding left')
            exit(1)
        fv_main_nested_file_following_empty_end_offset -= 2
        if fv_main_nested_file_following_empty_end_offset < fv_main_nested_file.get_following_offset() - 1:
            print('No padding left')
            exit(1)
    elif fv_main_nested_file.get_following_offset() < fv_main_nested_file_following_offset_initial:
        # new fv_main_nested_file got smaller, fill up with "empty bytes"
        rom_helper.fill_blocks(start_offset=fv_main_nested_file.get_following_offset(),
                               end_offset=fv_main_nested_file_following_offset_initial - 1, data=b'\xff')
        print(f'FV_MAIN_NESTED got smaller, filled up {hex(fv_main_nested_file.get_following_offset())} - {hex(fv_main_nested_file_following_offset_initial-1)}')

    # rewrite fv_main_nested_file in rom
    rom_helper.write_blocks(start_offset=fv_main_nested_offset, end_offset=fv_main_nested_file.get_following_offset()-1,
                            data=fv_main_nested_file.get_rom_bytes())
    print(f'FV_MAIN_NESTED new at {hex(fv_main_nested_offset)} - {hex(fv_main_nested_file.get_following_offset()-1)}')

    # write patched rom
    pos = ROM_PATH[::-1].find('.')
    rom_patched_fname = f'{ROM_PATH}_Patched.rom' if pos == -1 else f'{ROM_PATH[:-pos - 1]}_Patched{ROM_PATH[-pos - 1:]}'
    rom_helper.write(fname=rom_patched_fname)
    print(f'\nPatched rom saved to "{rom_patched_fname}".')
    print('Create reports with MMTool and compare patched with original. Make sure there are no files missing!')

    if TEST_MAIN_ONLY_HEADER_CREATION:
        print(f'Patched rom matches: {read_bytes(rom_patched_fname) == read_bytes(ROM_PATH)}')
