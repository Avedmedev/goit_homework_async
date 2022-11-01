import asyncio
import shutil
from aiopath import AsyncPath
from typing import List
import logging
import inspect


logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


async def get_list_folders(target_folder_: AsyncPath) -> List[AsyncPath]:
    folders = [target_folder_]
    async for el in target_folder_.iterdir():
        if await el.is_dir():
            r = get_list_folders(el)
            if r:
                folders = folders + await r
    return folders


async def sort_folder(target_dir: AsyncPath):

    logger.info(f'function {inspect.stack()[0][3]} started - {target_dir}')

    files = []

    [files.append(el) async for el in target_dir.iterdir() if await el.is_file()]

    # get set of file extensions in target directory
    ext_set = set(map(lambda file_name: file_name.suffix, files))

    # make directories named by file extension
    [await (target_dir / ext.upper()).mkdir(exist_ok=True, parents=True) for ext in ext_set]

    # move files to directory with own name
    for file in files:
        if file.suffix:
            try:
                shutil.move(file, target_dir / file.suffix.upper())
            except Exception as err:
                logger.info(f'Raised exception: {err}')

    logger.info(f'function {inspect.stack()[0][3]} finished - {target_dir}')

    return True


async def folder_walk(target_folder_: AsyncPath):

    # get list folders
    folders = await get_list_folders(target_folder_)

    print(*folders, sep='\n')

    # create tasks
    tasks = [asyncio.create_task(sort_folder(folder)) for folder in folders]

    [await task for task in tasks]


if __name__ == '__main__':

    target_folder = 'trash'

    asyncio.run(folder_walk(AsyncPath(target_folder)))

    # while True:
    #     target_folder = input("insert trash folder path or type 'exit': ")
    #
    #     if target_folder == 'exit':
    #         break
    #     else:
    #         asyncio.run(folder_walk(AsyncPath(target_folder)))
