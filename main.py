import csv
import random
import sys
from datetime import datetime

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
            location.doors[opposite_directions[direction]] = self

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
                creature = Pymon(name, description) if adoptable else Creature(name, description, adoptable)
                self.creatures.append(creature)

    def load_items(self, filename):
        try:
            with open(filename, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Strip spaces from all keys to handle any extra spaces in the header
                    row = {key.strip(): value.strip() for key, value in row.items()}
                    item = Item(row['name'], row['description'], row['pickable'], row['consumable'])
                    self.items.append(item)
        except KeyError as e:
            print(f"Error: Missing expected column {e} in {filename}")


    def load_locations(self, filename):
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                location = Location(row['name'].strip(), row['description'].strip())
                self.locations.append(location)

                # Connect locations based on directions in the CSV file
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
        super().__init__(name, description, adoptable=True)
        self.energy = 3
        self.inventory = []
        self.battle_stats = []
        self.current_location = None

    def pick_item(self, item):
        if item.pickable:
            print(f"{self.name} picked up {item.name}.")
            self.inventory.append(item)
        else:
            print(f"{item.name} cannot be picked up.")

    def challenge(self, opponent):
        if not isinstance(opponent, Pymon):
            print(f"{opponent.name} is not a Pymon and cannot be challenged.")
            return
        
        print(f"{self.name} challenges {opponent.name} to a battle!")
        my_wins, opponent_wins = 0, 0

        for encounter in range(min(3, self.energy)):
            player_choice = input("Choose your move (rock, paper, scissors): ").strip().lower()
            opponent_choice = random.choice(['rock', 'paper', 'scissors'])
            print(f"{opponent.name} chose {opponent_choice}")

            if player_choice == opponent_choice:
                print("Draw - no one wins.")
            elif (player_choice == 'rock' and opponent_choice == 'scissors') or \
                 (player_choice == 'scissors' and opponent_choice == 'paper') or \
                 (player_choice == 'paper' and opponent_choice == 'rock'):
                print(f"{self.name} wins this encounter!")
                my_wins += 1
            else:
                print(f"{opponent.name} wins this encounter.")
                opponent_wins += 1
                self.energy -= 1  # Deduct energy when losing an encounter

            if my_wins == 2:
                print(f"{self.name} wins the battle and captures {opponent.name}!")
                return "win"
            elif opponent_wins == 2:
                print(f"{opponent.name} wins the battle. {self.name} is moved to the wild.")
                return "lose"

        print("The battle ended without a clear winner.")
        return "draw"

    def record_battle(self, opponent, wins, draws, losses):
        timestamp = datetime.now().strftime("%d/%m/%Y %I:%M %p")
        self.battle_stats.append({
            "timestamp": timestamp,
            "opponent": opponent.name,
            "wins": wins,
            "draws": draws,
            "losses": losses
        })

    def show_battle_stats(self):
        total_wins = total_draws = total_losses = 0
        print(f"\nBattle Stats for {self.name}:")
        for stat in self.battle_stats:
            print(f"Date: {stat['timestamp']} | Opponent: {stat['opponent']} | Wins: {stat['wins']} | Draws: {stat['draws']} | Losses: {stat['losses']}")
            total_wins += stat['wins']
            total_draws += stat['draws']
            total_losses += stat['losses']
        print(f"\nTotal Stats - Wins: {total_wins}, Draws: {total_draws}, Losses: {total_losses}")

class Game:
    def __init__(self, record):
        self.record = record
        self.current_pymon = None
        self.current_location = None
        self.pymon_bench = []

    def start_game(self):
        # Set random starting location and Pymon
        self.current_pymon = random.choice([creature for creature in self.record.creatures if isinstance(creature, Pymon)])
        self.current_location = random.choice(self.record.locations)
        self.current_pymon.current_location = self.current_location
        print(f"Starting at {self.current_location.name}. Pymon: {self.current_pymon.name}")

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
                self.challenge_creature()
            elif choice == '7':
                self.current_pymon.show_battle_stats()
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
        print("7. Show battle stats")
        print("8. Exit the program")

    def inspect_pymon(self):
        print(f"Pymon Name: {self.current_pymon.name}, Energy: {self.current_pymon.energy}")
        if self.pymon_bench:
            print("Available benched Pymons:")
            for idx, pymon in enumerate(self.pymon_bench, 1):
                print(f"{idx}. {pymon.name} (Energy: {pymon.energy})")
            choice = input("Enter the number to swap with current Pymon, or press Enter to skip: ")
            if choice.isdigit() and 1 <= int(choice) <= len(self.pymon_bench):
                new_pymon = self.pymon_bench.pop(int(choice) - 1)
                self.pymon_bench.append(self.current_pymon)
                self.current_pymon = new_pymon
                print(f"Swapped to {self.current_pymon.name}")

    def inspect_location(self):
        print(f"Location Name: {self.current_location.name}, Description: {self.current_location.description}")

    def move(self):
        direction = input("Enter direction to move (west/north/east/south): ")
        next_location = self.current_location.doors.get(direction)
        if next_location:
            self.current_location = next_location
            self.current_pymon.current_location = next_location
            print(f"You moved to {self.current_location.name}.")
        else:
            print(f"There is no location to the {direction}.")

    def pick_item(self):
        if self.current_location.items:
            item = self.current_location.items.pop(0)
            self.current_pymon.pick_item(item)
        else:
            print("No items available in this location.")

    def view_inventory(self):
        if not self.current_pymon.inventory:
            print("Your inventory is empty.")
        else:
            for item in self.current_pymon.inventory:
                print(f"- {item.name}: {item.description}")

    def challenge_creature(self):
        opponents = [c for c in self.current_location.creatures if isinstance(c, Pymon) and c != self.current_pymon]
        if not opponents:
            print("No other Pymons to challenge in this location.")
            return
        
        opponent = opponents[0]  # Select the first Pymon found as the opponent
        result = self.current_pymon.challenge(opponent)

        if result == "win":
            self.pymon_bench.append(opponent)
            self.current_location.creatures.remove(opponent)
        elif result == "lose":
            new_location = random.choice(self.record.locations)
            self.current_pymon.current_location = new_location
            self.current_location = new_location
            if self.pymon_bench:
                self.current_pymon = self.pymon_bench.pop(0)
                print(f"{self.current_pymon.name} is now your active Pymon.")
            else:
                print("No other Pymons in your pet list. Game over.")
                exit()

if __name__ == "__main__":
    record = Record()
    creatures_file = sys.argv[2] if len(sys.argv) > 2 else "creatures.csv"
    items_file = sys.argv[3] if len(sys.argv) > 3 else "items.csv"
    locations_file = sys.argv[1] if len(sys.argv) > 1 else "locations.csv"

    record.load_creatures(creatures_file)
    record.load_items(items_file)
    record.load_locations(locations_file)

    game = Game(record)
    game.start_game()
