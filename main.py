import argparse
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request
from xml import etree
import webbrowser

XML_FILE = "artisteAlgerien.xml"


def load_data():
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    return root

def find_artist_by_name(name_query):
    root = load_data()
    results = []
    for artist in root.findall('artiste'):
        name = artist.attrib.get('nom', '')
        if name_query.lower() in name.lower():
            results.append(artist)
    return results

def get_albums_by_artist_id(artist_id):
    root = load_data()
    albums = []
    for album in root.findall('album'):
        ref = album.find('ref-artiste')
        if ref is not None and ref.attrib.get('ref') == artist_id:
            albums.append(album)
    return albums

def display_artist_info(artist):
    print(f"Name: {artist.attrib.get('nom')}")
    print(f"City: {artist.attrib.get('ville')}")
    site = artist.find('site')
    print(f"Website: {site.attrib.get('url') if site is not None else 'N/A'}")
    bio = artist.find('biographie')
    print(f"Biography: {bio.text if bio is not None else 'N/A'}")
    print("\nAlbums:")
    albums = get_albums_by_artist_id(artist.attrib.get('no'))
    for album in albums:
        print(f"  - {album.find('titre').text} ({album.attrib.get('annee')})")
        print("    Tracks:")
        for song in album.find('chansons').findall('chanson'):
            print(f"      • {song.text}")
    print("-" * 30)

def render_xslt():
    dom = etree.parse(XML_FILE)
    xslt = etree.parse(XSLT_FILE)
    transform = etree.XSLT(xslt)
    newdom = transform(dom)
    with open("output.html", "w", encoding='utf-8') as f:
        f.write(str(newdom))
    print("Transformed output written to output.html")
    webbrowser.open("output.html")

def cli_mode():
    name = input("Enter artist name to search: ")
    results = find_artist_by_name(name)
    if not results:
        print("No artist found.")
    else:
        for artist in results:
            display_artist_info(artist)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        name = request.form.get('name')
        results = find_artist_by_name(name)
    return render_template('artist.html', results=results, get_albums=get_albums_by_artist_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Algerian Artists Search App")
    parser.add_argument('--mode', choices=['cli', 'web', 'xslt'], required=True, help="Choose execution mode")
    args = parser.parse_args()

    if args.mode == 'cli':
        cli_mode()
    elif args.mode == 'web':
        app.run(debug=True)
    elif args.mode == 'xslt':
        render_xslt()
