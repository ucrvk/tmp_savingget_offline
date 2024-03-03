import os
from shutil import rmtree
from pathlib import Path
from zipfile import ZipFile
from typing import List
from shutil import copy
import winshell
import sys


def get_shortcut_target(shortcut_path):
    try:
        # 使用winshell模块打开快捷方式
        shortcut = winshell.shortcut(shortcut_path)
        # 获取目标路径
        target_path = shortcut.path
        # 检查目标路径是否存在
        if os.path.exists(target_path):
            return target_path
        else:
            return ""
    except Exception as e:
        print("Error accessing shortcut:", e)
        return ""


def detctDefaultDir() -> List[str]:
    """
    检测默认游戏目录
    :return: 返回默认游戏目录,找不到返回空串
    """
    if os.path.exists(
        Path(os.path.expanduser(r"~\Documents\Euro Truck Simulator 2\profiles"))
    ):
        DOCUMENTS_DIR = (
            str(
                Path(os.path.expanduser(r"~\Documents\Euro Truck Simulator 2\profiles"))
            )
            + "\\"
        )
    else:
        DOCUMENTS_DIR = ""
    if os.path.exists(
        Path(os.path.expanduser(r"~\Documents\Euro Truck Simulator 2\readme.rtf.lnk"))
    ):
        GAME_DIR = get_shortcut_target(
            os.path.expanduser(r"~\Documents\Euro Truck Simulator 2\readme.rtf.lnk")
        ).rstrip("readme.rtf")
    else:
        GAME_DIR = ""
    return [DOCUMENTS_DIR, GAME_DIR]


dafaultDirectory = detctDefaultDir()


def deleteDirectory(directory) -> None:
    if os.path.exists(directory):
        os.rmdir(directory)


def get_resource_path(relative_path) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def delDisabled(dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".disabled"):
                file_path = os.path.join(root, file)
                new_file_path = os.path.join(
                    root, file[:-8]
                )  # 删除文件名中的.disabled后缀

                # 检查新文件名是否已经存在
                if os.path.exists(new_file_path):
                    os.remove(
                        file_path
                    )  # 如果新文件名已经存在，则直接删除.disabled文件
                else:
                    # 如果新文件名不存在，则删除.disabled后缀
                    os.rename(file_path, new_file_path)


def get_recently_modified_folder(directory) -> str:
    folders = [
        f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))
    ]
    if not folders:
        return None

    recently_modified_folder = None
    recent_modified_time = float("-inf")

    for folder_name in folders:
        folder_path = os.path.join(directory, folder_name)
        modified_time = os.path.getmtime(folder_path)

        if modified_time > recent_modified_time:
            recent_modified_time = modified_time
            recently_modified_folder = folder_path

    return recently_modified_folder


def getConfigFile(directory) -> list:
    try:
        targetfodder = get_recently_modified_folder(directory)
    except FileNotFoundError:
        try:
            targetfodder = get_recently_modified_folder(
                directory + "..\\steam_profiles\\"
            )
        except FileNotFoundError:
            return []
    PossibleTargetFile = (
        targetfodder + "\\" + "config.cfg",
        targetfodder + "\\" + "config_local.cfg",
        targetfodder + "\\" + "controls.sii",
    )
    targetFile = []
    for file in PossibleTargetFile:
        if os.path.exists(file):
            targetFile.append(file)
    return targetFile


def changeConfigFile(directory, StartFile) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)
    for file_path in StartFile:
        if not os.path.exists(file_path):
            continue
        try:
            file_name = os.path.basename(file_path)
            target_file_path = os.path.join(directory, file_name)
            copy(file_path, target_file_path)
        except Exception as e:
            print(f"复制文件时出现错误: {e}")


def findZipfile(dir=".") -> str:
    with os.scandir(dir) as entries:
        for entry in entries:
            if entry.name.endswith(".zip"):
                return entry.name
    return None
