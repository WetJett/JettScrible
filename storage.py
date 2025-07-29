import json
import os

# Øëÿõ äî ôàéëó, äå çáåğ³ãàòèìåìî äàí³ êîğèñòóâà÷³â
STORAGE_FILE = "user_data.json"

LANGUAGE_MAP = {
    "ua": "uk",
    "en": "en",
    "pl": "pl",
    "ru": "ru"
                       }

def load_user_data():
    """
    Loads user's data from JSON file.
    If file is empty or don't exists - returns emptp dict
    """
    if not os.path.exists(STORAGE_FILE):
        return {} # Ïîâåğòàºìî ïîğîæí³é ñëîâíèê, ÿêùî ôàéë íå ³ñíóº

    # Ïåğåâ³ğÿºìî, ÷è ôàéë íå ïîğîæí³é
    if os.path.getsize(STORAGE_FILE) == 0:
        return {} # Ïîâåğòàºìî ïîğîæí³é ñëîâíèê, ÿêùî ôàéë ïîğîæí³é

    # ßêùî ôàéë ³ñíóº ³ íå ïîğîæí³é, íàìàãàºìîñÿ éîãî çàâàíòàæèòè
    with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Íà âèïàäîê, ÿêùî ôàéë ç³ïñîâàíèé àáî ì³ñòèòü íåâàë³äíèé JSON
            print(f"Error while decoding file {STORAGE_FILE}. Maling empty dict...")
            return {}

def save_user_data(data):
    '''Saving user's data in JSON file.'''
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user_language(user_id: int) -> str:
    '''Tekes user's language'''
    user_data = load_user_data()
    return user_data.get(str(user_id), {}).get("language", None)

def set_user_language(user_id: int, language: str):
    '''Saving user's lang.'''
    user_data = load_user_data()
    user_data.setdefault(str(user_id), {})["language"] = language
    save_user_data(user_data)