import json
import argparse
import sys
import getpass
import keyring

from strava_cz_api import Api, Filter, Auth, StravaError


def send_msg(data):
    reset = "\033[0m"
    bold = "\033[01m"
    purple = "\033[35m"

    width = max(80, max(map(len, data), default=0))
    lines = ""

    for line in data:
        lines += f"{purple}║ {reset}" + line.ljust(width) + f"{purple}║{reset}"
        if line != data[-1]:
            lines += "\n"

    top = f"{purple}╔{'═' * (width + 1)}╗{reset}"
    footer_width = width - 6
    footer = (f"{purple}╚{'═' * (footer_width // 2)}{reset} "
              f"{bold}SCCLI{reset} {purple}"
              f"{'═' * (footer_width - footer_width // 2)}╝{reset}")
    msg = f"\n{top}\n{lines}\n{footer}\n"
    return msg


def get_prihlaseno(data, today=True):
    jidla_prihlaseno = []

    if today:
        data = data.get("table0", [])

    else:
        data = data.get("table1", [])

    try:
        for jidlo in data:
            if (jidlo["pocet"] == 1) or (jidlo["druh"] == "PO"):
                jidla_prihlaseno.append(jidlo)

        return jidla_prihlaseno

    except StravaError:
        login()


def make_msg(data, args):
    lines = []

    if args == "all":
        for jidlo in data:
            lines.append(f"{jidlo["druh_popis"]}: {jidlo["nazev"]}")

    elif args == "obed":
        for jidlo in data:
            if jidlo["chod"] == "C":
                lines.append(f"{jidlo["druh_popis"]}: {jidlo["nazev"]}")
            if jidlo["druh"] == "PO":
                lines.append(f"{jidlo["druh_popis"]}: {jidlo["nazev"]}")

    elif args == "vecere":
        for jidlo in data:
            if jidlo["chod"] == "E":
                lines.append(f"{jidlo["druh_popis"]}: {jidlo["nazev"]}")

            if jidlo["chod"] == "F":
                lines.append(f"{jidlo["druh_popis"]}: {jidlo["nazev"]}")

    if lines == []:
        lines = ["Dnes není nic k jídlu :("]

    return lines
        

def parse_args():
    parser = argparse.ArgumentParser(prog="sccli", description="Strava.cz CLI")

    parser.add_argument("--delete", action="store_true", help="Smazat uživatele")
    parser.add_argument("--today", nargs="?", const="all", help="Zobrazit dnešní jídelníček")
    parser.add_argument("--next", nargs="?", const="all", help="Zobrazit zítřejší jídelníček")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


def login():
    try:
        sid = keyring.get_password("sccli", "sid")
        s5url = keyring.get_password("sccli", "s5url")
        jidelna = keyring.get_password("sccli", "jidelna")

        if sid is None or s5url is None or jidelna is None:
            raise KeyError("Vrací None")

    except:
        username = input("Zadej zde svoje uživatelské jméno: ")
        password = getpass.getpass("Zadej zde svoje heslo: ")
        jidelna = input("Zadej zde číslo jídelny: ")

        try:
            data, _ = Auth.login(username, password, jidelna)

        except StravaError:
            print("Chybné heslo")
            exit()

        sid, s5url = Auth.getCredentials(data)
        
        keyring.set_password("sccli", "sid", sid)
        keyring.set_password("sccli", "s5url", s5url)
        keyring.set_password("sccli", "jidelna", jidelna)

    return Api(sid, s5url, jidelna)


def delete():
    keyring.delete_password("sccli", "sid")
    keyring.delete_password("sccli", "s5url")
    keyring.delete_password("sccli", "jidelna")


def main():
    args = parse_args()

    api = login()    

    if args.delete:
        delete()

    # arg = args.today if args.today is not None else args.next (inline final boss)

    if args.today is not None:
        print(send_msg(make_msg(Filter.filter_json(["nazev", "druh_popis", "chod", "pocet", "druh"], get_prihlaseno(json.loads(api.getJidelnicekAll()), True)), args.today)))

    if args.next is not None:
        print(send_msg(make_msg(Filter.filter_json(["nazev", "druh_popis", "chod", "pocet", "druh"], get_prihlaseno(json.loads(api.getJidelnicekAll()), False)), args.next)))


if __name__ == "__main__":
    main()
