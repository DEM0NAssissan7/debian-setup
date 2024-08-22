# Debian Setup Script
This script's primary goal is to extend already existing Debian features to the Debian desktop to make an extremely capable workstation setup.

# Services
Among the services and applications installed include:
- Flatpak w/ Flathub
- ZRAM (half of system memory)
- Pipewire w/ Wireplumber
- Google Chrome (optional)
- VLC

All services installed are configured sanely out of the box, and almost zero setup is required. This script is totally hands-off (except for accepting the Google Chrome EULA).

More services and configurations are coming (like making Flatpak default in Discover), but this script accomplishes its basic task very well.

# Supported Systems
Currently, the only supported system for this script is **Debian 12 (Bookworm) w/ KDE Plasma**. The official tasksel goes as follows:


- **Debian Desktop Environment**
- **KDE Plasma**
- **Standard System Utilities**
