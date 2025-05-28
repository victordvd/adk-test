import requests
 
# YouBike2.0 臺北市即時資訊 API
API_URL = (
    "https://tcgbusfs.blob.core.windows.net/"
    "dotapp/youbike/v2/youbike_immediate.json"
)
 
def get_youbike_locations_in_taipei_city():
    """
    取得臺北市 YouBike 的所有地點.
 
    Returns:
        dict: A dictionary containing a list of youbike's location.
        with a 'status' key ('success' or 'error') and a 'locations' key with a list of youbike locations, or an 'error_message' if an error occurred.
    """
    try:
        resp = requests.get(API_URL, timeout=5)
        resp.raise_for_status()
        stations = resp.json()
        return {'status':'success', 'locations':"📋 可查詢之場站清單：\n"+','.join([s['sna'][11:] for s in stations])}
    except requests.RequestException as e:
        return  {'status':'error', 'error_message':f'❌ 無法取得資料: {e}'}
 
 
def get_youbike_info(location:str):
    """
    取得台灣臺北市特定 YouBike自行車站的即時資訊
 
    Parameters:
        location(str): youbike車站的中文或英文名稱
       
    Returns:
        str: 場站資訊的字串;若無法取得資料或找不到符合的場站，則回傳錯誤訊息.
    """
    try:
        resp = requests.get(API_URL, timeout=5)
        resp.raise_for_status()
        stations = resp.json()
    except requests.RequestException as e:
       return f"❌ 無法取得資料: {e}"
 
    # 過濾場站（精確比對代號或名稱）
    matched = [
        s for s in stations
        if location == s.get('sno')
        or location == s.get('sna')[11:]
        or location.lower() == s.get('snaen', '').lower()
    ]
    if not matched:
        return f"🔍 找不到符合「{location}」的場站。"
       
 
    # 列印每個符合場站的詳細資訊
    rs = []
    for s in matched:
        rs.append("————————————————————————————————————")
        rs.append(f"🏷️ 場站代號：{s['sno']}")
        rs.append(f"🚲 場站名稱：{s['sna']} / {s.get('snaen')}")
        rs.append(f"📍 區域：{s['sarea']} / {s.get('sareaen')}")
        total = s.get('tot') or s.get('total')
        rent  = s.get('sbi') or s.get('available_rent_bikes')
        back  = s.get('bemp') or s.get('available_return_bikes')
        rs.append(f"🔋 總車格數：{total}")
        rs.append(f"🚲 可借車數：{rent}")
        rs.append(f"🈳 空位數量：{back}")
        rs.append(f"⏱️ 更新時間：{s.get('mday')}")
        rs.append(f"📍 地址：{s.get('ar')} ({s.get('aren')})")
        # rs.append(f"🌐 座標：({s.get('lat')}, {s.get('lng')})")
        rs.append("————————————————————————————————————")
    return "\n".join(rs)
 
 
# 查詢站點代號為「YouBike站點代號」的即時資訊
# print(get_youbike_info("500119092"))
# print(get_youbike_info("臺大管理學院一館"))
# print(get_youbike_locations_in_taipei_city())
 