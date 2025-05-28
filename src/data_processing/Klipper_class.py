from requests import get, post
from utils.extract_gcode_from_string import extract_relevant_slicing_parameters_from_string


class KlipperPrinter(object):
    """Moonraker API interface.
    Args
    ----
    address (str): e.g. 'http://192.168.1.17/'
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

    def get_filename(self) -> str:
        printer_gcode_filename = self.get("/printer/objects/query?print_stats")[
            "result"
        ]["status"]["print_stats"]["filename"]

        return printer_gcode_filename

    def get_gcode(self):

        printer_gcode_filename = self.get_filename()
        gcode_download_url = f"/server/files/gcodes/{printer_gcode_filename}"
        gcode_response = self.get_download(gcode_download_url)
        gcode_content = gcode_response.text
        return gcode_content

    def extract_gcode_params(self) -> dict:
        gcode_content = self.get_gcode()
        # Extract relevant parameters from the G-code content
        params = extract_relevant_slicing_parameters_from_string(gcode_content)
        return params
    def get_part_name(self) -> str:

        return self.get_filename().split("_0")[0]

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

    def get_current_layer(self) -> int:
        """
        Get the current layer number of the print job.

        Returns
        -------
        int
            The current layer number.
        """
        return self.get("/printer/objects/query?print_stats")["result"]["status"]["print_stats"]["info"]["current_layer"]
        
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

    def get_download(self, url: str):
        """Download the content from a G-code file from the printer's server. without cenversion to json"""
        return get(self.addr + url, timeout=2)
