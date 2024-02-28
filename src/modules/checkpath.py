import os
import platform
import configparser
from modules.logger import *
from configuration.settings import localconfig
from tkinter import messagebox
from tkinter import filedialog

def select_yuzu_exe(self, ev = None):
    # Open a file dialog to browse and select yuzu.exe
    if self.os_platform == "Windows":
        yuzu_path = filedialog.askopenfilename(
            title=f"Please select {self.mode}.exe",
            filetypes=[("Executable files", "*.exe"), ("All Files", "*.*")]
        )
        executable_name = yuzu_path
        if executable_name.endswith("Ryujinx.exe") or executable_name.endswith("Ryujinx.Ava.exe"):
            if self.mode == "Yuzu":
                self.switchmode("true")
        if executable_name.endswith("yuzu.exe"):
            if self.mode == "Ryujinx":
                self.switchmode("true")
        if yuzu_path:
            # Save the selected yuzu.exe path to a configuration file
            save_user_choices(self, self.config, yuzu_path)
            home_directory = os.path.dirname(yuzu_path)
            fullpath = os.path.dirname(yuzu_path)
            if any(item in os.listdir(fullpath) for item in ["user", "portable"]):
                log.info(
                    f"Successfully selected {self.mode}.exe! And a portable folder was found at {home_directory}!")
                checkpath(self, self.mode)
                return yuzu_path
            else:
                log.info(f"Portable folder for {self.mode} not found defaulting to appdata directory!")
                checkpath(self, self.mode)
                return yuzu_path

            # Update the yuzu.exe path in the current session
            self.yuzu_path = yuzu_path
        else:
            checkpath(self, self.mode)
            return None
        # Save the selected yuzu.exe path to a configuration file
        save_user_choices(self, self.config, yuzu_path)
    return yuzu_path
# Define Directories for different OS or Yuzu Folders, Check if User has correct paths for User Folder.
def checkpath(self, mode):
    if self.is_extracting is True:
        self.configdir = None
        self.TOTKconfig = None
        self.nand_dir = None
        self.ryujinx_config = None
        self.sdmc = None
        self.load_dir = os.getcwd()
        self.Yuzudir = os.getcwd()
        self.Globaldir = os.getcwd()
        return

    home_directory = os.path.expanduser("~")
    # Default Dir for Linux/SteamOS
    self.os_platform = platform.system()
    if self.os_platform == "Linux":
        if mode == "Yuzu":
            flatpak = os.path.join(home_directory, ".var", "app", "org.yuzu_emu.yuzu", "config", "yuzu")
            steamdeckdir = os.path.join(home_directory, ".config", "yuzu", "qt-config.ini")

            self.Globaldir = os.path.join(home_directory, ".local", "share", "yuzu")
            self.configdir = os.path.join(self.Globaldir, "config", "qt-config.ini")
            self.TOTKconfig = os.path.join(self.Globaldir, "config", "custom")

            # Assume it's a steamdeck
            if os.path.exists(steamdeckdir):
                log.info("Detected a steamdeck!")
                self.configdir = steamdeckdir
                self.TOTKconfig = os.path.join(home_directory, ".config", "yuzu", "custom")

            # Check for a flatpak.
            if os.path.exists(flatpak):
                log.info("Detected a Yuzu flatpak!")
                self.configdir = os.path.join(flatpak, "qt-config.ini")
                self.TOTKconfig = os.path.join(flatpak, "custom")
                new_path = os.path.dirname(os.path.dirname(flatpak))
                self.Globaldir = os.path.join(new_path, "data", "yuzu")

            config_parser = configparser.ConfigParser()
            config_parser.read(self.configdir, encoding="utf-8")
            self.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{self.Globaldir}/nand'))
            self.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{self.Globaldir}/sdmc'))
            if self.nand_dir.startswith('"'):
                self.nand_dir = self.nand_dir.strip('"')[0]
            self.load_dir = os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{self.Globaldir}/load'))
            if self.nand_dir.startswith('"'):
                self.nand_dir = self.nand_dir.strip('"')[0]
            self.load_dir = os.path.join(self.load_dir, "0100F2C0115B6000")

            self.Yuzudir = os.path.normpath(os.path.join(home_directory, ".local", "share", "yuzu", "load", "0100F2C0115B6000"))
            return

        if mode == "Ryujinx":
            self.Globaldir = os.path.join(home_directory, ".config", "Ryujinx")
            flatpak = os.path.join(home_directory, ".var", "app", "org.ryujinx.Ryujinx", "config", "Ryujinx")

            if os.path.exists(flatpak):
                log.info("Detected a Ryujinx flatpak!")
                self.Globaldir = flatpak
                self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
                self.sdmc_dir = os.path.join(f"{self.Globaldir}", "sdcard")
                self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100f2c0115b6000")
                self.Yuzudir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents",
                                            "0100f2c0115b6000")
                self.ryujinx_config = os.path.join(self.Globaldir, "Config.json")
                return

            self.configdir = None
            self.TOTKconfig = None
            self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
            self.sdmc_dir = os.path.join(f"{self.Globaldir}", "sdcard")
            self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100f2C0115B6000")
            self.Yuzudir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
            self.ryujinx_config = os.path.join(self.Globaldir, "Config.json")
            return
    # Default Dir for Windows or user folder.
    elif self.os_platform == "Windows":
        yuzupath = load_yuzu_path(self, localconfig)
        userfolder = os.path.join(yuzupath, "../user/")
        portablefolder = os.path.join(yuzupath, "../portable/")
        # Check for user folder
        if mode == "Yuzu":
            if os.path.exists(userfolder):
                self.configdir = os.path.join(yuzupath, "../user/config/qt-config.ini")
                self.TOTKconfig = os.path.join(self.configdir, "../custom")
                config_parser = configparser.ConfigParser()
                config_parser.read(self.configdir, encoding="utf-8")
                self.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{os.path.join(yuzupath, "../user/nand")}'))
                self.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{os.path.join(yuzupath, "../user/sdmc")}'))
                if self.nand_dir.startswith('"'):
                    self.nand_dir = self.nand_dir.strip('"')[0]
                self.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{os.path.join(yuzupath, "../user/nand")}')), "0100F2C0115B6000")
                if self.load_dir.startswith('"'):
                    self.load_dir = self.load_dir.strip('"')[0]
                self.Yuzudir = os.path.join(home_directory, "AppData", "Roaming", "yuzu", "load", "0100F2C0115B6000")
                NEWyuzu_path = os.path.normpath(os.path.join(userfolder, "../"))
                self.Globaldir = os.path.join(NEWyuzu_path, "user")
                qt_config_save_dir = os.path.normpath(os.path.join(self.nand_dir, "../../"))
                # Warn user that their QT-Config path is INCORRECT!
                if qt_config_save_dir != NEWyuzu_path and self.warn_again == "yes":
                    message = (
                        f"WARNING: Your QT Config Save Directory may not be correct!\n"
                        f"Your saves could be in danger.\n"
                        f"Your current Yuzu directory: {NEWyuzu_path}\n"
                        f"Your QT Config Save Directory: {qt_config_save_dir}\n"
                        f"Do you want to create a backup of your save file?"
                    )
                    response = messagebox.askyesno("Warning", message, icon=messagebox.WARNING)
                    if response:
                        self.backup()
                        self.warn_again = "no"
                        log.info("Sucessfully backed up save files, in backup folder. "
                                 "Please delete qt-config in USER folder! "
                                 "Or correct the user folder paths, then use the backup file to recover your saves!")
                        pass
                    else:
                        self.warn_again = "no"
                        log.info("Warning has been declined, "
                                 "no saves have been moved!")
                return
            # Default to Appdata
            else:
                self.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "yuzu")
                self.configdir = os.path.join(self.Globaldir, "config", "qt-config.ini")
                self.TOTKconfig = os.path.join(self.configdir, "../custom")
                config_parser = configparser.ConfigParser()
                config_parser.read(self.configdir, encoding="utf-8")
                self.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{self.Globaldir}/nand'))
                self.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{self.Globaldir}/sdmc'))
                if self.nand_dir.startswith('"'):
                    self.nand_dir = self.nand_dir.strip('"')[0]
                self.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{self.Globaldir}/load')), "0100F2C0115B6000")
                if self.load_dir.startswith('"'):
                    self.load_dir = self.load_dir.strip('"')[0]
                self.Yuzudir = os.path.join(home_directory, "AppData", "Roaming", "yuzu", "load", "0100F2C0115B6000")
                return
        if mode == "Ryujinx":
            if os.path.exists(portablefolder):
                self.configdir = None
                self.TOTKconfig = None
                self.ryujinx_config = os.path.join(portablefolder, "Config.json")
                self.nand_dir = os.path.join(f"{portablefolder}", "bis", "user", "save")
                self.load_dir = os.path.join(f"{portablefolder}", "mods", "contents", "0100f2C0115b6000")
                self.sdmc_dir = os.path.join(f"{portablefolder}", "sdcard")
                self.Yuzudir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
                return
            else:
                self.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx")
                self.configdir = None
                self.TOTKconfig = None
                self.ryujinx_config = os.path.join(self.Globaldir, "Config.json")
                self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
                self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100f2C0115b6000")
                self.sdmc_dir = os.path.join(f"{self.Globaldir}", "sdcard")
                self.Yuzudir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
                return
    # Ensure the path exists.
    try:
        # attempt to create qt-config.ini directories in case they don't exist. Give error to warn user
        os.makedirs(self.nand_dir, exist_ok=True)
        os.makedirs(self.load_dir, exist_ok=True)
        os.makedirs(self.Yuzudir, exist_ok=True)
    except PermissionError as e:
        log.warrning(f"Unable to create directories, please run {self.mode}, {e}")
        self.warning(f"Unable to create directories, please run {self.mode}, {e}")

# Define OS
def DetectOS(self, mode):
    if self.os_platform == "Linux":
        log.info("Detected a Linux based SYSTEM!")
    elif self.os_platform == "Windows":
        log.info("Detected a Windows based SYSTEM!")
        if mode == "Yuzu":
            if os.path.exists(self.configdir):
                log.info("a qt-config.ini file found!")
            else:
                log.warning("qt-config.ini not found, the script will assume default appdata directories, "
                            "please reopen Yuzu for consistency and make sure TOTK is present..!")

def load_yuzu_path(self, config_file):
    if self.mode == "Yuzu":
        config = configparser.ConfigParser()
        config.read(config_file, encoding="utf-8")
        yuzu_path = config.get('Paths', 'yuzupath', fallback="Appdata")
        return yuzu_path
    if self.mode == "Ryujinx":
        config = configparser.ConfigParser()
        config.read(config_file, encoding="utf-8")
        ryujinx_path = config.get('Paths', 'ryujinxpath', fallback="Appdata")
        return ryujinx_path