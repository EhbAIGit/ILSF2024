from spherov2 import scanner

# Create a function to scan for available Sphero toys
def find_available_toys():
    while True:
        try:
            toy = scanner.find_toy()
            if toy:
                yield toy
        except KeyboardInterrupt:
            break

# List available Sphero toys
print("Scanning for available Sphero toys...")
for found_toy in find_available_toys():
    print(f"Found Sphero Toy: {found_toy.name} (MAC Address: {found_toy.get_mac_address})")
