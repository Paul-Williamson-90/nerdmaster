import os
import json

def recursive_remove(directory):
    for item in os.listdir(directory):
        if os.path.isdir(f"{directory}/{item}"):
            recursive_remove(f"{directory}/{item}")
            os.rmdir(f"{directory}/{item}")
        else:
            os.remove(f"{directory}/{item}")

def clear_test(character:str="Paul Williamson"):
    # delete directory "./saves"
    os.system("rm -rf C:/Users/paulw/Documents/nerdmaster/saves")

    with open("./data/game/game.json", "r") as f:
        game = json.load(f)

    # remove "Paul Williamson" from keys
    if character in game.keys():
        game.pop(character)

        # save game.json
        with open("./data/game/game.json", "w") as f:
            json.dump(game, f, indent=4)

    # remove "Paul Williamson" from "players"
    with open("./data/player/player.json", "r") as f:
        players = json.load(f)

    if character in players.keys():
        players.pop(character)

        # save players.json
        with open("./data/player/player.json", "w") as f:
            json.dump(players, f, indent=4)

    files = os.listdir("./data/audio")
    for file in files:
        os.remove(f"./data/audio/{file}")

    recursive_remove("./data/logs")

    if os.path.exists("./saves"):
        recursive_remove("./saves")
        os.rmdir("./saves")