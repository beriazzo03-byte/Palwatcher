"""
PALWORLD SERVER WATCHER (Python) - v1
Monitora un server ufficiale Palworld (via API pubblica di BattleMetrics)
e avvisa con suono + finestra di popup quando si libera un posto.

REQUISITI:
  - Python 3.8+ installato su Windows (python.org -> durante l'installazione
    spunta "Add python.exe to PATH")
  - Nessuna libreria esterna da installare: usa solo moduli standard.

USO:
  1. Apri il Prompt dei comandi nella cartella dello script
  2. Esegui:  python palworld_watcher.py
  3. Segui il menu: prima "Cerca server" per trovarlo e salvarlo,
     poi "Avvia monitoraggio".
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
import ctypes

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "palworld_watcher_config.json")
API_BASE = "https://api.battlemetrics.com"
USER_AGENT = "PalworldWatcher-Python"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cerca_server():
    nome = input("Nome (o parte del nome) del server ufficiale Palworld da cercare: ").strip()
    if not nome:
        print("Nome vuoto, annullato.")
        return

    params = {
        "filter[game]": "palworld",
        "filter[search]": nome,
        "page[size]": "15",
    }
    url = f"{API_BASE}/servers?{urllib.parse.urlencode(params)}"

    try:
        data = http_get_json(url)
    except Exception as e:
        print(f"Errore nella richiesta a BattleMetrics: {e}")
        return

    risultati = data.get("data", [])
    if not risultati:
        print("Nessun server trovato con questo nome. Prova con una parola sola.")
        return

    print("\nServer trovati:")
    for i, s in enumerate(risultati, start=1):
        attr = s.get("attributes", {})
        print(f"  {i}. {attr.get('name')}  [{attr.get('players')}/{attr.get('maxPlayers')}]  (ID {s.get('id')})")

    scelta = input("\nScrivi il NUMERO del server giusto (invio per annullare): ").strip()
    if not scelta:
        print("Annullato.")
        return
    try:
        idx = int(scelta)
        assert 1 <= idx <= len(risultati)
    except (ValueError, AssertionError):
        print("Numero non valido.")
        return

    scelto = risultati[idx - 1]
    cfg = load_config()
    cfg["server_id"] = scelto["id"]
    cfg["server_name"] = scelto["attributes"]["name"]
    cfg.setdefault("poll_seconds", 1.1)
    save_config(cfg)
    print(f"\nSalvato: {cfg['server_name']} (ID {cfg['server_id']})")


def avvisa(server_name, players, maxp):
    # Suono ripetuto (Windows beep di sistema)
    try:
        import winsound
        for _ in range(8):
            winsound.Beep(1200, 300)
            time.sleep(0.25)
    except Exception:
        print("\a" * 8)  # fallback: beep del terminale

    # Popup bloccante in primo piano (funziona anche a finestra ridotta / schermo spento)
    try:
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Server: {server_name}\nGiocatori: {players}/{maxp}\n\nCollegati ora dal gioco!",
            "POSTO LIBERO SU PALWORLD!",
            0x40 | 0x1000,  # MB_ICONINFORMATION | MB_SYSTEMMODAL
        )
    except Exception as e:
        print(f"(popup non disponibile: {e})")


def avvia_monitoraggio():
    cfg = load_config()
    server_id = cfg.get("server_id")
    server_name = cfg.get("server_name")
    poll_seconds = cfg.get("poll_seconds", 1.1)

    if not server_id:
        print("Prima usa 'Cerca server' per trovare e salvare un server.")
        return

    print(f"\nMonitoraggio '{server_name}' ogni {poll_seconds} secondi. Premi Ctrl+C per fermare.\n")
    url = f"{API_BASE}/servers/{server_id}"

    try:
        while True:
            try:
                data = http_get_json(url)
                attr = data["data"]["attributes"]
                players = attr["players"]
                maxp = attr["maxPlayers"]
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] {server_name}: {players}/{maxp}")

                if players < maxp:
                    print("\n>>> POSTO LIBERO! <<<\n")
                    avvisa(server_name, players, maxp)
                    print("Monitoraggio fermato. Rilancia il programma per ricontrollare.")
                    break

            except Exception as e:
                print(f"Errore durante il controllo: {e}")

            time.sleep(poll_seconds)

    except KeyboardInterrupt:
        print("\nMonitoraggio interrotto dall'utente.")


def imposta_intervallo():
    cfg = load_config()
    attuale = cfg.get("poll_seconds", 1.1)
    valore = input(f"Ogni quanti secondi controllare? (attuale: {attuale}, minimo 1.1): ").strip()
    if not valore:
        print("Annullato.")
        return
    try:
        secondi = float(valore.replace(",", "."))
        assert secondi >= 1.1
    except (ValueError, AssertionError):
        print("Inserisci un numero (anche decimale, es. 1.1) di almeno 1.1 secondi.")
        return
    cfg["poll_seconds"] = secondi
    save_config(cfg)
    print(f"Intervallo impostato a {secondi} secondi.")


def menu():
    while True:
        cfg = load_config()
        nome_attuale = cfg.get("server_name", "(nessuno)")
        intervallo = cfg.get("poll_seconds", 1.1)
        print("\n=== PALWORLD SERVER WATCHER ===")
        print(f"Server salvato: {nome_attuale}")
        print(f"Intervallo controllo: {intervallo} sec")
        print("1. Cerca server")
        print("2. Avvia monitoraggio")
        print("3. Imposta intervallo di controllo")
        print("4. Esci")
        scelta = input("Scegli: ").strip()

        if scelta == "1":
            cerca_server()
        elif scelta == "2":
            avvia_monitoraggio()
        elif scelta == "3":
            imposta_intervallo()
        elif scelta == "4":
            sys.exit(0)
        else:
            print("Scelta non valida.")


if __name__ == "__main__":
    print("=" * 40)
    print("   PALWORLD SERVER WATCHER")
    print("   Powered by beriazzo03 & Claude Strife")
    print("   https://github.com/beriazzo03-byte/Palwatcher.git")
    print("=" * 40)
    menu()
