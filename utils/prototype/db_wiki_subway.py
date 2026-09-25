import json, requests, re, csv
from urllib.parse import unquote
from bs4 import BeautifulSoup
import overpass

# pip install beautifulsoup4
# pip install overpass

# чтобы забрать списки городов с википедии и через ключ wikidata
# подцепить osm-data используя библиотеку "overpass" "~overpass-turbo.de "
#
# export json and optional csv\html

TARGET_CITY = "spb"

DB_NAME = "db_wiki_subway"
FILENAME = f"{DB_NAME}_{TARGET_CITY}"
HTML_OUT = True
CSV_OUT = True
DEBUG = False

METRO_LISTS = {
    "spb":    {"lang": "ru", "page": "Список_станций_Петербургского_метрополитена"},
    "moscow": {"lang": "ru", "page": "Список_станций_Московского_метрополитена"},
    "kazan":  {"lang": "ru", "page": "Список_станций_Казанского_метрополитена"},
    "london": {"lang": "en", "page": "List_of_London_Underground_stations"},
    "newyork":{"lang": "en", "page": "List_of_New_York_City_Subway_stations"},
    "tokyo":  {"lang": "en", "page": "List_of_Tokyo_Metro_stations"},
}
KEYWORDS = {
    "ru": "станци",
    "en": "statio"
}
U_EMAIL     = "v.aleksandrovsky@gmail.com"
U_ENDPOINT  = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
U_USERAGENT = f"OSM Subway ({U_EMAIL})"
U_TIMEOUT   = 60


def build_wiki_subway_db(city_key):
    print(f"Start\nbuild_wiki_subway_db\nfor {city_key}")
    city_config = METRO_LISTS.get(city_key)
    page_title = city_config["page"]
    page_lang = city_config["lang"]
    
    if not page_title:
        return []

    headers = {"User-Agent": f"GlobalSubwayLocalBuilder/7.0 ({U_EMAIL}) PythonRequests"}
    API_URL = f"https://{page_lang}.wikipedia.org/w/api.php"

    # Block 1 - 
    # Задача вытянуть из контента статьи wiki ТОЛЬКО ссылки
    # но исключить ряд ссылок некоторых блоков

    reference_list = set()
    exclude_sections = {"External_links","References","Notes","See_also"}

    output_blocks = []
    url = f"https://{page_lang}.wikipedia.org/wiki/{page_title.replace(' ', '_')}"

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        root_container = soup.find(id="mw-content-text")

        if root_container is None:
            print("Error: mw-content-text not found")
            return []

        sections = root_container.find_all("section")

        for idx, section in enumerate(sections):

            section_id = section.get("aria-labelledby")
            if not section_id:
                section_id = f"Section_{idx}"
            else:
                section_id = section_id.strip()

            if section_id in exclude_sections:
                continue

            clean_links = []
            seen = set()

            for a_tag in section.find_all("a", href=True):

                td_parent = a_tag.find_parent("td")
                if td_parent:
                    table_parent = td_parent.find_parent("table")
                    if table_parent:
                        headers_list = []
                        for th in table_parent.find_all("th"):
                            th_text = str(th.get_text(" ", strip=True)).lower()
                            headers_list.append(th_text)
                        
                        exclude_col_indexes = []
                        for c_idx, h_text in enumerate(headers_list):
                            if "see also" in h_text or h_text == "also":
                                exclude_col_indexes.append(c_idx)
                        
                        if exclude_col_indexes:
                            tr_parent = td_parent.find_parent("tr")
                            if tr_parent:
                                current_td_index = 0
                                for td in tr_parent.find_all("td", recursive=False):
                                    if td == td_parent:
                                        break
                                    current_td_index += int(td.get("colspan", 1))
                                
                                if current_td_index in exclude_col_indexes:
                                    continue


                href = a_tag["href"].strip()
                if href.startswith("./wiki/"):
                    href = href[1:]
                elif href.startswith(f"https://{page_lang}.wikipedia.org/wiki/"):
                    href = href[len(f"https://{page_lang}.wikipedia.org"):]
                elif not href.startswith("/wiki/"):
                    continue

                raw_title = href[len("/wiki/"):].split("#", 1)[0]

                if not raw_title:
                    continue

                wiki_title = unquote(raw_title).replace("_", " ")
                if ":" in wiki_title:
                    continue

                link_text = a_tag.get_text(" ", strip=True)

                if not link_text or wiki_title in seen:
                    continue

                seen.add(wiki_title)
                reference_list.add(raw_title)

                clean_links.append(
                    f'  <a href="/wiki/{raw_title}">{link_text}</a>'
                )

            if clean_links and DEBUG:
                output_blocks.append(
                    f'<div id="{section_id}">\n'
                    + "\n".join(clean_links)
                    + "\n</div>"
                )

        ultra_clean_html = "\n\n".join(output_blocks)

        if DEBUG:
            print(f"B1: finded links: {len(reference_list)}")

        if not reference_list:
            print("B1: links not found")
            return []

        print(ultra_clean_html)

    except Exception as e:
        print(f"B1: Error {e}")
        return []
    
    if DEBUG: 
        pass 
    print("Length reference_list",len(list(reference_list)))

    # Блок 2 - пройтись по созданному списку ссылок и 
    # создать необходиму таблицу
    clean_stations = {}
    raw_titles_list = [unquote(t).replace('_', ' ') for t in reference_list]
    chunk_size = 10
    chunks = [raw_titles_list[i:i + chunk_size] for i in range(0, len(raw_titles_list), chunk_size)]

    try:
        
        for chunk in chunks:
            print(f"Send chunks fr {len(chunk)} elems... Current DB Size: {len(clean_stations)}")
            titles_string = "|".join(chunk)

            payload = {
                "action": "query",
                "titles": titles_string,  
                "prop": "coordinates|pageprops",
                "format": "json"
            }
            
            response = requests.post(API_URL, data=payload, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            for page_id, page_info in pages.items():
                if int(page_id) < 0:
                    continue
                    
                title = page_info.get("title")
                special_word = KEYWORDS.get(page_lang)
                if special_word and special_word not in title.lower():
                    continue

                coords_list = page_info.get("coordinates", [])
                props = page_info.get("pageprops", {})
                main_coord = None
            
                if coords_list:
                    if isinstance(coords_list, list) and len(coords_list) > 0:
                        main_coord = coords_list[0]
                    elif isinstance(coords_list, dict):
                        main_coord = coords_list
                else:
                    
                    infobox_coords_str = props.get("coordinates", "")
                    if infobox_coords_str:
                        lat_match = re.search(r'latitude=(-?\d+\.\d+)', infobox_coords_str)
                        lon_match = re.search(r'longitude=(-?\d+\.\d+)', infobox_coords_str)
                        if lat_match and lon_match:
                            main_coord = {
                                "lat": float(lat_match.group(1)),
                                "lon": float(lon_match.group(1))
                            }

                if not main_coord:
                    continue

                clean_name = title.split(" (")[0]
                raw_name = title.replace(' ', '_')
                wiki_url = f"https://{page_lang}.wikipedia.org/wiki/{raw_name}"
                wikidata_id = props.get("wikibase_item", "")
                clean_stations[title] = {
                    "name": clean_name,
                    "lat": round(main_coord.get("lat", 0), 6),
                    "lon": round(main_coord.get("lon", 0), 6),
                    #"pageid": int(page_id),
                    "wikidata": wikidata_id, 
                    "wiki_url": wiki_url
                }

    except Exception as e:
        print(f"Error on collects: {e}")
        return []

    result_list = list(clean_stations.values())
    result_list.sort(key=lambda x: x["name"])
    return result_list



result = build_wiki_subway_db(TARGET_CITY)




if result:
    wikidata_ids = [station["wikidata"] for station in result if station.get("wikidata")]
    osm_filters = []
    for q_id in wikidata_ids:
        osm_filters.append(f'  node["wikidata"="{q_id}"];')

    filters_string = "\n".join(osm_filters)
    
    query = f"""
    (
    {filters_string}
    );
    out;
    """


    api = overpass.API(
        user_agent=U_USERAGENT, 
        timeout=U_TIMEOUT, 
        **({"endpoint": U_ENDPOINT} if U_ENDPOINT else {})
    )
    response = api.get(query, responseformat="json")

    #print("RESP TYPE:", type(response))
    #print("KEYS:", list(response.keys()) if isinstance(response, dict) else "Не словарь")
    #print("FIRST:", response.get("elements", [{}])[0] if "elements" in response else response.get("features", [{}])[0])

    if response and "elements" in response:
        osm_elements = response.get("elements", [])
        osm_mapping = {}
        
        for element in osm_elements:
            tags = element.get("tags", {})
            q_id = tags.get("wikidata")
            
            if q_id:
                name_en_osm = tags.get("name:en", "").strip()
                osm_id_num = element.get("id")
                
                osm_mapping[q_id] = {
                    "name_en": name_en_osm,
                    "osm_id": osm_id_num
                }

        for station in result:
            station_q_id = station.get("wikidata")
            
            if station_q_id in osm_mapping:
                osm_data = osm_mapping[station_q_id]
                station["name_en"] = osm_data["name_en"]
                station["osm_id"] = osm_data["osm_id"]
            else:
                station["name_en"] = ""
                station["osm_id"] = ""

        print(f"Данные OSM успешно вмержены в result для {len(osm_mapping)} станций.")



    city_config = METRO_LISTS.get(TARGET_CITY)
    page_title = city_config["page"]
    page_lang = city_config["lang"]

    output_file = f"{FILENAME}_{page_lang}.json"
    # "utf-8-sig", чтобы продукты Microsoft видели кодировку
    with open(output_file, "w", encoding="utf-8-sig") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"succes! Total: {len(result)}: {output_file}")

    if CSV_OUT and result:
        csv_file = f"{FILENAME}_{page_lang}.csv"
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
            fieldnames = list(result[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=",")
            writer.writeheader()
            for station in result:
                writer.writerow(station)
                
        print(f"csv generated: {csv_file}")

    if HTML_OUT:
        html_file = f"{FILENAME}_{page_lang}.html"
        target_page = f"https://{page_lang}.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        html_content = [
            "<!DOCTYPE html><html><head><meta charset='utf-8'>",
            f"<title>{html_file}</title>",
            "<style>body{font-family:sans-serif;margin:20px;}ul{line-height:1.6;}</style>",
            f"</head><body><h1>{TARGET_CITY} | grab stations: {len(result)}</h1><p>Source page: <a href='{target_page}'>{target_page}</a></p> <ul>"
        ]
        
        for station in result:
            name = station["name"]
            url = station["wiki_url"]
            lat = station["lat"]
            lon = station["lon"]
            html_content.append(f"<li><a href='{url}' target='_blank'>{name}</a> / lat-lon: {lat},{lon}</li>")
        
        html_content.append("</ul></body></html>")
        
        with open(html_file, "w", encoding="utf-8") as f:
            f.write("\n".join(html_content))
        print(f"html generated: {html_file}")

    enddebug = False
    if enddebug:
        station_names = [station["name"] for station in result]
        print(", ".join(station_names))