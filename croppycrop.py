import json

# === CONFIG ===
GRID_WIDTH = 20
GRID_HEIGHT = 20

# unit_type index → character (Großbuchstabe = Spieler 1, Kleinbuchstabe = Spieler 2)
UNIT_TYPE_TO_CHAR = {
    0: "W",  # Warrior
    1: "M",  # Miner
    2: "C",  # Carrier
    3: "T",  # Tank
}

# Non-unit types → single character (unverändert)
TYPE_TO_CHAR = {
    0: "B",  # base/core
    2: "R",  # resource/deposit
    3: "L",  # waLL
    4: "G",  # gem pile
}

EMPTY_CHAR = "A"  # empty tile


def load_replay(path):
    with open(path, "r") as f:
        return json.load(f)


def get_team_order(data):
    """Gibt (team_id_player1, team_id_player2) zurück.
    Spieler 1 = Platz 0 (Gewinner), Spieler 2 = Platz 1 — oder einfach
    nach Reihenfolge in team_results wenn kein klarer Gewinner."""
    teams = data["misc"]["team_results"]
    sorted_teams = sorted(teams, key=lambda t: t["place"])
    p1_id = sorted_teams[0]["id"]
    p2_id = sorted_teams[1]["id"]
    p1_name = sorted_teams[0]["name"]
    p2_name = sorted_teams[1]["name"]
    print(f"Spieler 1 (Großbuchstaben): {p1_name} (id={p1_id})")
    print(f"Spieler 2 (Kleinbuchstaben): {p2_name} (id={p2_id})")
    return p1_id, p2_id


def build_frames(data, p1_id, p2_id):
    ticks = data["ticks"]
    current_objects = {}
    frames = []

    for tick_index in sorted(ticks, key=lambda x: int(x)):
        tick = ticks[tick_index]

        # Apply updates (diff system)
        if "objects" in tick:
            for obj in tick["objects"]:
                obj_id = obj["id"]

                # Remove dead objects
                if obj.get("state") == "dead":
                    current_objects.pop(obj_id, None)
                    continue

                if obj_id not in current_objects:
                    current_objects[obj_id] = {}
                current_objects[obj_id].update(obj)

        # Build grid
        grid = [[EMPTY_CHAR for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        for obj in current_objects.values():
            if "x" not in obj or "y" not in obj or "type" not in obj:
                continue

            x, y = obj["x"], obj["y"]
            if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
                continue

            obj_type = obj["type"]

            if obj_type == 1:
                # Unit: Zeichen abhängig von unit_type und Team
                unit_type = obj.get("unit_type", 0)
                char = UNIT_TYPE_TO_CHAR.get(unit_type, "U")
                team_id = obj.get("teamId")
                if team_id == p2_id:
                    char = char.lower()
                # p1 bleibt Großbuchstabe (oder unbekanntes Team auch)
                grid[y][x] = char
            else:
                grid[y][x] = TYPE_TO_CHAR.get(obj_type, "?")

        # Flatten to single string (NO spaces)
        frame_str = "".join("".join(row) for row in grid)
        frames.append(frame_str)

    return frames


def export_to_txt(frames, output_path):
    with open(output_path, "w") as f:
        for frame in frames:
            f.write(frame + "\n")


if __name__ == "__main__":
    replay_path = "replay.json"
    output_path = "scratch_frames.txt"

    data = load_replay(replay_path)
    p1_id, p2_id = get_team_order(data)
    frames = build_frames(data, p1_id, p2_id)
    export_to_txt(frames, output_path)
    print(f"Exported {len(frames)} frames.")
    print()
    print("Zeichenlegende:")
    print("  W/w = Warrior  (Spieler 1 groß / Spieler 2 klein)")
    print("  M/m = Miner")
    print("  C/c = Carrier")
    print("  T/t = Tank")
    print("  B   = Base/Core")
    print("  R   = Resource/Deposit")
    print("  L   = Wall")
    print("  G   = Gem Pile")
    print("  A   = leer")