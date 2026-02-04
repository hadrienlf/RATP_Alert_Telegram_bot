import os
import requests
import time
import sys
from dotenv import load_dotenv

import datetime

# Charge les variables d'environnement depuis le fichier .env (si présent, pour le local)
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
API_KEY_IDFM = os.getenv('API_KEY_IDFM')

# Dictionnaire des lignes à surveiller
LINES = {
    "Ligne 1": "line:IDFM:C01371",
    "Ligne 13": "line:IDFM:C01383",
    "RER E": "line:IDFM:C01729"
}

def send_telegram(text):
    # En mode manuel, on affiche aussi dans la console
    if sys.stdout.isatty():
        print(f"TELEGRAM: {text}")
        
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Erreur : Token Telegram ou Chat ID manquant.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erreur envoi Telegram : {e}")

def check_line(line_name, line_id):
    headers = {"apikey": API_KEY_IDFM}
    url_api = f"https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/lines/{line_id}/line_reports"
    max_retries = 3
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url_api, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # On cherche s'il y a des perturbations actives
            traffic_disruption = None
            now = datetime.datetime.now()

            if "disruptions" in data:
                for d in data["disruptions"]:
                    # 1. Filtre Ascenseur
                    if "Ascenseur" in d.get("tags", []):
                        continue
                    
                    # 2. Filtre Gravité (Information = on ignore)
                    severity_name = d.get("severity", {}).get("name", "").lower()
                    if severity_name == "information":
                        continue

                    # 3. Filtre Date (Est-ce actif maintenant ?)
                    # Les dates sont au format YYYYMMDDTHHMMSS
                    is_active = False
                    periods = d.get("application_periods", [])
                    if not periods:
                        # Si pas de période, on suppose actif par défaut (sécurité)
                        is_active = True
                    else:
                        for period in periods:
                            try:
                                begin_str = period.get("begin")
                                end_str = period.get("end")
                                # Parse dates
                                begin = datetime.datetime.strptime(begin_str, "%Y%m%dT%H%M%S")
                                end = datetime.datetime.strptime(end_str, "%Y%m%dT%H%M%S")
                                
                                if begin <= now <= end:
                                    is_active = True
                                    break
                            except ValueError:
                                # Si format de date bizarre, on ignore ou on considère actif par précaution
                                # Ici on continue pour voir les autres périodes
                                continue
                    
                    if not is_active:
                        continue

                    # Si on passe tous les filtres, c'est une vraie perturbation
                    traffic_disruption = d
                    break
            
            # Préfixe pour le mode manuel
            is_manual = sys.stdout.isatty()
            prefix = "(TEST) " if is_manual else ""

            if traffic_disruption:
                severity = traffic_disruption.get("severity", {}).get("name", "Inconnue")
                
                # On cherche le message détaillé
                cause = "Détail non disponible"
                for msg in traffic_disruption.get("messages", []):
                    if "web" in msg.get("channel", {}).get("types", []):
                        cause = msg.get("text", "")
                        break
                if cause == "Détail non disponible" and traffic_disruption.get("messages"):
                     cause = traffic_disruption["messages"][0].get("text", "")

                message = f"{prefix}⚠️ Perturbation sur la {line_name}\nStatut : {severity}\nDétails : {cause}"
                send_telegram(message)
                return False # Perturbation trouvée
            else:
                print(f"{line_name} : Trafic normal.")
                return True # Trafic normal
            
        except Exception as e:
            print(f"[{line_name}] Tentative {attempt}/{max_retries} échouée : {e}")
            if attempt < max_retries:
                time.sleep(2)
            else:
                send_telegram(f"Désolé, impossible de récupérer les infos pour {line_name} (3 erreurs).")
                return False # Considéré comme échec/non-normal pour l'agrégation

def check_ratp():
    print("--- Démarrage du contrôle RATP ---")
    normal_lines = []
    
    for name, line_id in LINES.items():
        if check_line(name, line_id):
            normal_lines.append(name)
            
    # Notification de succès global en mode manuel uniquement
    is_manual = sys.stdout.isatty()
    if is_manual:
        prefix = "(TEST) "
        if len(normal_lines) == len(LINES):
            send_telegram(f"{prefix}✅ Trafic normal sur : {', '.join(normal_lines)}")
        elif normal_lines:
            # Optionnel : si on veut notifier que certaines sont OK même si d'autres sont KO
            pass

if __name__ == "__main__":
    check_ratp()