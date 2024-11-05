import csv
import random
import sys

# Custom exceptions
class InvalidDirectionException(Exception):
    pass

class InvalidInputFileFormat(Exception):
    pass

class Creature:
    def __init__(self, name, description, adoptable=False):
        self.name = name
        self.description = description
        self.adoptable = adoptable

class Item:
    def __init__(self, name, description, pickable, consumable):
        self.name = name
        self.description = description
        self.pickable = pickable == 'yes'
        self.consumable = consumable == 'yes'

class Location:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.doors = {"west": None, "north": None, "east": None, "south": None}
        self.creatures = []
        self.items = []

    def connect(self, direction, location):
        if direction in self.doors:
            self.doors[direction] = location
            opposite_directions = {
                "west": "east",
                "north": "south",
                "east": "west",
                "south": "north"
            }
            getattr(location, 'doors')[opposite_directions[direction]] = self

class Record:
    def __init__(self):
        self.creatures = []
        self.items = []
        self.locations = []

    def load_creatures(self, filename):
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['name'].strip()
                description = row['description'].strip()
                adoptable = row['adoptable'].strip().lower() == 'yes'
                print(f"Loading Creature - Name: {name}, Description: {description}, Adoptable: {adoptable}")

                creature = Pymon(name, description) if adoptable else Creature(name, description, adoptable)
                self.creatures.append(creature)

    def load_items(self, filename):
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                trimmed_row = {key.strip(): value.strip() for key, value in row.items()}
                item = Item(trimmed_row['name'], trimmed_row['description'], trimmed_row['pickable'], trimmed_row['consumable'])
                self.items.append(item)

    def load_locations(self, filename):
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                location = Location(row['name'].strip(), row['description'].strip())
                self.locations.append(location)

                # Connect locations based on direction
                for direction in ['west', 'north', 'east', 'south']:
                    if row[direction] and row[direction].strip() != 'None':
                        connected_location = next((loc for loc in self.locations if loc.name == row[direction].strip()), None)
                        if connected_location:
                            location.connect(direction, connected_location)

                # Assign items to the location based on a predefined mapping
                if location.name == "Playground":
                    item = next((item for item in self.items if item.name == "potion"), None)
                    if item:
                        location.items.append(item)
                elif location.name == "Beach":
                    item = next((item for item in self.items if item.name == "apple"), None)
                    if item:
                        location.items.append(item)
                elif location.name == "School":
                    item = next((item for item in self.items if item.name == "binocular"), None)
                    if item:
                        location.items.append(item)
                # Add additional conditions for other locations as needed


class Pymon(Creature):
    def __init__(self, name, description):
        super().__init__(name, description, adoptable=True)  # Automatically adoptable
        self.energy = 3
        self.inventory = []
        self.current_location = None

    def pick_item(self, item):
        if self.current_location and item.pickable:
            print(f"{self.name} picked up {item.name}.")
            self.inventory.append(item)
            if item in self.current_location.items:
                self.current_location.items.remove(item)
        else:
            print(f"{item.name} cannot be picked up.")

    def use_item(self, item_name):
        item = next((i for i in self.inventory if i.name == item_name), None)
        if item:
            if item.consumable:
                if item.name == 'apple':
                    if self.energy < 3:
                        self.energy += 1
                        print(f"{self.name} ate an {item.name} and now has {self.energy} energy.")
                        self.inventory.remove(item)
                    else:
                        print(f"{self.name} already has full energy.")
                elif item.name == 'potion':
                    print(f"{self.name} used a {item.name}.")
                    self.inventory.remove(item)
                else:
                    print(f"{item.name} can't be used.")
            else:
                print(f"{item.name} is not consumable.")
        else:
            print(f"{item_name} not found in inventory.")

class Game:
    def __init__(self, record):
        self.record = record
        self.current_pymon = None
        self.current_location = None

    def start_game(self):
        # Check for available adoptable Pymons
        adoptable_pymons = [p for p in self.record.creatures if isinstance(p, Pymon) and p.adoptable]
        if not adoptable_pymons:
            print("No adoptable Pymons available. Exiting game.")
            return

        # Select a random starting location and Pymon
        self.current_pymon = random.choice(adoptable_pymons)
        self.current_location = random.choice(self.record.locations)
        self.current_pymon.current_location = self.current_location  # Ensure Pymon location is set

        print(f"You are in {self.current_location.name}. {self.current_location.description}")
        print(f"Your current Pymon is {self.current_pymon.name}. Energy: {self.current_pymon.energy}")

        while True:
            self.show_menu()
            choice = input("Choose an action: ")

            if choice == '1':
                self.inspect_pymon()
            elif choice == '2':
                self.inspect_location()
            elif choice == '3':
                self.move()
            elif choice == '4':
                self.pick_item()
            elif choice == '5':
                self.view_inventory()
            elif choice == '6':
                print("Challenge feature is not implemented yet.")
            elif choice == '7':
                print("Stats feature is not implemented yet.")
            elif choice == '8':
                print("Exiting game.")
                break
            else:
                print("Invalid choice. Please try again.")

    def show_menu(self):
        print("\nMenu:")
        print("1. Inspect Pymon")
        print("2. Inspect current location")
        print("3. Move")
        print("4. Pick an item")
        print("5. View inventory")
        print("6. Challenge a creature")
        print("7. Generate stats")
        print("8. Exit the program")

    def inspect_pymon(self):
        print(f"Pymon Name: {self.current_pymon.name}, Description: {self.current_pymon.description}, Energy: {self.current_pymon.energy}")

    def inspect_location(self):
        print(f"Location Name: {self.current_location.name}, Description: {self.current_location.description}")

    def move(self):
        direction = input("Enter direction to move (west/north/east/south): ")
        if direction in self.current_location.doors:
            next_location = self.current_location.doors[direction]
            if next_location:
                self.current_location = next_location
                self.current_pymon.current_location = next_location  # Update Pymon's location
                print(f"You moved to {self.current_location.name}.")
            else:
                print(f"There is no location to the {direction}.")
        else:
            print(f"Invalid direction: {direction}.")

    def pick_item(self):
        if self.current_location.items:
            print("Items available to pick:")
            for idx, item in enumerate(self.current_location.items):
                print(f"{idx + 1}. {item.name} - {item.description}")
            item_choice = int(input("Select an item to pick: ")) - 1
            if 0 <= item_choice < len(self.current_location.items):
                self.current_pymon.pick_item(self.current_location.items[item_choice])
            else:
                print("Invalid choice.")
        else:
            print("No items available in this location.")

    def view_inventory(self):
        print("Inventory:")
        if not self.current_pymon.inventory:
            print("Your inventory is empty.")
        for item in self.current_pymon.inventory:
            print(f"- {item.name}: {item.description}")

if __name__ == "__main__":
    record = Record()
    record.load_creatures('creatures.csv')  # Loading creatures
    record.load_items('items.csv')          # Loading items
    record.load_locations('locations.csv')  # Loading locations

    game = Game(record)
    game.start_game()  # Start the game after loading everything
