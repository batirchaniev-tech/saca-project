# ops/cli.py
import argparse
import sys

def build_parser():
    parser = argparse.ArgumentParser(
        prog="cybersec-toolkit",
        description="CyberSec Ops Toolkit 2.0"
    )

    sub = parser.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan")
    p_scan.add_argument("path")
    p_scan.add_argument("--quarantine", action="store_true")

    p_net = sub.add_parser("net-scan")
    p_net.add_argument("target")
    p_net.add_argument("--ports")
    p_net.add_argument("--threads", type=int, default=50)
    p_net.add_argument("--timeout", type=float, default=1.0)

    p_sniff = sub.add_parser("sniff")
    p_sniff.add_argument("--interface")
    p_sniff.add_argument("--count", type=int, default=30)

    p_scrape = sub.add_parser("scrape")
    p_scrape.add_argument("url")
    p_scrape.add_argument("--selector", default="p")

    p_web = sub.add_parser("web-auto")
    p_web.add_argument("url")
    p_web.add_argument("--no-headless", action="store_true")

    p_ssh = sub.add_parser("ssh")
    p_ssh.add_argument("--host")
    p_ssh.add_argument("--username")
    p_ssh.add_argument("--password")
    p_ssh.add_argument("--key")
    p_ssh.add_argument("--port", type=int, default=22)
    p_ssh.add_argument("--command", dest="command", required=True)
    p_ssh.add_argument("--local", action="store_true")

    p_serve = sub.add_parser("serve")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8888)

    p_report = sub.add_parser("report")
    p_report.add_argument("--email")

    p_sys = sub.add_parser("sysmon")
    p_sys.add_argument("--config")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        sys.exit(0)

    if args.cmd == "scan":
        from ops.files import run_scan
        run_scan(args)

    elif args.cmd == "net-scan":
        from ops.net import run_net_scan
        run_net_scan(args)

    elif args.cmd == "sniff":
        from ops.sniff import run_sniff
        run_sniff(args)

    elif args.cmd == "scrape":
        from ops.scrape import run_scrape
        run_scrape(args)

    elif args.cmd == "web-auto":
        from ops.web_auto import run_web_auto
        run_web_auto(args)

    elif args.cmd == "ssh":
        from ops.ssh import run_ssh
        run_ssh(args)

    elif args.cmd == "serve":
        from ops.serve import run_serve
        run_serve(args)

    elif args.cmd == "report":
        from ops.report import run_report
        run_report(args)

    elif args.cmd == "sysmon":
        from ops.sysmon import run_sysmon
        run_sysmon(args)
