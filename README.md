# Debian Setup Script
This script's primary goal is to extend already existing Debian features to the Debian desktop to make an extremely capable workstation setup.

# Supported Systems
Currently, the only supported system for this script is **Debian 12 (Bookworm) w/ KDE Plasma**. The official supported tasksel is:


- **Debian Desktop Environment**
- **KDE Plasma**
- **Standard System Utilities**

# How To Run
Run the following in a command line shell:

`/bin/sudo /bin/bash -c "$(wget -q -O - https://raw.githubusercontent.com/DEM0NAssissan7/debian-setup/main/setup.bash)"`

If that does not work, try:

`/bin/sudo /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/DEM0NAssissan7/debian-setup/main/setup.bash)"`

#### Be Advised: This script NEEDS administrator privileges in order to run

# Services
Among the services and applications installed include:
- **Flatpak** w/ Flathub
- **ZRAM** (half of system memory)
- **Pipewire** w/ Wireplumber
- **Google Chrome** (optional)
- **VLC**

All services installed are configured sanely out of the box, and almost zero setup is required. This script is totally hands-off (except for accepting the Google Chrome EULA).

More services and configurations are coming (like making Flatpak default in Discover).
