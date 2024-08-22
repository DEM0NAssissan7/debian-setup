#!/bin/bash

function check_root {
    if [ $UID != 0 ]; then
        echo "This script must be run as root."
        echo "Try sudo [command] instead."
        exit 1
    fi
}

check_root

# General functions
function echo_section_title {
    echo
    echo "<-------------------------->"
    echo $@
    echo "<-------------------------->"
    echo
}
services=""
function add_service {
    services="$services\n   * $@"
}
function show_installed_services {
    printf "Installed services:$services"
    echo
}
function apt_install {
    apt install --assume-yes $@
}
function flatpak_install {
    flatpak install -y $@
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

# Script pre-configuration
system_type="plasma"
function prompt_system_type {
    read -p "Warning: only KDE Plasma is officially supported at this time [press ENTER to acknowledge]"

}

# System setup
function setup_flatpak {
    # Copied from https://flatpak.org/setup/Debian
    echo_section_title "Setting up Flatpak"
    add_service "Flatpak, Flathub"

    apt_install flatpak plasma-discover-backend-flatpak
    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
}
function setup_pipewire {
    echo_section_title "Setting up Pipewire & Wireplumber"
    add_service "Pipewire, Wireplumber"

    apt_install wireplumber pipewire-pulse pipewire-alsa pipewire-jack
}
function setup_zram {
    # Taken from https://wiki.debian.org/ZRam
    echo_section_title "Setting up ZRAM"
    add_service "ZRAM"

    apt_install zram-tools
    echo -e "ALGO=zstd\nPERCENT=50\nPRIORITY=100" | tee -a /etc/default/zramswap
    service zramswap reload
}
function setup_system {
    setup_flatpak
    setup_pipewire
    setup_zram
}

# App setup
function install_chrome_pkg {
    echo_section_title "Installing Google Chrome"
    add_service "Google Chrome"

    chrome_pkg="google-chrome-stable_current_amd64.deb"
    wget https://dl.google.com/linux/direct/$chrome_pkg
    apt_install ./$chrome_pkg
    echo "Cleaning $PWD/$chrome_pkg"
    rm $chrome_pkg
}
function install_apps {

    # Chrome
    echo_section_title "Google Chrome"
    echo "Google Chrome terms of service: https://policies.google.com/terms https://www.google.com/chrome/terms"
    ask_prompt "Would you like to install Google Chrome? By answering yes, you automatically agree to its terms of service." install_chrome_pkg echo n

    # VLC
    echo_section_title "Installing VLC"
    add_service "VLC Media Player"
    apt_install vlc
}

# Post-installation
function reboot_system {
        echo "Rebooting system..."
        systemctl reboot
        exit
}
function exit_setup {
        echo "Exiting setup script"
        exit
}
function prompt_reboot {
    echo
    ask_prompt "Would you like to reboot your computer to complete the setup?" reboot_system exit_setup
}
function conclude_install {
    echo_section_title "Setup Complete!"
    show_installed_services

    prompt_reboot
}

# Run setup functions
setup_system
install_apps
conclude_install
