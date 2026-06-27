import sys

import requests

HEROES_URL = "https://api.opendota.com/api/heroes"
PLAYER_URL = "https://api.opendota.com/api/players/{account_id}"
PLAYER_WL_URL = "https://api.opendota.com/api/players/{account_id}/wl"
PLAYER_MATCHES_URL = "https://api.opendota.com/api/players/{account_id}/matches"
PLAYER_HEROES_URL = "https://api.opendota.com/api/players/{account_id}/heroes"


def get_heroes():
    response = requests.get(HEROES_URL)
    response.raise_for_status()
    return response.json()


def get_player(account_id):
    response = requests.get(PLAYER_URL.format(account_id=account_id))
    response.raise_for_status()
    return response.json()


def print_heroes():
    heroes = get_heroes()
    for hero in heroes:
        print(hero["localized_name"])


def get_hero_names():
    heroes = get_heroes()
    return {hero["id"]: hero["localized_name"] for hero in heroes}


def get_win_loss(account_id):
    response = requests.get(PLAYER_WL_URL.format(account_id=account_id))
    response.raise_for_status()
    return response.json()


def print_player(account_id):
    player = get_player(account_id)
    wl = get_win_loss(account_id)
    profile = player.get("profile", {})
    print("Nombre:", profile.get("personaname"))
    print("Pais:", profile.get("loccountrycode"))
    print("MMR estimado:", player.get("mmr_estimate", {}).get("estimate"))
    print("Partidas ganadas:", wl.get("win"))
    print("Partidas perdidas:", wl.get("lose"))


def get_recent_matches(account_id, limit=10):
    params = {"limit": limit}
    response = requests.get(PLAYER_MATCHES_URL.format(account_id=account_id), params=params)
    response.raise_for_status()
    return response.json()


def print_recent_matches(account_id, limit=10, hero_names=None):
    hero_names = hero_names or {}
    matches = get_recent_matches(account_id, limit)
    for match in matches:
        resultado = "Victoria" if match.get("radiant_win") == (match.get("player_slot") < 128) else "Derrota"
        hero_nombre = hero_names.get(match.get("hero_id"), f"Hero ID {match.get('hero_id')}")
        print(
            f"Match ID: {match.get('match_id')} | Heroe: {hero_nombre} | "
            f"Resultado: {resultado} | Duracion: {match.get('duration')}s"
        )


def get_player_heroes(account_id):
    response = requests.get(PLAYER_HEROES_URL.format(account_id=account_id))
    response.raise_for_status()
    return response.json()


def print_most_played_hero(account_id, hero_names=None):
    hero_names = hero_names or {}
    player_heroes = get_player_heroes(account_id)
    if not player_heroes:
        print("No hay datos de heroes para este jugador.")
        return
    top = max(player_heroes, key=lambda h: h.get("games", 0))
    hero_nombre = hero_names.get(top.get("hero_id"), f"Hero ID {top.get('hero_id')}")
    print(f"Heroe mas usado: {hero_nombre} | Partidas: {top.get('games')} | Victorias: {top.get('win')}")


def main():
    if len(sys.argv) > 1:
        account_id = sys.argv[1]
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        hero_names = get_hero_names()
        print_player(account_id)
        print()
        print_most_played_hero(account_id, hero_names)
        print()
        print_recent_matches(account_id, limit, hero_names)
    else:
        print_heroes()


if __name__ == "__main__":
    main()
