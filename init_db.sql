-- 創建表格
CREATE TABLE IF NOT EXISTS air_conditioners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_number TEXT NOT NULL,
    series_name TEXT NOT NULL,
    type TEXT NOT NULL,
    cooling_capacity DECIMAL(5,2) NOT NULL,
    heating_capacity DECIMAL(5,2),
    suitable_area_min INTEGER,
    suitable_area_max INTEGER,
    energy_efficiency_rating TEXT,
    price INTEGER,
    features TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS series_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_name TEXT NOT NULL,
    feature_description TEXT NOT NULL
);

-- 插入冷氣型號資料
INSERT INTO air_conditioners (
    model_number, series_name, type, cooling_capacity, 
    heating_capacity, suitable_area_min, suitable_area_max, 
    energy_efficiency_rating, price, features
) VALUES 
-- 大關系列
('RXM71SVLT/FTXM71SVLT', '大關系列', '分離式', 7.1, 
 8.5, 12, 15, '1級', 76000,
 'PM2.5過濾、閃流除菌、智慧節能、3D氣流、除濕運轉'),

('RXM50SVLT/FTXM50SVLT', '大關系列', '分離式', 5.0,
 6.0, 8, 11, '1級', 52900,
 'PM2.5過濾、閃流除菌、智慧節能、3D氣流、除濕運轉'),

-- 橫綱系列
('RXM41SVLT/FTXM41SVLT', '橫綱系列', '分離式', 4.1,
 5.0, 6, 9, '1級', 45900,
 'PM2.5過濾、智慧節能、除濕運轉'),

('RXM36SVLT/FTXM36SVLT', '橫綱系列', '分離式', 3.6,
 4.2, 5, 8, '1級', 39900,
 'PM2.5過濾、智慧節能、除濕運轉'),

-- 經典系列
('RXP20HVLT/FTXP20HVLT', '經典系列', '分離式', 2.0,
 2.7, 3, 5, '2級', 25900,
 '智慧節能、除濕運轉'),

-- 吊隱式系列
('RZAG35LVTG/FBA35ALVTG', '吊隱式系列', '吊隱式', 3.5,
 4.0, 5, 8, '1級', 68000,
 'DC變頻、濾網防塵網、可調式風向、高效節能、靜音運轉'),

('RZAG50LVTG/FBA50ALVTG', '吊隱式系列', '吊隱式', 5.0,
 6.0, 8, 11, '1級', 82000,
 'DC變頻、濾網防塵網、可調式風向、高效節能、靜音運轉'),

-- 超薄型吊隱式
('RZF25CV2S/FDBNQ25MV1', '超薄型吊隱式系列', '吊隱式', 2.5,
 3.2, 4, 6, '2級', 55000,
 '超薄機身、易安裝、低噪音運轉、簡易維護'),

-- 大金鎖吊隱式系列
('RZA71LVTG/FHA71AVMG', '大金鎖吊隱式系列', '吊隱式', 7.1,
 8.0, 12, 15, '1級', 98000,
 'DC變頻、四方吹、自動擺風、防霉濾網、智慧節能、靜音運轉'),

('RZA50LVTG/FHA50AVMG', '大金鎖吊隱式系列', '吊隱式', 5.0,
 6.0, 8, 11, '1級', 85000,
 'DC變頻、四方吹、自動擺風、防霉濾網、智慧節能、靜音運轉'),

-- 大金鎖超薄吊隱式系列
('RZF60DVM/FDPQ60CVMG', '大金鎖超薄吊隱式系列', '吊隱式', 6.0,
 7.0, 10, 13, '2級', 88000,
 '超薄設計、四方吹、自動擺風、防霉濾網、簡易安裝維護');

-- 插入系列特點
INSERT INTO series_features (series_name, feature_description) VALUES 
('大關系列', '頂級旗艦機種，搭載最完整的空氣清淨功能，適合追求最佳空氣品質的用戶'),
('橫綱系列', '高性價比的中階機種，具備基本的空氣清淨功能，適合一般家庭使用'),
('經典系列', '入門款機種，具備基本製冷功能，適合預算考量的用戶'),
('吊隱式系列', '專業商用機種，適合商辦空間，具備高效能源效率與穩定性能'),
('超薄型吊隱式系列', '適合天花板空間有限的場所，安裝便利，維護簡單'),
('大金鎖吊隱式系列', '專業商用機種，搭載四方吹技術，適合大型辦公空間與商用場所'),
('大金鎖超薄吊隱式系列', '超薄型設計，適合天花板淨高受限場所，具備四方吹技術'); 