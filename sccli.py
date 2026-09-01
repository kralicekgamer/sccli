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
    
    lines = ""

    data_last = data[-1]

    for line in data:
        lines += f"{purple}║ {reset}" + line.ljust(80) + f"{purple}║{reset}"

        if line != data_last:
            lines += "\n"

    msg = f"""
{purple}╔═════════════════════════════════════════════════════════════════════════════════╗{reset}
{lines}
{purple}╚═════════════════════════════════════{reset} {bold}SCCLI{reset} {purple}═════════════════════════════════════╝{reset}
"""
    return msg


def get_prihlaseno(data):
    jidla_prihlaseno = []
    
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

    if args.today is not None:
        print(send_msg(make_msg(get_prihlaseno(Filter.filter_json(["nazev", "druh_popis", "chod", "pocet", "druh"], api.getJidelnicekToday())), args.today)))

if __name__ == "__main__":
    main()
