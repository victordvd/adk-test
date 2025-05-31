GOOGLE_MAP_API_KEY = 'AIzaSyAop5n-F6rhtMIEuYXjX_whgS8RdZmjc00'

def build_map_place_html(location:str)->str:
    """取得特定地點的 Google Map embedding HTML

    Parameters:
        location(str): 地點名稱
        
    Returns:
        str: Google Map embedding HTML
    """
    
    html = f'<div><iframe width="700" height="450" frameborder="0" style="border:0" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps/embed/v1/place?key={GOOGLE_MAP_API_KEY}&q={location}" allowfullscreen></iframe></div>'
    return html


def build_restaurant_search_map_html(query_location:str)->str:
    """搜尋特定地點附近的餐廳並產生 Google Map embedding HTML

    Parameters:
        query_location(str): 搜尋地點
        
    Returns:
        str: Google Map embedding HTML
    """
    
    q = f'餐廳+near+{query_location}'    
    zoom:int=16
    html = f'<div><iframe width="700" height="450" frameborder="0" style="border:0" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps/embed/v1/search?key={GOOGLE_MAP_API_KEY}&zoom={zoom}&q={q}" allowfullscreen></iframe></div>'
    return html


# if __name__ == "__main__":
        # print(build_map_place_html('中正紀念堂 餐廳'))
        # print(build_restaurant_search_map_html('中正紀念堂'))