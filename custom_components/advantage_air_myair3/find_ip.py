"""Helpers for validating a MyAir3 device by IP."""
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


def find_ip_and_mac(ip_address: str, password: str = "password", timeout: int = 5):
    """Validate the supplied IP address and return its IP and MAC if authenticated."""
    try:
        query = urllib.parse.urlencode({"password": password})
        url = f"http://{ip_address}/login?{query}"

        with urllib.request.urlopen(url, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="ignore")

        root = ET.fromstring(text)

        authenticated = root.findtext("authenticated")
        mac = root.findtext("mac")

        if authenticated == "1" and mac:
            return ip_address, mac

        return None, None

    except Exception:
        return None, None