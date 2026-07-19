# Palwatcher

Monitora un server ufficiale **Palworld** (tramite l'API pubblica di [BattleMetrics](https://www.battlemetrics.com/)) e ti avvisa con suono + popup non appena si libera un posto libero.

> Powered by **beriazzo03** & **Claude Strife**

## Cosa fa

- Cerchi il tuo server ufficiale per nome e lo salvi.
- Lo script controlla periodicamente (di default ogni 1,1 secondi) quanti giocatori ci sono rispetto al massimo.
- Appena si libera uno slot: beep ripetuti + finestra di popup sempre in primo piano.
- Il monitoraggio si ferma da solo dopo l'avviso (per non continuare a suonare), va rilanciato manualmente.

## Requisiti

- Windows
- Python 3.8+ ([python.org](https://www.python.org/) — durante l'installazione spunta "Add python.exe to PATH")
- Nessuna libreria esterna: usa solo moduli della libreria standard di Python.

## Uso da sorgente

```
python palworld_watcher_v5.py
```

Segui il menu a schermo:

1. **Cerca server** — cerca per nome su BattleMetrics e salva il server scelto
2. **Avvia monitoraggio** — parte il controllo periodico
3. **Imposta intervallo di controllo** — in secondi, minimo 1.1 (limite pratico legato al rate-limit di BattleMetrics: 60 richieste/minuto)
4. **Esci**

La configurazione (server scelto, intervallo) viene salvata in `palworld_watcher_config.json`, nella stessa cartella dello script/eseguibile.

## Compilare un eseguibile (.exe)

```
python -m pip install pyinstaller
python -m PyInstaller --onefile --console --name PalworldWatcher palworld_watcher_v5.py
```

L'eseguibile finale si trova in `dist/PalworldWatcher.exe`. Le cartelle `build/` e il file `.spec` generati durante la compilazione non servono e possono essere cancellati.

> **Nota:** alcuni antivirus / Windows Defender segnalano falsi positivi sugli eseguibili generati da PyInstaller — è un problema noto del tool di compilazione, non specifico di questo script. Il sorgente è pubblico in questo repository, quindi chiunque può verificare cosa fa il programma prima di eseguirlo.

## Limiti

- Il monitoraggio dipende dalla disponibilità e dai limiti di richieste dell'API pubblica di BattleMetrics.
- Lo script avvisa soltanto: il collegamento al server va fatto manualmente dal gioco.

## Licenza

Nessuna licenza specificata — tutti i diritti riservati agli autori, salvo diversa indicazione.
