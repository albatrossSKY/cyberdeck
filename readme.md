# ⚡ CYBERDECK // NODE

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

A cross-platform, highly modular, terminal-based system health and data dashboard. 

Built with [Textual](https://github.com/Textualize/textual), Cyberdeck transforms your standard terminal into a high-density matrix display, providing real-time system diagnostics, network latency, local weather, and live asset tracking—all without the flicker of traditional CLI loops.

> **Tip:** Press `CTRL + P` (or use the built-in Textual screenshot hotkey) to export your current dashboard view directly to an SVG file.

## 🚀 Features

* **Modular Grid Interface:** A responsive TUI (Text User Interface) that scales perfectly to your terminal window.
* **Core Systems & Hardware Sensors:** Real-time tracking of CPU usage, RAM allocation, Local Disk Space, and GPU Load/Temperatures (Nvidia).
* **Permissionless Ping:** Calculates network latency to `8.8.8.8` (or your chosen target) using TCP Port 53, bypassing the need for raw ICMP admin/root privileges.
* **Atmospheric Sensors:** Automatically detects your IP and fetches localized terminal weather via `wttr.in`.
* **Live Asset Uplink:** Background fetching of live cryptocurrency prices (BTC, ETH, SHIB) with clean decimal formatting.
* **JSON Configuration:** Easily customize targets, assets, and refresh rates without touching the core Python code.

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/cyberdeck.git](https://github.com/yourusername/cyberdeck.git)
   cd cyberdeck