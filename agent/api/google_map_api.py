
GOOGLE_MAP_API_KEY = 'AIzaSyAop5n-F6rhtMIEuYXjX_whgS8RdZmjc00'

def build_map_html(location:str):
    html = f'''
    <div>
        <iframe
        width="450"
        height="250"
        frameborder="0" style="border:0"
        referrerpolicy="no-referrer-when-downgrade"
        src="https://www.google.com/maps/embed/v1/place?key={GOOGLE_MAP_API_KEY}&q={location}"
        allowfullscreen>
        </iframe>
    </div>'''

    return html


if __name__ == "__main__":
        print(build_map_html('台灣大學'))