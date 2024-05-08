import socket
import time
import xml.etree.ElementTree as ET
import logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

def find_ip_and_mac():
    try:
        # Determine the local IP address
        local_ip = socket.gethostbyname(socket.gethostname())
        logger.info(f"Local IP: {local_ip}")

        # Broadcast ip = .255 of current subnet
        ip_parts = local_ip.split('.')
        ip_parts[-1] = '255'
        broadcast = '.'.join(ip_parts)
        logger.info(f"Broadcast IP: {broadcast}")

        # Set up the listener socket
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.bind((local_ip, 3001))

        # Send the broadcast message
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sender.sendto(b'identify', (broadcast, 3000))
        logger.info("Broadcast message sent.")

        # Give it some time to respond
        time.sleep(2)  # Adjust timing as necessary

        # Try to receive the response
        data, addr = listener.recvfrom(1024)
        if data:
            logger.info("Received data.")
            root = ET.fromstring(data.decode())

            # Try to extract MAC and IP address
            mac = root.find('.//mac')
            ip = root.find('.//ip')

            if mac is not None and ip is not None:
                logger.info(f"IP address: {ip.text}    Mac address: {mac.text}")
                return ip.text, mac.text
            else:
                logger.error("Error: Required elements not found in the response.")
                return None, None
        else:
            logger.error("No data received.")
            return None, None

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None, None

    finally:
        # Cleanup sockets
        if 'sender' in locals():
            sender.close()
        if 'listener' in locals():
            listener.close()

if __name__ == "__main__":
    find_ip_and_mac()
