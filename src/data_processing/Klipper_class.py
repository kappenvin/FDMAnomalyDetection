from requests import get, post


class KlipperPrinter(object):
    """Moonraker API interface.
    Args
    ----
    address (str): e.g. 'http://192.168.1.17'
    """

    def __init__(self, address: str) -> None:
        # used to strip trailing slashes that comes from copying the url from the browser
        self.addr = address.strip("/")

        configfile = self.get("/printer/objects/query?configfile")
        self.settings = configfile["result"]["status"]["configfile"]["settings"]
        self.config = configfile["result"]["status"]["configfile"]["config"]

        """
        self.cmd_qgl = "QUAD_GANTRY_LEVEL"
        self.cmd_bed_mesh = "BED_MESH_CALIBRATE"
        self.temp_sensors = self.list_temp_sensors()
        """

    def check_connection(self) -> bool:
        try:
            self.get("/printer/objects/query?configfile")
            return True
        except Exception as e:
            print(f"Error checking connection: {e}")
            return False

    def send_gcode(self, cmd: str) -> bool:
        resp = self.post("/printer/gcode/script?script=%s" % cmd)
        if "result" in resp:
            return True
        return False

    def get_gcode(self):
        pass

    def query_status(self):
        """
        Query the current status of the printer.

        Returns
        -------
        str
            The current state of the printer (e.g., 'ready', 'printing', 'error').
        """
        query = "/printer/objects/query?print_stats"
        return self.get(query)["result"]["status"]["print_stats"]["state"]

    def set_bed_temp(self, target: float = 0.0):
        pass

    def set_extruder_temp(self, target: float = 0.0):
        pass

    def get(self, url: str):
        """`response.get` wrapper. `url` concatenated to printer base address
        Returns .json response dict."""
        return get(self.addr + url, timeout=2).json()

    def post(self, url: str, *args, **kwargs):
        """`response.set` wrapper. `url` is concatenated to printer base address.
        Returns .json response dict."""
        return post(self.addr + url, *args, **kwargs).json()
