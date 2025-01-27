import sqlite3
import pandas as pd
import os
from typing import List, Dict

class AirConditionerDB:
    def __init__(self, db_path: str = "aircond.db"):
        # 冷氣空調資料庫
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
    
    def find_by_area(self, area: float, brand: str = None) -> pd.DataFrame:
        """根據坪數和品牌查詢適合的冷氣"""
        if brand:
            query = """
            SELECT 
                brand as 品牌,
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
            AND brand = ?
            ORDER BY price ASC
            """
            df = pd.read_sql_query(query, self.conn, params=(area, area, brand))
        else:
            query = """
            SELECT 
                brand as 品牌,
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
            ORDER BY brand, price ASC
            """
            df = pd.read_sql_query(query, self.conn, params=(area, area))
        return df
    
    def find_by_price_range(self, min_price: int, max_price: int, brand: str = None) -> pd.DataFrame:
        """根據價格範圍和品牌查詢冷氣"""
        if brand:
            query = """
            SELECT 
                brand as 品牌,
                model_number as 型號,
                series_name as 系列,
                type as 類型,
                suitable_area_min || '~' || suitable_area_max || '坪' as 適用坪數,
                price as 價格,
                energy_efficiency_rating as 能源效率
            FROM air_conditioners
            WHERE price BETWEEN ? AND ?
            AND brand = ?
            ORDER BY price ASC
            """
            df = pd.read_sql_query(query, self.conn, params=(min_price, max_price, brand))
        else:
            query = """
            SELECT 
                brand as 品牌,
                model_number as 型號,
                series_name as 系列,
                type as 類型,
                suitable_area_min || '~' || suitable_area_max || '坪' as 適用坪數,
                price as 價格,
                energy_efficiency_rating as 能源效率
            FROM air_conditioners
            WHERE price BETWEEN ? AND ?
            ORDER BY brand, price ASC
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
        """計算所需冷氣能力"""
        # 基本冷氣能力計算 (每坪約 0.8 kW)
        base_capacity = area * 0.8
        
        # 根據房間高度調整
        if height > 2.8:
            base_capacity *= (height / 2.8)
        
        # 根據房間類型調整
        type_factors = {
            '一般': 1.0,
            '廚房': 1.2,
            '電腦室': 1.3
        }
        base_capacity *= type_factors.get(room_type, 1.0)
        
        # 根據朝向調整
        direction_factors = {
            '一般': 1.0,
            '東西向': 1.1,
            '南向': 1.15
        }
        base_capacity *= direction_factors.get(direction, 1.0)
        
        # 如果有大面積窗戶，增加 10%
        if windows:
            base_capacity *= 1.1
        
        return round(base_capacity, 2)

    def suggest_ac_by_calculation(self, capacity: float) -> pd.DataFrame:
        """根據計算的冷氣能力建議機型"""
        query = """
        SELECT 
            brand as 品牌,
            model_number as 型號,
            series_name as 系列,
            type as 類型,
            cooling_capacity as 冷氣能力,
            suitable_area_min || '~' || suitable_area_max || '坪' as 適用坪數,
            price as 價格,
            energy_efficiency_rating as 能源效率,
            features as 特點
        FROM air_conditioners
        WHERE cooling_capacity >= ?
        ORDER BY cooling_capacity ASC, price ASC
        LIMIT 3
        """
        
        df = pd.read_sql_query(query, self.conn, params=(capacity,))
        return df 