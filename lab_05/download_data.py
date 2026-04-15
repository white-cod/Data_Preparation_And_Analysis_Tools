import os
import urllib.request
import datetime
import glob

os.makedirs('data', exist_ok=True)

def download_noaa_data():
    base_url = "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={}&year1=1981&year2=2024&type=Mean"
    
    for province_id in range(1, 28):
        existing_files = glob.glob(f'data/vhi_id_{province_id}_*.csv')
        if existing_files:
            print(f"Файл для області {province_id} вже існує. Пропускаємо.")
            continue
            
        url = base_url.format(province_id)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/vhi_id_{province_id}_{timestamp}.csv"
        
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read().decode('utf-8')
                
            lines = html.split('\n')
            clean_data = []
            for line in lines:
                if not line.startswith("<") and not line.startswith("</") and line.strip() != "":
                    clean_data.append(line.replace(', ', ','))
            
            with open(filename, 'w') as f:
                f.write('\n'.join(clean_data))
            print(f"Завантажено: {filename}")
        except Exception as e:
            print(f"Помилка завантаження {province_id}: {e}")

if __name__ == "__main__":
    download_noaa_data()