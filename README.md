# CyberSec Ops Toolkit 2.0

Een modulaire command-line toolkit voor cybersecurity taken zoals bestandsscanning,
netwerkscanning, web scraping, SSH automatisering en meer.
Gebouwd in Python met een object-georiënteerde architectuur.

---

## Installatie

Zorg dat Python 3.10 of hoger geïnstalleerd is. Installeer dan de dependencies:

pip install requests beautifulsoup4 paramiko scapy selenium send2trash psutil rich pyyaml

---

## Hoe starten?

python main.py <subcommando> [argumenten]

of

python -m ops.cli <subcommando> [argumenten]

---

## Subcommando's

### scan — Bestandsscanner
Zoekt naar verdachte bestanden op basis van extensie, bestandsnaam en inhoud.

python main.py scan data/ --quarantine

Voorbeeld output:
[SCAN] Directory: data/
[SCAN] Total files: 5
[SCAN] Suspicious: 2
  [!] data/backdoor.bat
      - suspicious extension .bat
  [!] data/script.py
      - pattern match: password\s*=

---

### net-scan — Netwerkscanner
Scant open poorten op een host of heel CIDR-bereik met meerdere threads.

python main.py net-scan 192.168.1.1 --ports 22,80,443 --threads 50

Voorbeeld output:
[NET-SCAN] Hosts: 1, Ports per host: 3
  [OPEN] 192.168.1.1:80 (http)
  [OPEN] 192.168.1.1:443 (https)

---

### sniff — Packet Sniffer
Onderschept netwerkpakketjes en zoekt naar wachtwoorden of credentials in HTTP verkeer.

python main.py sniff --interface eth0 --count 50

Voorbeeld output:
[SNIFF] Sniffing 50 packets on interface: eth0
[!] Credential hit from 192.168.1.5
[SNIFF] Summary
  Total packets: 50
  HTTP packets: 3
  Credential hits: 1

---

### scrape — Web Scraper
Haalt een webpagina op en extraheert tekst via CSS selectors. Detecteert ook emailadressen.

python main.py scrape https://example.com --selector p

Voorbeeld output:
[SCRAPE] URL: https://example.com
[SCRAPE] Selector: p
[SCRAPE] Found: 3 elements
[SCRAPE] Emails found: ['info@example.com']

---

### web-auto — Web Automatisering
Opent een browser via Selenium, laadt een pagina en maakt een screenshot.

python main.py web-auto https://example.com

Voorbeeld output:
[WEB-AUTO] Opening: https://example.com
[WEB-AUTO] Page title: Example Domain
[WEB-AUTO] Screenshot saved: data/screenshots/screenshot_20260506_120000.png

---

### ssh — SSH Automatisering
Verbindt met een remote server via SSH en voert commando's uit. Ondersteunt ook lokale commando's.

python main.py ssh --host 192.168.1.10 --username admin --password secret --command "whoami"

Lokaal commando:
python main.py ssh --local --command "whoami"

Voorbeeld output:
[SSH] Connected to 192.168.1.10:22
[SSH] > whoami
       admin
[SSH] Disconnected.

---

### serve — HTTP Dashboard
Start een lokale webserver die alle JSON rapporten toont via de browser.

python main.py serve --host 0.0.0.0 --port 8888

Voorbeeld output:
[SERVE] Dashboard running at http://0.0.0.0:8888/reports
[SERVE] Press Ctrl+C to stop.

---

### report — Rapportage en Email
Voegt alle JSON rapporten samen tot één bestand en stuurt optioneel een email.

python main.py report --email jouw@email.com

Voorbeeld output:
[REPORT] Found 4 report files
[REPORT] Merged report saved to: reports/merged_report.json
[REPORT] Email prepared, base64 preview: Q29udGVudC1UeXBlOiBtdWx0aXBhcnQv...

---

### sysmon — Systeemmonitor
Monitort CPU, RAM en schijfgebruik over meerdere samples en toont een tabel.

python main.py sysmon --config data/sysmon_config.yaml

Voorbeeld output:
[SYSMON] Collecting 5 samples every 2s
  CPU: 12.3% | RAM: 67.4%
[SYSMON] Report saved to reports/sysmon_report.json

---

## Checklist verplichte modules

| Module | Waar gebruikt? |
|---|---|
| argparse | cli.py |
| base64 | report.py, web_auto.py, utils.py |
| bs4 | scrape.py |
| datetime | scrape.py, sniff.py, ssh.py, web_auto.py |
| email | report.py |
| fnmatch | files.py |
| glob | files.py, report.py |
| http | serve.py |
| image_viewer | web_auto.py |
| itertools | net.py |
| json | files.py, report.py, ssh.py, utils.py |
| os | files.py, utils.py |
| paramiko | ssh.py |
| pathlib | files.py, utils.py, web_auto.py |
| random | net.py |
| re | files.py, scrape.py, sniff.py |
| requests | scrape.py |
| scapy | sniff.py |
| selenium | web_auto.py |
| send2trash | files.py |
| shutil | files.py |
| socket | net.py, report.py |
| subprocess | ssh.py |
| sys | utils.py, main.py |
| threading | net.py |
| time | net.py |

---

## Drie zelfgekozen modules

### 1. rich
Wat doet het?
rich is een Python module voor mooie terminal output. Je kan er tabellen, kleuren
en opgemaakte tekst mee tonen in de terminal.

Waarom gekozen?
De sysmon output is veel leesbaarder als een echte tabel dan als losse printregels.

Waar gebruikt?
In sysmon.py om de verzamelde CPU, RAM en schijfdata te tonen als een tabel
via rich.table.Table en rich.console.Console.

---

### 2. pyyaml
Wat doet het?
pyyaml is een module om YAML bestanden te lezen en schrijven. YAML is een
configuratieformaat dat makkelijker leesbaar is dan JSON.

Waarom gekozen?
Voor de sysmon configuratie is YAML handiger omdat je interval en samples
makkelijk kan aanpassen zonder JSON syntax te moeten volgen.

Waar gebruikt?
In sysmon.py om een optioneel sysmon_config.yaml bestand in te laden
via yaml.safe_load().

---

### 3. psutil
Wat doet het?
psutil is een module die systeeminformatie ophaalt zoals CPU gebruik,
geheugen, schijfruimte en netwerkverkeer.

Waarom gekozen?
Voor de sysmon subtool heb je een manier nodig om echte systeemdata op
te halen. psutil is de standaard module hiervoor in Python.

Waar gebruikt?
In sysmon.py via psutil.cpu_percent(), psutil.virtual_memory(),
psutil.disk_usage() en psutil.net_io_counters().

---

## Ethische disclaimer

Deze toolkit is uitsluitend bedoeld voor gebruik op eigen systemen of in
legale testomgevingen zoals een eigen laboratorium of een omgeving waarvoor
je expliciete toestemming hebt gekregen.

Gebruik van deze toolkit op systemen zonder toestemming is illegaal en
strafbaar onder de wet. De ontwikkelaar is niet verantwoordelijk voor
misbruik van deze software.

Gebruik altijd verantwoordelijk en ethisch.