import socket
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

def find_ip_and_mac():
    """Find the IP and MAC address of the device using UDP broadcast."""
    sender = None
    listener = None
    try:
        # Determine the local IP address
        local_ip = socket.gethostbyname(socket.gethostname())
        logger.debug("Local IP: %s", local_ip)

        # Broadcast IP = .255 of current subnet
        ip_parts = local_ip.split('.')
        ip_parts[-1] = '255'
        broadcast_ip = '.'.join(ip_parts)
        logger.debug("Broadcast IP: %s", broadcast_ip)

        # Set up the listener socket
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.settimeout(5)
        listener.bind((local_ip, 3001))

        # Send the broadcast message
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sender.sendto(b'identify', (broadcast_ip, 3000))
        logger.debug("UDP discovery broadcast sent")

        # Wait up to 5 seconds for a response
        data, addr = listener.recvfrom(1024)
        if data:
            root = ET.fromstring(data.decode())
            mac = root.find('.//mac')
            ip = root.find('.//ip')
            if mac is not None and ip is not None:
                logger.info("MyAir3 discovered: IP=%s MAC=%s", ip.text, mac.text)
                return ip.text, mac.text
            logger.debug("UDP response received but IP/MAC not found in payload")
        return None, None

    except socket.timeout:
        # No device responded to the broadcast — normal when discovery isn't supported
        logger.debug("UDP discovery timed out — no device found, will fall back to manual IP")
        return None, None
    except Exception as e:
        logger.warning("UDP discovery failed: %s", e)
        return None, None

    finally:
        for sock in (sender, listener):
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass
            

if __name__ == "__main__":
    find_ip_and_mac()
