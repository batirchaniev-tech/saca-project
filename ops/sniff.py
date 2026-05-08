# ops/sniff.py
import re
import datetime
from ops.utils import load_config, save_json, timestamp

try:
    from scapy.all import sniff, IP, TCP, Raw
    HAS_SCAPY = True
except ImportError:
    HAS_SCAPY = False


class PacketSniffer:
    def __init__(self, interface=None, count=30):
        self.interface = interface
        self.count = count
        cfg = load_config().get("sniff", {})
        self.output_file = cfg.get("output_file", "reports/sniff_report.json")

        self.stats = {
            "total_packets": 0,
            "http_packets": 0,
            "credential_hits": 0,
            "packets": []
        }

        self.cred_patterns = [
            re.compile(r"(?i)(username|user|login|email)\s*[:=]\s*\S+"),
            re.compile(r"(?i)(password|pass|pwd)\s*[:=]\s*\S+"),
            re.compile(r"(?i)Authorization:\s*Basic\s+[A-Za-z0-9+/=]+")
        ]

    def _process_packet(self, pkt):
        self.stats["total_packets"] += 1

        # Alleen TCP pakketjes met inhoud verwerken, want HTTP zit daar in
        if pkt.haslayer(TCP) and pkt.haslayer(Raw):
            try:
                payload = pkt[Raw].load.decode("utf-8", errors="ignore")
            except Exception:
                return

            if "HTTP" in payload or "GET " in payload or "POST " in payload:
                self.stats["http_packets"] += 1

                creds = []
                for pattern in self.cred_patterns:
                    found = pattern.findall(payload)
                    if found:
                        creds.extend(found)
                        self.stats["credential_hits"] += len(found)

                entry = {
                    "timestamp": timestamp(),
                    "src": pkt[IP].src if pkt.haslayer(IP) else "unknown",
                    "dst": pkt[IP].dst if pkt.haslayer(IP) else "unknown",
                    "sport": pkt[TCP].sport,
                    "dport": pkt[TCP].dport,
                    "payload_preview": payload[:200],
                    "credentials_found": creds
                }

                self.stats["packets"].append(entry)

                if creds:
                    print(f"[!] Credential hit from {entry['src']}")

    def start(self):
        if not HAS_SCAPY:
            print("[!] Scapy not installed. Run: pip install scapy")
            return

        print(f"[SNIFF] Sniffing {self.count} packets on interface: {self.interface or 'default'}")

        try:
            sniff(
                iface=self.interface,
                count=self.count,
                prn=self._process_packet,
                store=False
            )
        except PermissionError:
            print("[!] Permission denied. Run as administrator/root.")
            return
        except Exception as e:
            print(f"[!] Sniff error: {e}")
            return

        self._save_report()
        self._print_summary()

    def _save_report(self):
        self.stats["saved_at"] = datetime.datetime.now().isoformat()
        save_json(self.stats, self.output_file)

    def _print_summary(self):
        print("\n[SNIFF] Summary")
        print(f"  Total packets: {self.stats['total_packets']}")
        print(f"  HTTP packets: {self.stats['http_packets']}")
        print(f"  Credential hits: {self.stats['credential_hits']}")


def run_sniff(args):
    sniffer = PacketSniffer(
        interface=args.interface,
        count=args.count
    )
    sniffer.start()

