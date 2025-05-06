import argparse
import logging
import requests
import socket
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MAC address vendor lookup API URL (using macvendors.co as an example)
MAC_VENDOR_API_URL = "https://macvendors.co/api/{mac_address}"


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description="Lookup vendor information for a given MAC address.")
    parser.add_argument("mac_address", help="The MAC address to lookup (e.g., 00:1A:2B:3C:4D:5E).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (DEBUG level).")
    return parser


def is_valid_mac_address(mac_address):
    """
    Validates if the provided string is a valid MAC address.

    Args:
        mac_address (str): The MAC address string to validate.

    Returns:
        bool: True if the MAC address is valid, False otherwise.
    """
    try:
        # Ensure the MAC address is in a valid format
        socket.inet_aton(':'.join(['0'] * 6))  # Dummy check for valid structure.  Doesn't validate the real address.
        if len(mac_address.split(':')) != 6:  # Requires six octets.
            return False

        for octet in mac_address.split(':'):
            if len(octet) != 2: #Requires 2 characters for each octet
                return False
            if not all(c in '0123456789abcdefABCDEF' for c in octet): # Requires hex characters
                return False
        return True

    except socket.error:
        return False


def lookup_mac_vendor(mac_address):
    """
    Looks up the vendor information for a given MAC address using a public API.

    Args:
        mac_address (str): The MAC address to lookup.

    Returns:
        str: The vendor information, or None if an error occurs.
    """
    try:
        url = MAC_VENDOR_API_URL.format(mac_address=mac_address)
        logging.debug(f"Sending request to {url}")  # Debug log

        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        if data and 'result' in data and 'company' in data['result']:
            return data['result']['company']
        else:
            logging.warning(f"Vendor information not found for MAC address: {mac_address}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred during the request: {e}")
        return None
    except ValueError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None


def main():
    """
    The main function that orchestrates the MAC address lookup process.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose logging enabled.")  # Debug log

    mac_address = args.mac_address.strip()

    if not is_valid_mac_address(mac_address):
        logging.error("Invalid MAC address format. Please use the format XX:XX:XX:XX:XX:XX.")
        sys.exit(1)

    logging.info(f"Looking up vendor for MAC address: {mac_address}")

    vendor_info = lookup_mac_vendor(mac_address)

    if vendor_info:
        print(f"Vendor: {vendor_info}")
    else:
        print("Vendor information not found.")


if __name__ == "__main__":
    # Example usage:
    # python main.py 00:1A:2B:3C:4D:5E
    # python main.py 00:1A:2B:3C:4D:5E -v  # Enable verbose logging
    main()