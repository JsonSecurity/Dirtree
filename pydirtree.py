import requests
from bs4 import BeautifulSoup
import json
import sys
import time

def explorar_directorio(url):
    """[+] Explora un directorio en un Directory Listing y devuelve una estructura JSON."""
    print(f"Verificando URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error al acceder a {url}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    enlaces = soup.find_all("a")

    directorio = {"name": url.rstrip('/').split('/')[-1] or "root", "type": "directory", "children": []}
    
    for enlace in enlaces:
        nombre = enlace.text.strip()
        href = enlace.get("href")
        
        # Evitar los enlaces a directorios padre (../)
        if nombre in ["Parent Directory", ".."]:
            continue

        # Si termina en "/", es un subdirectorio
        if href.endswith("/"):
            sub_url = url.rstrip('/') + "/" + href
            subdir_json = explorar_directorio(sub_url)
            if subdir_json:
                directorio["children"].append(subdir_json)
        else:
            directorio["children"].append({"name": nombre, "type": "file"})

        time.sleep(0.5)

    return directorio

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"\n [!] Uso: {sys.argv[0]} <url>\n")
        sys.exit(1)

    root_url = sys.argv[1]
    json_structure = explorar_directorio(root_url)

    if json_structure:
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(json_structure, f, indent=4)

        print("\n📂 Mapa de directorios guardado en output.json")
    else:
        print("\n❌ No se pudo generar el JSON.")
