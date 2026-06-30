import json
import psutil
import requests
import time
import socket
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Header, Footer, Static

try:
    import GPUtil
    HAS_GPU = True
except ImportError:
    HAS_GPU = False

# Load Configuration
try:
    with open("config.json", "r") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    # Fallback if config is missing
    CONFIG = {
        "node_name": "CYBER-01",
        "crypto_assets": "bitcoin,ethereum,shiba-inu",
        "ping_target": "8.8.8.8",
        "refresh_rate_sys": 1.0,
        "refresh_rate_net": 15.0
    }

# ----------------------------------------------------------------------
# WIDGET MODULES
# ----------------------------------------------------------------------

class SystemStats(Static):
    """Monitors CPU and RAM"""
    def on_mount(self) -> None:
        self.set_interval(CONFIG["refresh_rate_sys"], self.update_stats)

    def update_stats(self) -> None:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        
        content = f"[b]>> CORE SYSTEMS[/b]\n\n"
        content += f"CPU: [{'#' * int(cpu // 5):<20}] {cpu}%\n"
        content += f"RAM: [{'#' * int(ram.percent // 5):<20}] {ram.percent}%\n"
        content += f"USE: {ram.used // (1024 ** 3)} GB / {ram.total // (1024 ** 3)} GB"
        
        self.update(content)

class DriveStats(Static):
    """Monitors Local Disk Space"""
    def on_mount(self) -> None:
        self.update_drives()
        self.set_interval(10.0, self.update_drives) # Checks every 10 secs

    def update_drives(self) -> None:
        content = "[b]>> LOCAL DATA DRIVES[/b]\n\n"
        partitions = psutil.disk_partitions(all=False)
        
        for p in partitions:
            if 'fixed' in p.opts or 'rw' in p.opts:
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    content += f"{p.device} [{'#' * int(usage.percent // 5):<20}] {usage.percent}%\n"
                except PermissionError:
                    continue
        self.update(content)

class HardwareSensors(Static):
    """Monitors Temps and GPU Load"""
    def on_mount(self) -> None:
        self.set_interval(CONFIG.get("refresh_rate_sys", 1.0), self.update_sensors)

    def update_sensors(self) -> None:
        content = "[b]>> HARDWARE SENSORS[/b]\n\n"
        
        # CPU Temps (psutil only supports this natively on Linux/macOS)
        if hasattr(psutil, "sensors_temperatures"):
            try:
                temps = psutil.sensors_temperatures()
                if temps and 'coretemp' in temps:
                    cpu_temp = temps['coretemp'][0].current
                    content += f"CPU TEMP: {cpu_temp}°C\n"
                else:
                    content += "CPU TEMP: SENSOR LOCKED\n"
            except Exception:
                content += "CPU TEMP: SENSOR LOCKED\n"
        else:
            content += "CPU TEMP: OS UNSUPPORTED (WINDOWS)\n"
            
        # GPU Stats (GPUtil usually works fine on Windows if Nvidia drivers are present)
        if HAS_GPU:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    content += f"GPU NAME: {gpu.name}\n"
                    content += f"GPU LOAD: {gpu.load * 100:.1f}%\n"
                    content += f"GPU TEMP: {gpu.temperature}°C\n"
                    content += f"GPU VRAM: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB"
                else:
                    content += "GPU: NOT DETECTED"
            except Exception:
                content += "GPU: SENSOR READ ERROR"
        else:
            content += "GPU: 'gputil' NOT INSTALLED"

        self.update(content)

class WeatherModule(Static):
    """Fetches local terminal weather automatically via IP"""
    def on_mount(self) -> None:
        self.update_weather()
        self.set_interval(600, self.update_weather) # Update every 10 mins

    def update_weather(self) -> None:
        try:
            # Hitting the root URL without a location forces IP auto-detection
            res = requests.get("https://wttr.in/?format=3", timeout=3).text.strip()
            self.update(f"[b]>> ATMOSPHERIC SENSORS[/b]\n\nSTATUS: {res}")
        except Exception:
            self.update(f"[b]>> ATMOSPHERIC SENSORS[/b]\n\nSTATUS: [red]OFFLINE[/red]")

class CryptoTicker(Static):
    """Live asset uplink with fixed decimal formatting"""
    def on_mount(self) -> None:
        self.update_crypto()
        self.set_interval(300, self.update_crypto)

    def update_crypto(self) -> None:
        assets = CONFIG["crypto_assets"]
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={assets}&vs_currencies=usd"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=5).json()
            
            output = "[b]>> ASSET UPLINK[/b]\n\n"
            for asset, data in resp.items():
                # Formats to 8 decimal places to avoid scientific notation
                price = f"${data['usd']:.8f}".rstrip('0').rstrip('.') 
                output += f"{asset.upper()}: {price}\n"
            self.update(output)
        except Exception:
            self.update("[b]>> ASSET UPLINK[/b]\n\n[red]FEED DISCONNECTED[/red]")

class NetworkPing(Static):
    """Permissionless cross-platform latency check using TCP Port 53"""
    def on_mount(self) -> None:
        self.update_ping()
        self.set_interval(CONFIG["refresh_rate_net"], self.update_ping)

    def update_ping(self) -> None:
        target = CONFIG["ping_target"]
        try:
            start = time.time()
            # Connect to DNS port (53) to test latency without needing raw ICMP permissions
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((target, 53))
            s.close()
            latency = int((time.time() - start) * 1000)
            
            color = "green" if latency < 100 else "yellow"
            self.update(f"[b]>> SATELLITE UPLINK[/b]\n\nTARGET: {target}\nLATENCY: [{color}]{latency} ms[/{color}]")
        except Exception:
            self.update(f"[b]>> SATELLITE UPLINK[/b]\n\nTARGET: {target}\nLATENCY: [red]TIMEOUT/OFFLINE[/red]")


# ----------------------------------------------------------------------
# MAIN APPLICATION
# ----------------------------------------------------------------------

class CyberdeckApp(App):
    """The main TUI Application"""
    
    # Textual CSS for 2x3 grid layout
    CSS = """
    Grid {
        grid-size: 2 3;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr 1fr 1fr;
        padding: 1;
    }
    Static {
        border: solid green;
        padding: 1;
        background: $boost;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        yield Grid(
            SystemStats(),
            HardwareSensors(),
            DriveStats(),
            NetworkPing(),
            WeatherModule(),
            CryptoTicker()
        )
        
        yield Footer()

if __name__ == "__main__":
    app = CyberdeckApp()
    app.title = f"CYBERDECK // NODE: {CONFIG.get('node_name', 'UNKNOWN')}"
    app.run()