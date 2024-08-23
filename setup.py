#!/bin/python3
from enum import Enum

import subprocess
import os
import tty
import sys
import termios

# Ensure the program has root permissions
if os.getuid() != 0:
    print("This program must be run as root.")
    exit()

# General functions
def prompt(message, default):
    yes_no_prompt = "[Y/n]"
    _default = True
    if default == False:
        yes_no_prompt = "[y/N]"
        _default = False
    i = input(message + " " + yes_no_prompt + ": ").lower()

    if i == "":
        return _default

    if i == "y" or i == "yes":
        return True

    if i == "n" or i == "no":
        return False

def new_section(title):
    longline = "<------------------------------>"
    print("\n" + longline)
    print(title)
    print(longline + "\n")



# Tasks
class Category(Enum):
    SERVICE=0
    PACKAGE=1
    FLATPAK=2
    APP=3

def get_pretty_category(category):
    switcher = {
        0: "service",
        1: "package",
        2: "flatpak",
        3: "application",
    }

    return switcher.get(category, "NO TASK CATEGORY FOUND. RUNNING TASK")

tasks = []
# Redefine some commands for the sake of scalability
bash_functions = """
function apt {
    /usr/bin/apt --assume-yes $@
}
function ask_prompt {
    # Argument 1: Message
    # Argument 2: If yes (function name)
    # 3: If no (function name)
    # 4: Default

    message=$1
    yes=$2
    no=$3

    default=$yes
    p="[Y/n]"

    if [ -z $4 ]; then
        true
    elif [ $4 == "n" ]; then
        default=$no
        p="[y/N]"
    fi


    read -p "$message $p: " input
    if [ -z $input ]; then
        $default
    elif [ ${input,,} == "y" -o ${input,,} == "yes" ]; then
        $yes
    elif [ ${input,,} == "n" -o ${input,,} == "no" ]; then
        $no
    else
        ask_prompt $@
    fi
}

"""
system_needs_reboot=False
class Task:
    name="Task"
    category=Category.SERVICE.value
    script="echo Task"
    selected=True
    reboot=False
    def __init__(self, name, category, script, *args, **kwargs):
        self.name = name
        self.category = category.value
        self.pretty_category = get_pretty_category(self.category)
        self.script = script
        self.reboot = kwargs.get("reboot", False)
        self.selected = kwargs.get("selected", True)
        tasks.append(self)

    def run(self):
        new_section("Installing " + self.name + " (" + self.pretty_category + ")...")
        subprocess.run(bash_functions + self.script, shell=True, executable="/bin/bash")
        # If a service needs to reboot, we prompt the user at the end to reboot if they want
        global system_needs_reboot
        system_needs_reboot = system_needs_reboot or self.reboot
    
    def get_selected_status(self):
        if self.selected == True:
            return "X"
        if self.selected == False:
            return " "
    
    def enable(self):
        self.selected = True
    
    def disable(self):
        self.selected = False
    
    def toggle(self):
        if self.selected == True:
            self.disable()
        elif self.selected == False:
            self.enable()
        return self.selected

# User task selection
def show_tasks():
    i = 0
    for task in tasks:
        i = i + 1
        print("[" + task.get_selected_status() + "] ("+str(i)+"): " + task.name + " (" + task.pretty_category + ")")

def show_prompt_info():
    os.system("clear")
    print()
    print("Tasks:")
    show_tasks()
    print()
    print("Enter number (e.g '1' or '2') to toggle associated selection")
    print()
    print("To enable all tasks, press 'e'")
    print("To disable all tasks, press 'd'")
    print()
    print("To begin installation, press [ENTER]")
    print("To QUIT, press 'q'")
    print()

def prompt_task_selection():
    show_prompt_info()
    orig_settings = termios.tcgetattr(sys.stdin)

    tty.setcbreak(sys.stdin)
    global i
    i=0
    while i != chr(13): # Enter
        i=sys.stdin.read(1)[0]
        if "e" in i:
            for task in tasks:
                task.enable()
            show_prompt_info()
        elif "d" in i:
            for task in tasks:
                task.disable()
            show_prompt_info()
        elif "q" in i:
            quit_program()
            break
        elif '\n' in i:
            break
        else:
            i = i.split(" ")
            try:
                for num in i:
                    tasks[int(num) - 1].toggle()
                show_prompt_info()
            except:
                continue
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)

def run_selected_tasks():
    for task in tasks:
        if task.selected == True:
            task.run()

def finalize():
    for i in range(5):
        print()
    new_section("Tasks completed!")
    if system_needs_reboot == True:
        prompt_reboot()

def quit_program():
    for i in range(5):
        print()
    print("Exiting...")
    exit()
    
def prompt_reboot():
    # os.system("clear")
    i = prompt("To finalize the installation, would you like to restart your computer?", "n")
    if i == True:
        os.system("systemctl reboot")


# System information collector
# We need to collect certain, very basic system information in order to
# properly determine which packages to install
Task("Flatpak w/ Flathub", Category.PACKAGE,"""
            apt install flatpak plasma-discover-backend-flatpak
            flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
            """, reboot=True)
Task("ZRAM", Category.SERVICE, """
            apt install zram-tools
            echo -e "ALGO=zstd\nPERCENT=65\nPRIORITY=100" | tee -a /etc/default/zramswap
            service zramswap reload
            """)
Task("Command Not Found", Category.PACKAGE,"""
            apt install command-not-found
            apt update
            """)
Task("Pipewire w/ Wireplumber", Category.PACKAGE,
            "apt install pipewire-audio pipewire-jack",
            reboot=True)
Task("VLC", Category.APP,
            "apt install vlc")

# Controversial
Task("Google Chrome", Category.APP,"""
            echo "Google Chrome terms of service: https://policies.google.com/terms https://www.google.com/chrome/terms"
            echo "Would you like to install Google Chrome? By installing Google Chrome, you agree to its terms of service."
            ask_prompt "Do you want to install Google Chrome?" true exit

            chrome_pkg="google-chrome-stable_current_amd64.deb"
            wget https://dl.google.com/linux/direct/$chrome_pkg
            apt install ./$chrome_pkg
            echo "Cleaning $PWD/$chrome_pkg"
            rm $chrome_pkg
            """, selected=False)

prompt_task_selection()
# After user made selection
run_selected_tasks()
finalize()
quit_program()