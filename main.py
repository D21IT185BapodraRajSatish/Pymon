import random
import csv

def generate_random_number(max_number=1):
    return random.randint(0, max_number)

import random

class Pymon:
    def __init__(self, name, description, energy):
        self.name = name
        self.description = description
        self.energy = energy
        self.inventory = []

    def pick_item(self, item):
        if item.pickable and len(self.inventory) < 10:  # Limit inventory size
            self.inventory.append(item)
            print(f"{self.name} picked up {item.name}.")
            return True
        else:
            print(f"{item.name} cannot be picked up.")
            return False

    def view_inventory(self):
        if not self.inventory:
            print("Inventory is empty.")
        else:
            print("Items in inventory:")
            for item in self.inventory:
                print(f"- {item.name}: {item.description}")

    def challenge(self, opponent):
        if opponent:  # Check if an opponent exists
            print(f"{self.name} challenges {opponent.name} to a battle!")
            return self.battle(opponent)
        else:
            print("No opponent to challenge.")

    def battle(self, opponent):
        my_wins = 0
        opponent_wins = 0

        for _ in range(3):  # Maximum of 3 encounters
            if self.energy <= 0:
                print(f"{self.name} has no energy left to battle.")
                break
            
            player_choice = input("Choose your shape (rock, paper, scissors): ").lower()
            opponent_choice = random.choice(['rock', 'paper', 'scissors'])
            print(f"{opponent.name} chose {opponent_choice}.")

            if player_choice == opponent_choice:
                print("Draw, no one wins.")
            elif (player_choice == 'rock' and opponent_choice == 'scissors') or \
                 (player_choice == 'paper' and opponent_choice == 'rock') or \
                 (player_choice == 'scissors' and opponent_choice == 'paper'):
                print(f"{self.name} wins this encounter!")
                my_wins += 1
            else:
                print(f"{opponent.name} wins this encounter!")
                opponent_wins += 1
                self.energy -= 1  # Decrease energy on loss

            if my_wins == 2:
                print(f"{self.name} wins the battle!")
                return True
            elif opponent_wins == 2:
                print(f"{opponent.name} wins the battle! {self.name} is moved to the wild.")
                return False
        
        print("Battle ended without a clear winner.")
        return None

    def __init__(self, name="Kimimon", color="white and yellow", face="square", energy=3, adoptable=True):
        self.name = name
        self.color = color
        self.face = face
        self.energy = energy
        self.adoptable = adoptable
        self.current_location = None

    def move(self, direction=None):
        if self.current_location and direction in self.current_location.doors:
            next_location = self.current_location.doors[direction]
            if next_location:
                next_location.add_creature(self)
                self.current_location.creatures.remove(self)
                self.current_location = next_location
                print(f"You traveled {direction} and arrived at {self.current_location.get_name()}.")
            else:
                print(f"There is no door to the {direction}. Pymon remains at its current location.")
        else:
            print("Invalid direction.")

    def spawn(self, location):
        if location:
            location.add_creature(self)
            self.current_location = location

    def get_location(self):
        return self.current_location

class Item:
    def __init__(self, name, description, pickable, consumable):
        self.name = name
        self.description = description
        self.pickable = pickable
        self.consumable = consumable

class Location:
    def __init__(self, name="New room", description="A mysterious place"):
        self.name = name
        self.description = description
        self.doors = {"west": None, "north": None, "east": None, "south": None}
        self.creatures = []
        self.items = []

    def add_creature(self, creature):
        self.creatures.append(creature)

    def add_item(self, item):
        self.items.append(item)

    def connect(self, direction, other_location):
        if direction in self.doors:
            self.doors[direction] = other_location
            opposite_directions = {"west": "east", "east": "west", "north": "south", "south": "north"}
            opposite_direction = opposite_directions[direction]
            if opposite_direction in other_location.doors:
                other_location.doors[opposite_direction] = self
    def get_item(self, item_name):
        for item in self.items:
            if item.name.lower() == item_name.lower():
                return item
    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

class Record:
    def __init__(self):
        self.locations = []
        self.creatures = []
        self.items = []

    def import_locations(self, filename="locations.csv"):
        location_dict = {}
        # First pass: Create Location objects
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['name']
                description = row['description']
                location = Location(name, description)
                self.locations.append(location)
                location_dict[name] = location

        # Second pass: Connect locations based on CSV data
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                location = location_dict[row['name']]
                for direction in ["west", "north", "east", "south"]:
                    neighbor_name = row[direction]
                    if neighbor_name and neighbor_name != "None" and neighbor_name in location_dict:
                        location.connect(direction, location_dict[neighbor_name])

    def import_items(self, filename="items.csv"):
        try:
            with open(filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if 'name' in row and 'description' in row and 'pickable' in row and 'consumable' in row:
                        name = row['name']
                        description = row['description']
                        pickable = row['pickable'].strip().lower() == 'yes'
                        consumable = row['consumable'].strip().lower() == 'yes'
                        item = {"name": name, "description": description, "pickable": pickable, "consumable": consumable}
                        self.items.append(item)
                    else:
                        print("Warning: One or more headers are missing in the items CSV.")
        except FileNotFoundError:
            print(f"Error: The file '{filename}' was not found.")
        except KeyError as e:
            print(f"Error: Missing expected column {e} in the items CSV.")

    def import_creatures(self, filename="creatures.csv"):
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['name']
                description = row['description']
                adoptable = row['adoptable'].lower() == 'yes'
                creature = Pymon(name=name, color="varied", face="varied", energy=3, adoptable=adoptable)
                self.creatures.append(creature)

    def get_locations(self):
        return self.locations

    def get_items(self):
        return self.items

    def get_creatures(self):
        return self.creatures

class Operation:
    def __init__(self):
        self.locations = []
        self.current_pymon = Pymon("Kimimon", color="white and yellow", face="square", energy=3)
        self.is_running = True

    def setup(self):
        record = Record()
        record.import_locations()
        record.import_items()
        record.import_creatures()

        self.locations = record.get_locations()
        # Spawn the main Pymon at a random location
        random_location = random.choice(self.locations)
        self.current_pymon.spawn(random_location)
        print(f"Spawned {self.current_pymon.name} at {random_location.get_name()}.")

    def display_menu(self):
        print("\nPlease issue a command to your Pymon:")
        print("1) Inspect Pymon")
        print("2) Inspect current location")
        print("3) Move")
        print("4) Exit the program")

    def inspect_pymon(self):
        print(f"\nHi Player, my name is {self.current_pymon.name}.")
        print(f"I am {self.current_pymon.color} with a {self.current_pymon.face} face.")
        print(f"My energy level is {self.current_pymon.energy}/3. What can I do to help you?")

    def inspect_location(self):
        location = self.current_pymon.get_location()
        if location:
            print(f"\nYou are at {location.get_name()}, {location.get_description()}")
            if location.creatures:
                print("Creatures here:")
                for creature in location.creatures:
                    print(f"- {creature.name}")
            else:
                print("No creatures here.")
            if location.items:
                print("Items here:")
                for item in location.items:
                    print(f"- {item['name']}: {item['description']}")
            else:
                print("No items here.")
        else:
            print("Pymon is not in any location.")

    def handle_move(self):
        direction = input("Moving to which direction?: ").strip().lower()
        self.current_pymon.move(direction)

    def start_game(self):
        print("Welcome to Pymon World!")
        print("It's just you and your loyal Pymon roaming around to find more Pymons to capture and adopt.")
        print(f"You started at {self.current_pymon.get_location().get_name()}\n")
        while self.is_running:
            self.display_menu()
            choice = input("Your command: ").strip()
            if choice == '1':
                self.inspect_pymon()
            elif choice == '2':
                self.inspect_location()
            elif choice == '3':
                self.handle_move()
            elif choice == '4':
                print("Exiting the game.")
                self.is_running = False
            else:
                print("Invalid choice. Please try again.")

if __name__ == '__main__':
    ops = Operation()
    ops.setup()
    ops.start_game()
