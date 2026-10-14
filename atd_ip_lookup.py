#!/usr/bin/env python3
"""ATD IP Lookup — public IP metadata lookup for learning and troubleshooting."""
import ipaddress
import json
import sys
from urllib.parse import quote

try:
    import requests
    from colorama import init, Fore, Style
except ImportError:
    print("Install dependencies: python -m pip install requests colorama")
    sys.exit(1)

init(autoreset=True)
API_BASE = "https://ipwho.is/"
TIMEOUT = 12


def banner():
    print(Fore.GREEN + Style.BRIGHT + r"""
     █████╗ ████████╗██████╗
    ██╔══██╗╚══██╔══╝██╔══██╗
    ███████║   ██║   ██║  ██║
    ██╔══██╗   ██║   ██║  ██║
    ██║  ██║   ██║   ██████╔╝
    ╚═╝  ╚═╝   ╚═╝   ╚═════╝
""" + Style.RESET_ALL)
    print(Fore.CYAN + Style.BRIGHT + "       ATD IP LOOKUP")
    print(Fore.YELLOW + "       Akhil Tech Developer | v1.0")
    print(Fore.GREEN + "  " + "─" * 44)


def show(label, value):
    print(Fore.CYAN + f"{label:<22}" + Fore.WHITE +
          (str(value) if value not in (None, "") else "Not available"))


def lookup(ip_text):
    try:
        ip_obj = ipaddress.ip_address(ip_text)
    except ValueError:
        print(Fore.RED + "Invalid IP address. Please check and try again.")
        return

    print(Fore.GREEN + "\n[+] IP classification")
    show("IP address:", ip_obj)
    show("IP version:", f"IPv{ip_obj.version}")
    show("Global/public:", "Yes" if ip_obj.is_global else "No (private/reserved/non-global)")

    if not ip_obj.is_global:
        print(Fore.YELLOW + "\nThis IP is not globally routable. Public lookup databases generally cannot identify a device from a private IP.")
        return

    print(Fore.YELLOW + "\n[+] Querying public IP metadata service...")
    try:
        response = requests.get(
            API_BASE + quote(str(ip_obj), safe=""),
            headers={"User-Agent": "ATD-IP-Lookup/1.0"},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        print(Fore.RED + f"Lookup failed: {exc}")
        return

    if not data.get("success", False):
        print(Fore.RED + "Lookup service could not resolve this IP.")
        print("Reason:", data.get("message", "No additional details"))
        return

    connection = data.get("connection") or {}
    timezone_info = data.get("timezone") or {}
    print(Fore.GREEN + "\n[+] Public lookup results")
    show("Country:", data.get("country"))
    show("Region:", data.get("region"))
    show("City:", data.get("city"))
    lat, lon = data.get("latitude"), data.get("longitude")
    show("Approx. coordinates:", f"{lat}, {lon}" if lat is not None and lon is not None else None)
    show("Postal code:", data.get("postal"))
    show("Timezone:", timezone_info.get("id"))
    show("ISP:", connection.get("isp"))
    show("Organization:", connection.get("org"))
    show("ASN:", connection.get("asn"))
    show("Domain:", connection.get("domain"))

    report = {
        "tool": "ATD IP Lookup",
        "ip": str(ip_obj),
        "ip_version": ip_obj.version,
        "is_global": ip_obj.is_global,
        "lookup_source": "ipwho.is",
        "results": data,
        "note": "Geolocation is approximate; this does not identify a specific person or device owner."
    }
    try:
        with open("atd_ip_lookup.json", "w", encoding="utf-8") as file:
            json.dump(report, file, indent=2, ensure_ascii=False)
        print(Fore.GREEN + "\n[+] JSON report saved: atd_ip_lookup.json")
    except OSError as exc:
        print(Fore.RED + f"Could not save report: {exc}")

    print(Fore.YELLOW + "\nNote: location and organization data can be inaccurate.")
    print("The lookup service receives the queried IP; check its privacy policy before use.")


def main():
    banner()
    try:
        ip_text = sys.argv[1].strip() if len(sys.argv) > 1 else input(
            Fore.YELLOW + "\n  ┌────────────────────────────────────┐\n"
            "  │ " + Fore.WHITE + "Enter IP address (IPv4 or IPv6)" +
            Fore.YELLOW + "   │\n  └────────────────────────────────────┘\n"
            + Fore.GREEN + "  ATD IP > " + Fore.WHITE
        ).strip()
        lookup(ip_text)
    except (KeyboardInterrupt, EOFError):
        print(Fore.YELLOW + "\nCancelled.")


if __name__ == "__main__":
    main()
