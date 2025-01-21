import sqlite3
from typing import List, Dict
import pandas as pd
import os

class AirConditionerDB:
    def __init__(self, db_path: str = "daikin.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """連接到資料庫並初始化表格"""
        db_exists = os.path.exists(self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        if not db_exists:
            self.initialize_database()
    
    def initialize_database(self):
        """初始化資料庫表格和資料"""
        try:
            with open('init_db.sql', 'r', encoding='utf-8') as file:
                sql_script = file.read()
                self.cursor.executescript(sql_script)
                self.conn.commit()
        except Exception as e:
            print(f"初始化資料庫時發生錯誤: {str(e)}")
            raise
    
    def close(self):
        """關閉資料庫連接"""
        if self.conn:
            self.conn.close()
    
    def find_by_area(self, area: float) -> pd.DataFrame:
        """根據坪數查詢適合的冷氣"""
        query = """
        SELECT 
            model_number as 型號,
            series_name as 系列,
            type as 類型,
            cooling_capacity as 冷氣能力,
            suitable_area_min || '~' || suitable_area_max || '坪' as 適用坪數,
            price as 價格,
            energy_efficiency_rating as 能源效率,
            features as 特點
        FROM air_conditioners
        WHERE suitable_area_min <= ? AND suitable_area_max >= ?
        ORDER BY price ASC
        """
        
        df = pd.read_sql_query(query, self.conn, params=(area, area))
        return df
    
    def find_by_price_range(self, min_price: int, max_price: int) -> pd.DataFrame:
        """根據價格範圍查詢冷氣"""
        query = """
        SELECT 
            model_number as 型號,
            series_name as 系列,
            type as 類型,
            suitable_area_min || '~' || suitable_area_max || '坪' as 適用坪數,
            price as 價格,
            energy_efficiency_rating as 能源效率
        FROM air_conditioners
        WHERE price BETWEEN ? AND ?
        ORDER BY price ASC
        """
        
        df = pd.read_sql_query(query, self.conn, params=(min_price, max_price))
        return df
    
    def get_series_info(self) -> pd.DataFrame:
        """獲取所有系列的特點說明"""
        query = """
        SELECT 
            series_name as 系列名稱,
            feature_description as 系列特點
        FROM series_features
        """
        
        df = pd.read_sql_query(query, self.conn)
        return df

    def calculate_cooling_capacity(self, area: float, height: float = 2.8, 
                                 room_type: str = '一般', direction: str = '一般',
                                 windows: bool = False) -> float:
        """計算空間所需冷氣能力
        
        參數:
            area: float - 空間坪數
            height: float - 天花板高度(公尺)，預設2.8公尺
            room_type: str - 空間類型（一般/廚房/電腦室）
            direction: str - 朝向（一般/東西向/南向）
            windows: bool - 是否有大面積窗戶
        
        回傳:
            float - 建議的冷氣能力(kW)
        """
        # 基本計算：1坪約需要0.4~0.6kW
        base_capacity = area * 0.5
        
        # 天花板高度調整
        if height > 2.8:
            base_capacity *= (height / 2.8)
        
        # 空間類型調整
        type_multiplier = {
            '一般': 1.0,
            '廚房': 1.2,  # 廚房需要較大冷氣能力
            '電腦室': 1.3  # 電腦室有較多熱源
        }
        base_capacity *= type_multiplier.get(room_type, 1.0)
        
        # 朝向調整
        direction_multiplier = {
            '一般': 1.0,
            '東西向': 1.2,  # 東西向日照較強
            '南向': 1.1     # 南向日照較多
        }
        base_capacity *= direction_multiplier.get(direction, 1.0)
        
        # 窗戶調整
        if windows:
            base_capacity *= 1.1  # 大面積窗戶增加熱負荷
        
        return round(base_capacity, 1)

    def suggest_ac_by_calculation(self, cooling_capacity: float) -> pd.DataFrame:
        """根據計算的冷氣能力建議適合的機型"""
        query = """
        SELECT 
            model_number as 型號,
            series_name as 系列,
            type as 類型,
            cooling_capacity as 冷氣能力,
            suitable_area_min || '~' || suitable_area_max || '坪' as 適用坪數,
            price as 價格,
            energy_efficiency_rating as 能源效率,
            features as 特點,
            (cooling_capacity - ?) as 能力差異
        FROM air_conditioners
        WHERE cooling_capacity >= ?  -- 確保冷氣能力大於或等於需求
        ORDER BY 能力差異 ASC       -- 選擇最接近但大於需求的型號
        LIMIT 5
        """
        
        df = pd.read_sql_query(query, self.conn, 
                              params=(cooling_capacity, cooling_capacity))
        
        if len(df) == 0:  # 如果沒有找到大於的型號，就找最大容量的型號
            query = """
            SELECT 
                model_number as 型號,
                series_name as 系列,
                type as 類型,
                cooling_capacity as 冷氣能力,
                suitable_area_min || '~' || suitable_area_max || '坪' as 適用坪數,
                price as 價格,
                energy_efficiency_rating as 能源效率,
                features as 特點
            FROM air_conditioners
            ORDER BY cooling_capacity DESC
            LIMIT 1
            """
            df = pd.read_sql_query(query, self.conn)
            print("\n注意：所需冷氣能力超過單機最大容量，建議考慮安裝多台或選擇其他冷氣類型")
        
        return df.drop('能力差異', axis=1) if '能力差異' in df.columns else df

def main():
    try:
        # 如果存在舊的資料庫檔案，先刪除它
        if os.path.exists("daikin.db"):
            os.remove("daikin.db")
            
        # 創建資料庫實例
        db = AirConditionerDB()
        db.connect()
        
        while True:
            print("\n=== 大金冷氣查詢系統 ===")
            print("1. 根據坪數查詢")
            print("2. 根據價格範圍查詢")
            print("3. 查看系列說明")
            print("4. 精確計算冷氣能力")
            print("5. 退出")
            
            choice = input("請選擇功能 (1-5): ")
            
            if choice == "1":
                area = float(input("請輸入坪數: "))
                result = db.find_by_area(area)
                if len(result) > 0:
                    print("\n適合的冷氣型號：")
                    print(result.to_string(index=False))
                else:
                    print("沒有找到適合的型號")
                    
            elif choice == "2":
                min_price = int(input("請輸入最低價格: "))
                max_price = int(input("請輸入最高價格: "))
                result = db.find_by_price_range(min_price, max_price)
                if len(result) > 0:
                    print("\n價格範圍內的冷氣：")
                    print(result.to_string(index=False))
                else:
                    print("沒有找到符合價格範圍的型號")
                    
            elif choice == "3":
                result = db.get_series_info()
                print("\n系列說明：")
                print(result.to_string(index=False))
                
            elif choice == "4":
                area = float(input("請輸入空間坪數: "))
                height = float(input("請輸入天花板高度(公尺，預設2.8): ") or 2.8)
                
                print("\n空間類型：")
                print("1. 一般")
                print("2. 廚房")
                print("3. 電腦室")
                room_type = input("請選擇空間類型 (1-3): ")
                room_type = {'1': '一般', '2': '廚房', '3': '電腦室'}.get(room_type, '一般')
                
                print("\n空間朝向：")
                print("1. 一般")
                print("2. 東西向")
                print("3. 南向")
                direction = input("請選擇空間朝向 (1-3): ")
                direction = {'1': '一般', '2': '東西向', '3': '南向'}.get(direction, '一般')
                
                windows = input("是否有大面積窗戶？(Y/N): ").upper() == 'Y'
                
                capacity = db.calculate_cooling_capacity(
                    area, height, room_type, direction, windows
                )
                print(f"\n計算結果：建議冷氣能力為 {capacity}kW")
                
                result = db.suggest_ac_by_calculation(capacity)
                if len(result) > 0:
                    print("\n建議的冷氣型號：")
                    print(result.to_string(index=False))
                else:
                    print("沒有找到完全符合的型號")
                    
            elif choice == "5":
                break
                
            else:
                print("無效的選擇，請重試")
        
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 