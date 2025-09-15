import ee
import requests

def initialize_gee():
    """認証と初期化。ローカル認証が必要な場合はee.Authenticate()を使う。"""
    try:
        ee.Initialize()
    except Exception:
        ee.Authenticate()
        ee.Initialize()

def get_ndvi_image(lat, lon, start_date, end_date, out_path):
    """
    指定座標・期間でNDVI画像を生成し、ファイル保存する。
    Args:
        lat (float): 緯度
        lon (float): 経度
        start_date (str): 取得開始日（YYYY-MM-DD）
        end_date (str): 取得終了日（YYYY-MM-DD）
        out_path (str): 保存先ファイルパス
    Returns:
        out_path (str): 保存した画像ファイルパス
    """
    # Sentinel-2画像コレクション取得
    point = ee.Geometry.Point([lon, lat])
    collection = ee.ImageCollection('COPERNICUS/S2') \
        .filterBounds(point) \
        .filterDate(start_date, end_date) \
        .sort('CLOUD_COVER')
    image = collection.first()
    # NDVI計算
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    # 可視化パラメータ
    vis_params = {'min': 0, 'max': 1, 'palette': ['blue', 'white', 'green']}
    # 画像をエクスポート
    url = ndvi.getThumbURL({'region': point.buffer(10000).bounds().getInfo(), 'dimensions': 512, 'format': 'png', **vis_params})
    # 画像ダウンロード
    r = requests.get(url)
    with open(out_path, 'wb') as f:
        f.write(r.content)
    return out_path

if __name__ == "__main__":
    # サンプル座標（東京駅付近）
    lat = 35.681236
    lon = 139.767125
    start_date = "2023-08-01"
    end_date = "2023-08-31"
    out_path = "ndvi_sample.png"
    print("GEE認証・初期化中...")
    initialize_gee()
    print("NDVI画像生成中...")
    result = get_ndvi_image(lat, lon, start_date, end_date, out_path)
    print(f"画像保存先: {result}")