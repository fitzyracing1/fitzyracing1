import json
import random

# === Event data (inline for demo) ===
EVENTS_JSON = """
                                  
"""
EVENTS_JSON = """
[
  {
    "id": "refugee_convoy",
    "title": "Refugee Convoy",
    "description": "A line of weary civilians trudges along the road, carts piled high with what little they could carry.",
    "choices": [
      {
        "id": "help",
        "text": "Help them reach safety",
        "effects": {"morale": 2, "time": 1, "resources": -1},
        "flavor": "They thank you with tears in their eyes, but the delay costs you precious daylight."
      },
      {
        "id": "take_supplies",
        "text": "Take their supplies",
        "effects": {"morale": -2, "resources": 2},
        "flavor": "They curse your name as you walk away heavier but colder."
      }
    ]
  },
  {
    "id": "martian_scout",
    "title": "Martian Scout Tripod",
    "description": "A lone tripod stalks the horizon, its heat‑ray sweeping the fields.",
    "choices": [
      {
        "id": "avoid",
        "text": "Hide and wait for it to pass",
        "effects": {"time": 1, "risk": -0.2},
        "flavor": "You hold your breath as the shadow passes over you."
      },
      {
        "id": "engage",
        "text": "Attack the scout",
        "effects": {"morale": 1, "risk": 0.5},
        "flavor": "Your shots spark against its armor — it turns toward you."
      }
    ]
  },
  {
    "id": "telegraph_station",
    "title": "Abandoned Telegraph Station",
    "description": "The door hangs open, wires spilling like vines.",
    "choices": [
      {
        "id": "search",
        "text": "Search for working parts",
        "effects": {"intel": 1, "risk": 0.3},
        "flavor": "You pocket a coil and a battered key — maybe enough to send a signal."
      },
      {
        "id": "bypass",
        "text": "Leave it alone",
        "effects": {},
        "flavor": "You keep moving, the silence pressing in."
      }
    ]
  },
  {
    "id": "rail_bridge",
    "title": "Rail Bridge Decision",
    "description": "The bridge spans a deep gorge — a perfect choke point.",
    "choices": [
      {
        "id": "blow",
        "text": "Demolish the bridge",
        "effects": {"time": 2, "escape_routes": -1},
        "flavor": "The explosion echoes for miles — the Martians will have to find another way."
      },
      {
        "id": "leave",
        "text": "Leave it intact",
        "effects": {"time": -1},
        "flavor": "You hurry across, knowing the enemy can too."
      }
    ]
  },
  {
    "id": "crash_site",
    "title": "Crash Site Showdown",
    "description": "The cylinder looms before you, guarded by a war machine.",
    "choices": [
      {
        "id": "sabotage",
        "text": "Sabotage the cylinder",
        "effects": {"ending": "victory"},
        "flavor": "You slip inside and wreck the machinery — the song dies."
      },
      {
        "id": "assault",
        "text": "Direct assault",
        "effects": {"risk": 0.8, "morale": 2, "ending": "pyrrhic"},
        "flavor": "You charge, weapons blazing — the machine shudders, but at a cost."
      },
      {
        "id": "signal",
        "text": "Signal HQ",
        "requirements": {"intel": 1},
        "effects": {"ending": "victory"},
        "flavor": "The key clicks, the message flies — help is on the way."
      }
    ]
  }
]
"""
# === Epilogue generator ===
def generate_epilogue(state):
    if not state.get("alive", True) or state.get("morale", 0) <= 0:
        return "The black smoke rolled in. Silence followed."
    ending = state.get("ending")
    if ending == "victory":
        return "The cylinder’s song died. Reinforcements are on the move."
    elif ending == "pyrrhic":
        return "You lived to see the smoke rise over the capital."
    else:
        return "You slip away into the night, the war far from over."

# === Game loop ===
def play_pilot():
    events = json.loads(EVENTS_JSON)
    state = {
        "morale": 5,
        "resources": 2,
        "intel": 0,
        "time": 0,
        "alive": True,
        "ending": None
    }

    print("\n=== PILOT EPISODE: THE FIRST CYLINDER ===")
    print("At 04:17, the sky tore open. A cylinder fell beyond the ridge.\n")

    # Act I & II: randomize order, keep crash_site last
    non_final = [e for e in events if e["id"] != "crash_site"]
    random.shuffle(non_final)
    ordered_events = non_final + [e for e in events if e["id"] == "crash_site"]

    for ev in ordered_events:
        print(f"\n--- {ev['title']} ---")
        print(ev["description"])
        choices = ev["choices"]

        # Filter by requirements
        available = []
        for c in choices:
            reqs = c.get("requirements", {})
            if all(state.get(k, 0) >= v for k, v in reqs.items()):
                available.append(c)

        for i, c in enumerate(available, 1):
            print(f"{i}. {c['text']}")

        # Get player choice
        while True:
            try:
                sel = int(input("> ")) - 1
                if 0 <= sel < len(available):
                    choice = available[sel]
                    break
            except ValueError:
                pass
            print("Invalid choice.")

        # Apply effects
        for k, v in choice.get("effects", {}).items():
            if k == "ending":
                state["ending"] = v
            else:
                state[k] = state.get(k, 0) + v

        print(choice["flavor"])

        # Simple risk check
        risk = choice.get("effects", {}).get("risk", 0)
        if risk > 0 and random.random() < risk:
            print("You were injured in the encounter!")
            state["morale"] -= 1
            if state["morale"] <= 0:
                state["alive"] = False
                break

    # If no ending set, decide based on survival
    if not state["ending"]:
        state["ending"] = "defeat" if not state["alive"] else "pyrrhic"

    print("\n=== EPILOGUE ===")
    print(generate_epilogue(state))

if __name__ == "__main__":
    play_pilot()