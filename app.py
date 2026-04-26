import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import json
import os
import pickle
import io

# ==================== إعداد الصفحة ====================
st.set_page_config(
    page_title="محلل الأسهم السعودي - الإصدار المتقدم الكامل",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS للتنسيق ====================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    .main-header h1 { color: #a5f3fc; }
    .stock-card {
        background: #1e293b;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-right: 4px solid;
    }
    .gold { border-right-color: #ffd700; }
    .silver { border-right-color: #c0c0c0; }
    .bronze { border-right-color: #cd7f32; }
    .timeframe-card {
        background: #0f172a;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==================== إعدادات ====================
CACHE_DIR = "stock_cache"
DATABASE_FILE = "stock_analysis.db"
STOCKS_DATA_FILE = "stocks_data.json"

for dir_name in [CACHE_DIR]:
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

# ==================== 1. إدارة الأسهم (الرأي الشرعي، القطاع) ====================
def load_stocks_data():
    """تحميل قائمة الأسهم مع الرأي الشرعي والقطاع"""
    default_stocks = {
         # ==================== الطاقة (نقبة) ====================
  "2030": {
    "name": "المصافي",
    "sector": "الطاقة",
    "opinion": "نقية"
  },
  "2381": {
    "name": "الحفر العربية",
    "sector": "الطاقة",
    "opinion": "نقية"
  },
  "4030": {
    "name": "البحري",
    "sector": "الطاقة",
    "opinion": "نقية"
  },
  "4200": {
    "name": "الدريس",
    "sector": "الطاقة",
    "opinion": "نقية"
  },
  "1210": {
    "name": "بي سي اي",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "1301": {
    "name": "أسلاك",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "1321": {
    "name": "أنابيب الشرق",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "1322": {
    "name": "آماك",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2001": {
    "name": "كيمانول",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2020": {
    "name": "سابك للمغذيات الزراعية",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2090": {
    "name": "جبسكو",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2150": {
    "name": "زجاج",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2170": {
    "name": "اللجين",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2180": {
    "name": "فيبكو",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2200": {
    "name": "أنابيب",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2210": {
    "name": "نماء للكيماويات",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2220": {
    "name": "معدنية",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2223": {
    "name": "لوبريف",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2240": {
    "name": "صناعات",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2250": {
    "name": "المجموعة السعودية",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2290": {
    "name": "ينساب",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2310": {
    "name": "سبكيم العالمية",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2330": {
    "name": "المتقدمة",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2350": {
    "name": "كيان السعودية",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "2360": {
    "name": "الفخارية",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3002": {
    "name": "أسمنت نجران",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3003": {
    "name": "أسمنت المدينة",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3004": {
    "name": "أسمنت الشمالية",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3005": {
    "name": "أسمنت أم القرى",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3007": {
    "name": "الواحة",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3010": {
    "name": "أسمنت العربية",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3020": {
    "name": "أسمنت اليمامة",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3030": {
    "name": "أسمنت السعودية",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3040": {
    "name": "أسمنت القصيم",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3080": {
    "name": "أسمنت الشرقية",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "3090": {
    "name": "أسمنت تبوك",
    "sector": "المواد الأساسية",
    "opinion": "نقية"
  },
  "1212": {
    "name": "أسترا الصناعية",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "1214": {
    "name": "شاكر",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "1302": {
    "name": "بوان",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "1303": {
    "name": "الصناعات الكهربائية",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "2040": {
    "name": "الخزف السعودي",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "2110": {
    "name": "الكابلات السعودية",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "2160": {
    "name": "أميانتيت",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "2320": {
    "name": "البابطين",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "2370": {
    "name": "مسكن",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "4110": {
    "name": "باتك",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "4140": {
    "name": "صادرات",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "4142": {
    "name": "كابلات الرياض",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "4143": {
    "name": "تالكو",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "4144": {
    "name": "رؤوم",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "4145": {
    "name": "العبيكان للزجاج",
    "sector": "السلع الرأسمالية",
    "opinion": "نقية"
  },
  "1831": {
    "name": "مهارة",
    "sector": "الخدمات التجارية والمهنية",
    "opinion": "نقية"
  },
  "1832": {
    "name": "صدر",
    "sector": "الخدمات التجارية والمهنية",
    "opinion": "نقية"
  },
  "1833": {
    "name": "الموارد",
    "sector": "الخدمات التجارية والمهنية",
    "opinion": "نقية"
  },
  "1834": {
    "name": "سماسكو",
    "sector": "الخدمات التجارية والمهنية",
    "opinion": "نقية"
  },
  "1835": {
    "name": "تمكين",
    "sector": "الخدمات التجارية والمهنية",
    "opinion": "نقية"
  },
  "4031": {
    "name": "الخدمات الأرضية",
    "sector": "النقل",
    "opinion": "نقية"
  },
  "4040": {
    "name": "سابتكو",
    "sector": "النقل",
    "opinion": "نقية"
  },
  "4260": {
    "name": "بدجت السعودية",
    "sector": "النقل",
    "opinion": "نقية"
  },
  "4261": {
    "name": "ذيب",
    "sector": "النقل",
    "opinion": "نقية"
  },
  "4262": {
    "name": "لومي",
    "sector": "النقل",
    "opinion": "نقية"
  },
  "4264": {
    "name": "ناس",
    "sector": "النقل",
    "opinion": "نقية"
  },
  "2130": {
    "name": "صدق",
    "sector": "السلع طويلة الأجل",
    "opinion": "نقية"
  },
  "2340": {
    "name": "ارتيكس",
    "sector": "السلع طويلة الأجل",
    "opinion": "نقية"
  },
  "4011": {
    "name": "لازوردي",
    "sector": "السلع طويلة الأجل",
    "opinion": "نقية"
  },
  "4012": {
    "name": "الأصيل",
    "sector": "السلع طويلة الأجل",
    "opinion": "نقية"
  },
  "4180": {
    "name": "مجموعة فتيحي",
    "sector": "السلع طويلة الأجل",
    "opinion": "نقية"
  },
  "1810": {
    "name": "سيرا",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "1820": {
    "name": "بان",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "1830": {
    "name": "لجام للرياضة",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "4170": {
    "name": "شمس",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "4290": {
    "name": "الخليج للتدريب",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "4291": {
    "name": "الوطنية للتعليم",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "4292": {
    "name": "عطاء",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "6002": {
    "name": "هرفي للأغذية",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "6012": {
    "name": "ريدان",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "6013": {
    "name": "التطويرية الغذائية",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "6014": {
    "name": "الآمار",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "6016": {
    "name": "برغرايزر",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "نقية"
  },
  "4071": {
    "name": "العربية",
    "sector": "الإعلام والترفيه",
    "opinion": "نقية"
  },
  "4008": {
    "name": "ساكو",
    "sector": "تجزئة السلع الكمالية",
    "opinion": "نقية"
  },
  "4050": {
    "name": "ساسكو",
    "sector": "تجزئة السلع الكمالية",
    "opinion": "نقية"
  },
"4051": {
    "name": "باعظيم",
    "sector": "التجزئة",
    "opinion": "نقية"
  },
"4190": {
    "name": "جرير",
    "sector": "التجزئة",
    "opinion": "نقية"
  },
"4191": {
    "name": "أبو معطي",
    "sector": "التجزئة",
    "opinion": "نقية"
  },
"4192": {
    "name": "السيف غاليري",
    "sector": "التجزئة",
    "opinion": "نقية"
  },
"4193": {
    "name": "نايس ون",
    "sector": "التجزئة",
    "opinion": "نقية"
  },
"4001": {
    "name": "أسواق العثيم",
    "sector": "السلع الاستهلاكية",
    "opinion": "نقية"
  },
"4061": {
    "name": "أنعام القابضة",
    "sector": "السلع الاستهلاكية",
    "opinion": "نقية"
  },
"4160": {
    "name": "ثمار",
    "sector": "السلع الاستهلاكية",
    "opinion": "نقية"
  },
"4161": {
    "name": "بن داود",
    "sector": "السلع الاستهلاكية",
    "opinion": "نقية"
  },
"4162": {
    "name": "المنجم",
    "sector": "السلع الاستهلاكية",
    "opinion": "نقية"
  },
"4163": {
    "name": "الدواء",
    "sector": "السلع الاستهلاكية",
    "opinion": "نقية"
  },
"4164": {
    "name": "النهدي",
    "sector": "السلع الاستهلاكية",
    "opinion": "نقية"
  },
"2100": {
    "name": "وفرة",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"2270": {
    "name": "سدافكو",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"2280": {
    "name": "المراعي",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"2281": {
    "name": "تنمية",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"2282": {
    "name": "نقي",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"2285": {
    "name": "المطاحن العربية",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"2286": {
    "name": "المطاحن الرابعة",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"2287": {
    "name": "إنتاج",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"4080": {
    "name": "سناد القابضة",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"6001": {
    "name": "حلواني إخواني",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"6010": {
    "name": "نادك",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"6020": {
    "name": "جاكو",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"6040": {
    "name": "تبوك الزراعية",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"6070": {
    "name": "الجوف الزراعية",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"6090": {
    "name": "جازادكو",
    "sector": "إنتاج الأغذية",
    "opinion": "نقية"
  },
"4165": {
    "name": "الماجد للعود",
    "sector": "المنتجات المنزلية و الشخصية",
    "opinion": "نقية"
  },
"2230": {
    "name": "الكيميائية",
    "sector": "الرعاية الصحية",
    "opinion": "نقية"
  },
"4004": {
    "name": "دلة الصحية",
    "sector": "الرعاية الصحية",
    "opinion": "نقية"
  },
"4013": {
    "name": "سليمان الحبيب",
    "sector": "الرعاية الصحية",
    "opinion": "نقية"
  },
"4014": {
    "name": "دار المعدات",
    "sector": "الرعاية الصحية",
    "opinion": "نقية"
  },
"4016": {
    "name": "أفالون فارما",
    "sector": "الادوية",
    "opinion": "نقية"
  },
"1182": {
    "name": "أملاك",
    "sector": "الخدمات الملية",
    "opinion": "نقية"
  },
"1183": {
    "name": "سهل",
    "sector": "الخدمات الملية",
    "opinion": "نقية"
  },
"2120": {
    "name": "متطورة",
    "sector": "الخدمات الملية",
    "opinion": "نقية"
  },
"4081": {
    "name": "النايفات",
    "sector": "الخدمات الملية",
    "opinion": "نقية"
  },
"4082": {
    "name": "مرنة",
    "sector": "الخدمات الملية",
    "opinion": "نقية"
  },
"4083": {
    "name": "تسهيل",
    "sector": "الخدمات الملية",
    "opinion": "نقية"
  },
"4130": {
    "name": "درب السعودية",
    "sector": "الخدمات الملية",
    "opinion": "نقية"
  },
"7202": {
    "name": "سلوشنز",
    "sector": "التطبيقات و حدمات التقنية",
    "opinion": "نقية"
  },
"7203": {
    "name": "علم",
    "sector": "التطبيقات و حدمات التقنية",
    "opinion": "نقية"
  },
"7204": {
    "name": "توبي",
    "sector": "التطبيقات و حدمات التقنية",
    "opinion": "نقية"
  },
"7211": {
    "name": "عزم",
    "sector": "التطبيقات و حدمات التقنية",
    "opinion": "نقية"
  },
"7010": {
    "name": "اس تي سي",
    "sector": "الاتصالات",
    "opinion": "نقية"
  },
"7020": {
    "name": "اتحاد الاتصالات",
    "sector": "الاتصالات",
    "opinion": "نقية"
  },
  "7040": {
    "name": "قو للاتصالات",
    "sector": "الاتصالات",
    "opinion": "نقية"
  },
  "2080": {
    "name": "الغاز",
    "sector": "المرافق العامة",
    "opinion": "نقية"
  },
  "2081": {
    "name": "الخريف",
    "sector": "الطاقة",
    "opinion": "نقية"
  },
  "2083": {
    "name": "مرافق",
    "sector": "المرافق العامة",
    "opinion": "نقية"
  },
  "4330": {
    "name": "الرياض ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4331": {
    "name": "الجزيرة ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4333": {
    "name": "تعليم ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4335": {
    "name": "مشاركة ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4336": {
    "name": "ملكية ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4337": {
    "name": "سيكو السعودية ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4339": {
    "name": "دراية ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4340": {
    "name": "الراجحي ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4342": {
    "name": "جدوى ريت السعودية",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4344": {
    "name": "سدكو كابيتال ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4345": {
    "name": "الإنماء ريت للتجزئة",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4346": {
    "name": "ميفك ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4347": {
    "name": "بنيان ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4348": {
    "name": "الخبير ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4349": {
    "name": "الإنماء ريت الفندقي",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "نقية"
  },
  "4090": {
    "name": "طيبة",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4100": {
    "name": "مكة",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4150": {
    "name": "التعمير",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4230": {
    "name": "البحر الأحمر",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4250": {
    "name": "جبل عمر",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4300": {
    "name": "دار الأركان",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4310": {
    "name": "مدينة المعرفة",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4320": {
    "name": "الأندلس",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4321": {
    "name": "سينومي سنترز",
    "sector": "العقارات",
    "opinion": "نقية"
  },
  "4322": {
    "name": "رتال",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4323": {
    "name": "سمو",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4324": {
    "name": "بنان",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  },
  "4325": {
    "name": "مسار",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "نقية"
  }
  "2380": {
    "name": "بترو رابغ",
    "sector": "الطاقة",
    "opinion": "مختلطة"
  },
  "2382": {
    "name": "أديس",
    "sector": "الطاقة",
    "opinion": "مختلطة"
  },
  "1202": {
    "name": "ميكو",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "1211": {
    "name": "معادن",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "1320": {
    "name": "أنابيب السعودية",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "1323": {
    "name": "يو سي آي سي",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "2010": {
    "name": "سابك",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "2060": {
    "name": "التصنيع",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "2300": {
    "name": "صناعة الورق",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "3008": {
    "name": "الكثيري",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "3050": {
    "name": "أسمنت الجنوب",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "3060": {
    "name": "أسمنت ينبع",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "3091": {
    "name": "أسمنت الجوف",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "3092": {
    "name": "أسمنت الرياض",
    "sector": "المواد الأساسية",
    "opinion": "مختلطة"
  },
  "4141": {
    "name": "العمران",
    "sector": "السلع الرأسمالية",
    "opinion": "مختلطة"
  },
  "6004": {
    "name": "كاترون",
    "sector": "الخدمات التجارية والمهنية",
    "opinion": "مختلطة"
  },
  "2190": {
    "name": "سيسكو القابضة",
    "sector": "النقل",
    "opinion": "مختلطة"
  },
  "4263": {
    "name": "سال",
    "sector": "النقل",
    "opinion": "مختلطة"
  },
  "6015": {
    "name": "أمريكانا",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "مختلطة"
  },
  "6018": {
    "name": "الأنذية للرياضة",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "مختلطة"
  },
  "4070": {
    "name": "تهامة",
    "sector": "الإعلام والترفيه",
    "opinion": "مختلطة"
  },
  "4003": {
    "name": "إكسترا",
    "sector": "تجزئة السلع الكمالية",
    "opinion": "مختلطة"
  },
  "4240": {
    "name": "سينومي ريتيل",
    "sector": "تجزئة السلع الكمالية",
    "opinion": "مختلطة"
  },
  "4006": {
    "name": "أسواق المزرعة",
    "sector": "تجزئة وتوزيع السلع الاستهلاكية",
    "opinion": "مختلطة"
  },
  "2050": {
    "name": "مجموعة صافولا",
    "sector": "إنتاج الأغذية",
    "opinion": "مختلطة"
  },
  "2283": {
    "name": "المطاحن الأولى",
    "sector": "إنتاج الأغذية",
    "opinion": "مختلطة"
  },
  "2284": {
    "name": "المطاحن الحديثة",
    "sector": "إنتاج الأغذية",
    "opinion": "مختلطة"
  },
  "2140": {
    "name": "أيان",
    "sector": "الرعاية الصحية",
    "opinion": "مختلطة"
  },
  "4002": {
    "name": "المواساة",
    "sector": "الرعاية الصحية",
    "opinion": "مختلطة"
  },
  "4005": {
    "name": "رعاية",
    "sector": "الرعاية الصحية",
    "opinion": "مختلطة"
  },
  "4007": {
    "name": "الحمادي",
    "sector": "الرعاية الصحية",
    "opinion": "مختلطة"
  },
  "4009": {
    "name": "السعودي الألماني الصحية",
    "sector": "الرعاية الصحية",
    "opinion": "مختلطة"
  },
  "4017": {
    "name": "فقيه الطبية",
    "sector": "الرعاية الصحية",
    "opinion": "مختلطة"
  },
  "4019": {
    "name": "إس إم سي للرعاية الصحية",
    "sector": "الرعاية الصحية",
    "opinion": "مختلطة"
  },
  "2070": {
    "name": "الدوائية",
    "sector": "الأدوية",
    "opinion": "مختلطة"
  },
  "4015": {
    "name": "جمجوم فارما",
    "sector": "الأدوية",
    "opinion": "مختلطة"
  },
  "1111": {
    "name": "مجموعة تداول",
    "sector": "الخدمات المالية",
    "opinion": "مختلطة"
  },
  "7200": {
    "name": "إم آي إس",
    "sector": "التطبيقات وخدمات التقنية",
    "opinion": "مختلطة"
  },
  "7201": {
    "name": "بحر العرب",
    "sector": "التطبيقات وخدمات التقنية",
    "opinion": "مختلطة"
  },
  "7030": {
    "name": "زين السعودية",
    "sector": "الاتصالات",
    "opinion": "مختلطة"
  },
  "2084": {
    "name": "مياهنا",
    "sector": "المرافق العامة",
    "opinion": "مختلطة"
  },
  "5110": {
    "name": "كهرباء السعودية",
    "sector": "المرافق العامة",
    "opinion": "مختلطة"
  },
  "4350": {
    "name": "الاستثمار ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "مختلطة"
  },
  "4020": {
    "name": "العقارية",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "مختلطة"
  },
  "1201": {
    "name": "تكوين",
    "sector": "المواد الأساسية",
    "opinion": "غير متوافقة"
  },
  "1304": {
    "name": "اليمامة للحديد",
    "sector": "المواد الأساسية",
    "opinion": "غير متوافقة"
  },
  "4270": {
    "name": "طباعة وتغليف",
    "sector": "الخدمات التجارية والمهنية",
    "opinion": "غير متوافقة"
  },
  "1213": {
    "name": "نسيج",
    "sector": "السلع طويلة الأجل",
    "opinion": "غير متوافقة"
  },
  "6017": {
    "name": "جاهز",
    "sector": "الخدمات الاستهلاكية",
    "opinion": "غير متوافقة"
  },
  "6050": {
    "name": "الأسماك",
    "sector": "إنتاج الأغذية",
    "opinion": "غير متوافقة"
  },
  "6060": {
    "name": "الشرقية للتنمية",
    "sector": "إنتاج الأغذية",
    "opinion": "غير متوافقة"
  },
  "4018": {
    "name": "الموسى",
    "sector": "الرعاية الصحية",
    "opinion": "غير متوافقة"
  },
  "4084": {
    "name": "دراية",
    "sector": "الخدمات المالية",
    "opinion": "غير متوافقة"
  },
  "2082": {
    "name": "أكوا باور",
    "sector": "المرافق العامة",
    "opinion": "غير متوافقة"
  },
  "4334": {
    "name": "المعذر ريت",
    "sector": "الصناديق العقارية المتداولة",
    "opinion": "غير متوافقة"
  },
  "4220": {
    "name": "إعمار",
    "sector": "إدارة وتطوير العقارات",
    "opinion": "غير متوافقة"
  },
  "4072": {
    "name": "مجموعة إم بي سي",
    "sector": "الإعلام والترفيه",
    "opinion": "غير متوافقة النشاط"
  },
  "4210": {
    "name": "الأبحاث والإعلام",
    "sector": "الإعلام والترفيه",
    "opinion": "غير متوافقة النشاط"
  },
  "4280": {
    "name": "المملكة",
    "sector": "الخدمات المالية",
    "opinion": "غير متوافقة النشاط"
  }
}
    if os.path.exists(STOCKS_DATA_FILE):
        try:
            with open(STOCKS_DATA_FILE, 'r', encoding='utf-8') as f:
                custom = json.load(f)
                default_stocks.update(custom)
        except:
            pass
    return default_stocks

def save_stocks_data(stocks):
    with open(STOCKS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)

def add_stock(symbol, name, sector, opinion):
    stocks = load_stocks_data()
    stocks[symbol.upper()] = {'name': name, 'sector': sector, 'opinion': opinion}
    save_stocks_data(stocks)
    return True

def delete_stock(symbol):
    stocks = load_stocks_data()
    if symbol.upper() in stocks:
        del stocks[symbol.upper()]
        save_stocks_data(stocks)
        return True
    return False

def update_stock(symbol, name, sector, opinion):
    stocks = load_stocks_data()
    if symbol.upper() in stocks:
        stocks[symbol.upper()] = {'name': name, 'sector': sector, 'opinion': opinion}
        save_stocks_data(stocks)
        return True
    return False

# ==================== 2. دوال التحليل الأساسية ====================
def format_symbol(symbol):
    symbol = symbol.strip().upper()
    if '.' in symbol:
        return symbol
    if symbol.isdigit() and len(symbol) >= 4:
        return f"{symbol}.SR"
    return symbol

def get_cached_data(symbol, interval, period):
    cache_file = f"{CACHE_DIR}/{symbol}_{interval}_{period}.pkl"
    if os.path.exists(cache_file):
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_time < timedelta(hours=1):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(interval=interval, period=period)
        if not df.empty:
            with open(cache_file, 'wb') as f:
                pickle.dump(df, f)
        return df
    except:
        return pd.DataFrame()

def calculate_indicators(df):
    df = df.copy()
    if len(df) < 20:
        return df
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    df['BB_mid'] = df['Close'].rolling(20).mean()
    bb_std = df['Close'].rolling(20).std()
    df['BB_upper'] = df['BB_mid'] + (bb_std * 2)
    df['BB_lower'] = df['BB_mid'] - (bb_std * 2)
    return df

# ==================== 3. مؤشرات متقدمة (Ichimoku, Fibonacci, ADX) ====================
def add_advanced_indicators(df):
    df = df.copy()
    if len(df) < 30:
        return df
    
    # ADX
    high = df['High']; low = df['Low']; close = df['Close']
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
    minus_di = abs(100 * (minus_dm.rolling(14).mean() / atr))
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df['ADX'] = dx.rolling(14).mean()
    
    # Ichimoku
    high_9 = df['High'].rolling(9).max()
    low_9 = df['Low'].rolling(9).min()
    df['Ichimoku_Tenkan'] = (high_9 + low_9) / 2
    high_26 = df['High'].rolling(26).max()
    low_26 = df['Low'].rolling(26).min()
    df['Ichimoku_Kijun'] = (high_26 + low_26) / 2
    
    # Fibonacci
    if len(df) >= 50:
        high_52w = df['High'].rolling(52).max()
        low_52w = df['Low'].rolling(52).min()
        diff = high_52w - low_52w
        df['Fib_236'] = low_52w + diff * 0.236
        df['Fib_382'] = low_52w + diff * 0.382
        df['Fib_500'] = low_52w + diff * 0.5
        df['Fib_618'] = low_52w + diff * 0.618
    
    return df

# ==================== 4. تحليل النماذج والفجوات ====================
def detect_gaps(df):
    gaps = []
    if len(df) < 2:
        return gaps
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if last['Open'] > prev['High']:
        gap_size = (last['Open'] - prev['High']) / prev['High'] * 100
        gaps.append(("فجوة صاعدة", f"📈 فجوة صاعدة ({gap_size:.1f}%)", 2))
    elif last['Open'] < prev['Low']:
        gap_size = (prev['Low'] - last['Open']) / prev['Low'] * 100
        gaps.append(("فجوة هابطة", f"📉 فجوة هابطة ({gap_size:.1f}%)", -2))
    return gaps

def detect_price_patterns(df):
    patterns = []
    if len(df) < 50:
        return patterns
    close = df['Close'].values
    peaks = []
    troughs = []
    for i in range(10, len(close) - 10):
        if all(close[i] > close[i-j] for j in range(1, 6)) and all(close[i] > close[i+j] for j in range(1, 6)):
            peaks.append((i, close[i]))
        if all(close[i] < close[i-j] for j in range(1, 6)) and all(close[i] < close[i+j] for j in range(1, 6)):
            troughs.append((i, close[i]))
    if len(peaks) >= 2:
        if abs(peaks[-1][1] - peaks[-2][1]) / peaks[-2][1] < 0.03:
            patterns.append(("قمة مزدوجة", "⚠️ نموذج انعكاس هابط", -2))
    if len(troughs) >= 2:
        if abs(troughs[-1][1] - troughs[-2][1]) / troughs[-2][1] < 0.03:
            patterns.append(("قاع مزدوج", "✅ نموذج انعكاس صاعد", 2))
    return patterns

# ==================== 5. تحليل الشموع اليابانية ====================
def detect_candle_patterns(df):
    patterns = []
    if len(df) < 2:
        return patterns
    last = df.iloc[-1]
    prev = df.iloc[-2]
    body = abs(last['Close'] - last['Open'])
    total_range = last['High'] - last['Low']
    lower_wick = min(last['Close'], last['Open']) - last['Low']
    upper_wick = last['High'] - max(last['Close'], last['Open'])
    
    if total_range > 0 and body / total_range < 0.1:
        patterns.append(("دوجي", "⚠️ عدم حسم", 0))
    if lower_wick > body * 2 and upper_wick < body * 0.5 and last['Close'] > last['Open']:
        patterns.append(("مطرقة", "🔨 انعكاس صاعد - شراء", 2))
    if upper_wick > body * 2 and lower_wick < body * 0.5 and last['Close'] < last['Open']:
        patterns.append(("نجمة شهاب", "⭐ انعكاس هابط - بيع", -2))
    if (last['Close'] > last['Open'] and prev['Close'] < prev['Open'] and
        last['Close'] > prev['Open'] and last['Open'] < prev['Close']):
        patterns.append(("ابتلاع صاعد", "🟢 شراء قوي", 3))
    return patterns

# ==================== 6. أهداف السعر ووقف الخسارة ====================
def calculate_price_targets(df, current_price):
    targets = []
    if len(df) < 20:
        return targets
    last = df.iloc[-1]
    if 'BB_upper' in last and pd.notna(last['BB_upper']):
        targets.append({'level': 'المقاومة (بولينجر)', 'price': round(last['BB_upper'], 2), 'percentage': round((last['BB_upper'] - current_price) / current_price * 100, 1)})
    targets.append({'level': 'هدف 5%', 'price': round(current_price * 1.05, 2), 'percentage': 5.0})
    targets.append({'level': 'هدف 10%', 'price': round(current_price * 1.10, 2), 'percentage': 10.0})
    return targets[:3]

def calculate_stop_loss(df, current_price):
    stop_levels = []
    stop_levels.append({'level': 'وقف 2%', 'price': round(current_price * 0.98, 2), 'percentage': -2.0})
    stop_levels.append({'level': 'وقف 5%', 'price': round(current_price * 0.95, 2), 'percentage': -5.0})
    if len(df) >= 20:
        recent_low = df['Low'].tail(20).min()
        if recent_low < current_price:
            stop_levels.append({'level': 'الدعم', 'price': round(recent_low, 2), 'percentage': round((recent_low - current_price) / current_price * 100, 1)})
    return stop_levels[:3]

def calculate_risk_reward(entry_price, stop_loss_price, target_prices):
    risk = abs(entry_price - stop_loss_price)
    if risk == 0:
        return []
    results = []
    for target in target_prices:
        reward = abs(target['price'] - entry_price)
        ratio = reward / risk
        assessment = 'ممتاز' if ratio >= 2 else ('جيد' if ratio >= 1.5 else 'مقبول')
        results.append({'target': target['level'], 'ratio': round(ratio, 1), 'assessment': assessment})
    return results

def generate_price_prediction(df, current_price, total_score, strong_count):
    if len(df) < 30:
        return {'direction': 'غير واضح', 'confidence': 0}
    last = df.iloc[-1]
    bullish = 0
    bearish = 0
    if 'RSI' in last and last['RSI'] < 30:
        bullish += 2
    if 'MACD' in last and 'MACD_signal' in last and last['MACD'] > last['MACD_signal']:
        bullish += 1
    if total_score >= 65:
        bullish += 1
    if strong_count >= 3:
        bullish += 1
    
    if bullish >= 3:
        return {'direction': 'صاعد', 'confidence': min(90, 50 + bullish * 10), 'target': round(current_price * 1.05, 2)}
    elif bullish >= 2:
        return {'direction': 'صاعد ضعيف', 'confidence': 60, 'target': round(current_price * 1.02, 2)}
    else:
        return {'direction': 'جانبي', 'confidence': 50, 'target': current_price}

def get_trading_recommendation(df, current_price, total_score, strong_count):
    if len(df) < 20:
        return {'action': 'انتظار', 'reason': 'بيانات غير كافية'}
    buy_signals = []
    last = df.iloc[-1]
    if 'RSI' in last and last['RSI'] < 30:
        buy_signals.append(f"RSI منخفض ({last['RSI']:.1f})")
    if 'MACD' in last and 'MACD_signal' in last and last['MACD'] > last['MACD_signal']:
        buy_signals.append("MACD إيجابي")
    if total_score >= 65:
        buy_signals.append(f"قوة عالية ({total_score:.0f})")
    if strong_count >= 3:
        buy_signals.append(f"ظهرت على {strong_count} فترات")
    
    if len(buy_signals) >= 3:
        return {'action': 'شراء قوي', 'reason': ' | '.join(buy_signals[:3])}
    elif len(buy_signals) >= 2:
        return {'action': 'شراء', 'reason': ' | '.join(buy_signals[:2])}
    elif len(buy_signals) == 1:
        return {'action': 'مراقبة', 'reason': buy_signals[0]}
    return {'action': 'انتظار', 'reason': 'لا توجد إشارات'}

def analyze_liquidity(symbol):
    try:
        df = get_cached_data(symbol, '1d', '1mo')
        if df.empty or len(df) < 5:
            return 50, ["بيانات غير كافية"]
        avg_volume = df['Volume'].mean()
        last_volume = df['Volume'].iloc[-1]
        vol_ratio = last_volume / avg_volume if avg_volume > 0 else 1
        score = 50
        reasons = []
        if vol_ratio > 1.5:
            score += 20
            reasons.append(f"حجم مرتفع ({vol_ratio:.1f}x)")
        elif vol_ratio > 1.2:
            score += 10
            reasons.append(f"حجم جيد ({vol_ratio:.1f}x)")
        elif vol_ratio < 0.5:
            score -= 15
            reasons.append(f"حجم منخفض ({vol_ratio:.1f}x)")
        else:
            reasons.append(f"حجم طبيعي ({vol_ratio:.1f}x)")
        return max(0, min(100, score)), reasons
    except:
        return 50, ["لا توجد بيانات"]

def get_fundamental_data(symbol):
    try:
        symbol_f = format_symbol(symbol)
        stock = yf.Ticker(symbol_f)
        info = stock.info
        return {
            'pe_ratio': info.get('trailingPE', 0),
            'pb_ratio': info.get('priceToBook', 0),
            'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
        }
    except:
        return {}

def get_multi_timeframe_data(symbol):
    TIMEFRAMES = {
        '15د': {'interval': '5m', 'period': '5d', 'name': '15 دقيقة'},
        'ساعة': {'interval': '1h', 'period': '30d', 'name': 'ساعة'},
        'يوم': {'interval': '1d', 'period': '3mo', 'name': 'يوم'},
        'اسبوع': {'interval': '1wk', 'period': '6mo', 'name': 'أسبوع'}
    }
    results = {}
    for tf_key, tf_config in TIMEFRAMES.items():
        try:
            df = get_cached_data(symbol, tf_config['interval'], tf_config['period'])
            if not df.empty and len(df) >= 15:
                df = calculate_indicators(df)
                df = add_advanced_indicators(df)
                score = 50
                last = df.iloc[-1]
                if 'RSI' in last:
                    if last['RSI'] < 30:
                        score = 70
                    elif last['RSI'] > 70:
                        score = 30
                    else:
                        score = 50
                results[tf_key] = {
                    'name': tf_config['name'],
                    'score': score,
                    'price': round(last['Close'], 2),
                    'rsi': round(last['RSI'], 1) if 'RSI' in last else 50,
                    'adx': round(last['ADX'], 1) if 'ADX' in last else 0,
                    'ichimoku': f"{last['Ichimoku_Tenkan']:.2f}" if 'Ichimoku_Tenkan' in last else 'N/A',
                    'fib': f"{last['Fib_618']:.2f}" if 'Fib_618' in last else 'N/A',
                    'status': 'قوية' if score >= 60 else ('متوسطة' if score >= 45 else 'ضعيفة')
                }
            else:
                results[tf_key] = {'name': tf_config['name'], 'score': 0, 'status': 'بيانات غير كافية'}
        except:
            results[tf_key] = {'name': tf_config['name'], 'score': 0, 'status': 'خطأ'}
        time.sleep(0.05)
    return results

def calculate_total_strength(timeframe_results):
    scores = []
    strong_timeframes = []
    for tf, data in timeframe_results.items():
        if data.get('score', 0) > 0:
            scores.append(data['score'])
            if data['score'] >= 60:
                strong_timeframes.append(data['name'])
    if not scores:
        return 0, [], 0
    avg_score = sum(scores) / len(scores)
    strong_count = len(strong_timeframes)
    if strong_count >= 3:
        avg_score = min(100, avg_score + 15)
    elif strong_count == 2:
        avg_score = min(100, avg_score + 8)
    return avg_score, strong_timeframes, strong_count

def analyze_single_stock(symbol_input):
    symbol = format_symbol(symbol_input)
    stocks_data = load_stocks_data()
    stock_info = stocks_data.get(symbol_input, {'name': symbol_input, 'sector': 'غير محدد', 'opinion': 'غير محدد'})
    
    timeframe_results = get_multi_timeframe_data(symbol)
    total_score, strong_timeframes, strong_count = calculate_total_strength(timeframe_results)
    liquidity_score, liquidity_reasons = analyze_liquidity(symbol)
    fundamental = get_fundamental_data(symbol)
    
    df_day = get_cached_data(symbol, '1d', '3mo')
    current_price = df_day['Close'].iloc[-1] if not df_day.empty else 0
    
    targets = calculate_price_targets(df_day, current_price) if not df_day.empty else []
    stop_losses = calculate_stop_loss(df_day, current_price) if not df_day.empty else []
    risk_reward = calculate_risk_reward(current_price, stop_losses[0]['price'] if stop_losses else current_price * 0.95, targets) if targets and stop_losses else []
    prediction = generate_price_prediction(df_day, current_price, total_score, strong_count) if not df_day.empty else {'direction': 'غير واضح', 'confidence': 0}
    trading_rec = get_trading_recommendation(df_day, current_price, total_score, strong_count) if not df_day.empty else {'action': 'انتظار', 'reason': 'بيانات غير كافية'}
    
    # تحليل إضافي
    gaps = detect_gaps(df_day) if not df_day.empty else []
    patterns = detect_price_patterns(df_day) if not df_day.empty else []
    candle_patterns = detect_candle_patterns(df_day) if not df_day.empty else []
    
    return {
        'symbol': symbol_input,
        'name': stock_info.get('name', symbol_input),
        'sector': stock_info.get('sector', 'غير محدد'),
        'opinion': stock_info.get('opinion', 'غير محدد'),
        'total_score': total_score,
        'strong_count': strong_count,
        'strong_timeframes': strong_timeframes,
        'timeframes': timeframe_results,
        'liquidity_score': liquidity_score,
        'liquidity_reasons': liquidity_reasons,
        'fundamental': fundamental,
        'current_price': current_price,
        'targets': targets,
        'stop_losses': stop_losses,
        'risk_reward': risk_reward,
        'prediction': prediction,
        'trading_recommendation': trading_rec,
        'gaps': gaps,
        'patterns': patterns,
        'candle_patterns': candle_patterns,
        'recommendation': 'شراء قوي' if strong_count >= 3 else ('شراء' if strong_count >= 2 else 'مراقبة')
    }

def find_best_opportunities(progress_callback=None):
    stocks_data = load_stocks_data()
    results = []
    total = len(stocks_data)
    
    for i, (symbol, info) in enumerate(stocks_data.items(), 1):
        if progress_callback:
            progress_callback(i, total)
        try:
            symbol_f = format_symbol(symbol)
            timeframe_results = get_multi_timeframe_data(symbol_f)
            total_score, strong_timeframes, strong_count = calculate_total_strength(timeframe_results)
            day_data = timeframe_results.get('يوم', {})
            liquidity_score, _ = analyze_liquidity(symbol_f)
            if total_score >= 35:
                results.append({
                    'symbol': symbol,
                    'name': info.get('name', symbol),
                    'sector': info.get('sector', 'غير محدد'),
                    'opinion': info.get('opinion', 'غير محدد'),
                    'total_score': total_score,
                    'strong_count': strong_count,
                    'strong_timeframes': strong_timeframes,
                    'price': day_data.get('price', 0),
                    'rsi': day_data.get('rsi', 0),
                    'adx': day_data.get('adx', 0),
                    'liquidity': liquidity_score,
                    'recommendation': 'شراء قوي' if strong_count >= 3 else ('شراء' if strong_count >= 2 else 'مراقبة')
                })
        except:
            pass
        time.sleep(0.05)
    
    results.sort(key=lambda x: x['total_score'], reverse=True)
    return results[:30]

# ==================== 7. تصدير التقارير ====================
def export_to_csv(results):
    data = []
    for i, r in enumerate(results, 1):
        data.append({
            'الترتيب': i, 'الرمز': r['symbol'], 'الشركة': r['name'],
            'القطاع': r.get('sector', ''), 'الرأي الشرعي': r.get('opinion', ''),
            'السعر': r['price'], 'RSI': r['rsi'], 'القوة': r['total_score'],
            'ADX': r.get('adx', 0), 'الفترات_القوية': r['strong_count'],
            'السيولة': r.get('liquidity', 50), 'التوصية': r['recommendation']
        })
    df = pd.DataFrame(data)
    return df.to_csv(index=False, encoding='utf-8-sig')

def export_single_to_csv(result):
    data = []
    for tf, tf_data in result['timeframes'].items():
        data.append({
            'الفترة': tf_data.get('name', tf),
            'الدرجة': tf_data.get('score', 0),
            'السعر': tf_data.get('price', 0),
            'RSI': tf_data.get('rsi', 0),
            'ADX': tf_data.get('adx', 0),
            'التقييم': tf_data.get('status', '')
        })
    df = pd.DataFrame(data)
    return df.to_csv(index=False, encoding='utf-8-sig')

# ==================== 8. إدارة الأسهم (واجهة) ====================
def stock_management_ui():
    st.subheader("📋 إدارة الأسهم")
    
    tabs = st.tabs(["➕ إضافة سهم", "✏️ تعديل سهم", "🗑️ حذف سهم", "📋 قائمة الأسهم"])
    
    with tabs[0]:
        with st.form("add_stock_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_symbol = st.text_input("رمز السهم", placeholder="مثال: 2222")
                new_name = st.text_input("اسم الشركة", placeholder="مثال: أرامكو السعودية")
            with col2:
                new_sector = st.selectbox("القطاع", ["البنوك", "الطاقة", "البتروكيماويات", "الاتصالات", "التجزئة", "العقار", "التأمين", "المرافق", "النقل", "أخرى"])
                new_opinion = st.selectbox("الرأي الشرعي", ["نقبة", "مختلطة", "غير متوافقة", "غير متوافقة النشاط"])
            submitted = st.form_submit_button("إضافة سهم")
            if submitted and new_symbol and new_name:
                if add_stock(new_symbol, new_name, new_sector, new_opinion):
                    st.success(f"✅ تم إضافة {new_symbol} - {new_name}")
                    st.rerun()
                else:
                    st.error("فشل في الإضافة")
    
    with tabs[1]:
        stocks = load_stocks_data()
        if stocks:
            selected_symbol = st.selectbox("اختر السهم للتعديل", list(stocks.keys()))
            if selected_symbol:
                stock = stocks[selected_symbol]
                with st.form("edit_stock_form"):
                    edit_name = st.text_input("اسم الشركة", value=stock.get('name', ''))
                    edit_sector = st.selectbox("القطاع", ["البنوك", "الطاقة", "البتروكيماويات", "الاتصالات", "التجزئة", "العقار", "التأمين", "المرافق", "النقل", "أخرى"], index=0)
                    edit_opinion = st.selectbox("الرأي الشرعي", ["نقبة", "مختلطة", "غير متوافقة", "غير متوافقة النشاط"], index=0)
                    submitted = st.form_submit_button("تحديث")
                    if submitted and edit_name:
                        if update_stock(selected_symbol, edit_name, edit_sector, edit_opinion):
                            st.success(f"✅ تم تحديث {selected_symbol}")
                            st.rerun()
                        else:
                            st.error("فشل في التحديث")
    
    with tabs[2]:
        stocks = load_stocks_data()
        if stocks:
            delete_symbol = st.selectbox("اختر السهم للحذف", list(stocks.keys()))
            if delete_symbol and st.button("🗑️ حذف", type="primary"):
                if delete_stock(delete_symbol):
                    st.success(f"✅ تم حذف {delete_symbol}")
                    st.rerun()
                else:
                    st.error("فشل في الحذف")
    
    with tabs[3]:
        stocks = load_stocks_data()
        if stocks:
            st.markdown("| الرمز | الشركة | القطاع | الرأي الشرعي |")
            st.markdown("|-------|--------|--------|--------------|")
            for symbol, info in sorted(stocks.items()):
                st.markdown(f"| {symbol} | {info.get('name', '')} | {info.get('sector', '')} | {info.get('opinion', '')} |")
        else:
            st.info("لا توجد أسهم مضافة")

# ==================== الواجهة الرئيسية ====================
st.markdown('<div class="main-header"><h1>🏆 محلل الأسهم السعودي المتقدم الكامل</h1><p>شموع يابانية | نماذج سعرية | فجوات | أهداف وتوقعات | إدارة أسهم</p></div>', unsafe_allow_html=True)

# الشريط الجانبي
with st.sidebar:
    st.markdown("## 🔍 التحليل الفردي")
    symbol_input = st.text_input("رمز السهم:", value="2222")
    analyze_btn = st.button("🔍 تحليل سهم فردي", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("## 🏆 البحث عن الفرص")
    find_btn = st.button("🏆 البحث عن أقوى الفرص", use_container_width=True)
    
    st.markdown("---")
    st.markdown("## 📋 إدارة الأسهم")
    manage_btn = st.button("📋 إدارة الأسهم", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 الميزات")
    st.markdown("""
    - ✅ 4 فترات زمنية
    - ✅ شموع يابانية
    - ✅ نماذج سعرية
    - ✅ فجوات سعريه
    - ✅ أهداف السعر
    - ✅ إدارة الأسهم
    - ✅ تصدير التقارير
    """)

# ==================== إدارة الأسهم ====================
if manage_btn:
    stock_management_ui()

# ==================== تحليل سهم فردي ====================
if analyze_btn:
    with st.spinner(f"جاري تحليل {symbol_input}..."):
        try:
            result = analyze_single_stock(symbol_input)
            
            # معلومات عامة
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🏢 الشركة", result['name'])
            with col2:
                st.metric("💰 السعر", f"{result['current_price']:.2f}")
            with col3:
                st.metric("📊 القوة", f"{result['total_score']:.1f}/100")
            with col4:
                st.metric("⚖️ الرأي الشرعي", result['opinion'])
            
            st.markdown("---")
            
            # الفترات الأربع
            st.subheader("📈 التحليل الفني")
            cols = st.columns(4)
            for i, tf in enumerate(['15د', 'ساعة', 'يوم', 'اسبوع']):
                data = result['timeframes'].get(tf, {})
                with cols[i]:
                    score = data.get('score', 0)
                    color = "#4ade80" if score >= 70 else ("#fbbf24" if score >= 60 else "#ef4444")
                    st.markdown(f"""
                    <div class="timeframe-card" style="border:1px solid {color}30;">
                        <h3 style="color:{color}">{data.get('name', tf)}</h3>
                        <div style="font-size:28px; color:{color};">{score:.0f}</div>
                        <div>💰 {data.get('price', 0)}</div>
                        <div>RSI: {data.get('rsi', 0):.1f}</div>
                        <div>ADX: {data.get('adx', 0):.1f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if result['strong_timeframes']:
                st.success(f"✅ ظهرت الفرصة على {result['strong_count']} فترات: {', '.join(result['strong_timeframes'])}")
            
            st.markdown("---")
            
            # التحليل الإضافي
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🕯️ الشموع اليابانية")
                if result.get('candle_patterns'):
                    for p, d, w in result['candle_patterns']:
                        st.info(d)
                else:
                    st.info("لا توجد أنماط شموع")
                
                st.subheader("📐 النماذج السعرية")
                if result.get('patterns'):
                    for p, d, w in result['patterns']:
                        st.warning(d)
                else:
                    st.info("لا توجد نماذج سعرية")
            
            with col2:
                st.subheader("📉 الفجوات السعرية")
                if result.get('gaps'):
                    for g, d, w in result['gaps']:
                        st.warning(d)
                else:
                    st.info("لا توجد فجوات سعرية")
                
                st.subheader("💧 السيولة")
                st.progress(result['liquidity_score'] / 100)
                st.caption(f"الدرجة: {result['liquidity_score']:.1f}/100")
            
            st.markdown("---")
            
            # الأهداف والتوقعات
            st.subheader("🎯 الأهداف ووقف الخسارة")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📈 أهداف السعر**")
                for t in result.get('targets', []):
                    st.write(f"• {t['level']}: {t['price']} ({t['percentage']:+.1f}%)")
            
            with col2:
                st.markdown("**📉 وقف الخسارة**")
                for sl in result.get('stop_losses', []):
                    st.write(f"• {sl['level']}: {sl['price']} ({sl['percentage']:+.1f}%)")
            
            with col3:
                st.markdown("**⚖️ المخاطرة/العائد**")
                for rr in result.get('risk_reward', []):
                    st.write(f"• {rr['target']}: 1:{rr['ratio']} - {rr['assessment']}")
            
            st.markdown("---")
            
            # التوصية والتوقعات
            col1, col2 = st.columns(2)
            with col1:
                rec = result.get('trading_recommendation', {})
                if result['strong_count'] >= 3:
                    st.success(f"🎯 التوصية: شراء قوي")
                elif result['strong_count'] >= 2:
                    st.info(f"🎯 التوصية: شراء")
                else:
                    st.warning(f"🎯 التوصية: مراقبة")
                st.caption(rec.get('reason', ''))
            
            with col2:
                pred = result.get('prediction', {})
                st.markdown(f"**🔮 توقع السعر:** {pred.get('direction', 'غير واضح')}")
                st.markdown(f"**📊 الثقة:** {pred.get('confidence', 0)}%")
            
            st.markdown("---")
            
            # التحليل الأساسي والمؤشرات
            fundamental = result.get('fundamental', {})
            if any(fundamental.values()):
                st.subheader("🏦 التحليل الأساسي")
                fund_cols = st.columns(4)
                with fund_cols[0]:
                    if fundamental.get('pe_ratio'):
                        st.metric("P/E", f"{fundamental['pe_ratio']:.2f}")
                with fund_cols[1]:
                    if fundamental.get('pb_ratio'):
                        st.metric("P/B", f"{fundamental['pb_ratio']:.2f}")
                with fund_cols[2]:
                    if fundamental.get('dividend_yield'):
                        st.metric("عائد توزيعات", f"{fundamental['dividend_yield']:.2f}%")
                with fund_cols[3]:
                    if fundamental.get('roe'):
                        st.metric("ROE", f"{fundamental['roe']:.1f}%")
            
            # زر التصدير
            csv_data = export_single_to_csv(result)
            st.download_button(
                label="📥 تصدير التقرير (CSV)",
                data=csv_data,
                file_name=f"{result['symbol']}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # الرسم البياني
            st.subheader("📈 الرسم البياني")
            symbol_f = format_symbol(symbol_input)
            df = get_cached_data(symbol_f, '1d', '3mo')
            if not df.empty:
                df = calculate_indicators(df)
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                                     row_heights=[0.6, 0.4])
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close', line=dict(color='#3b82f6', width=2)), row=1, col=1)
                if 'RSI' in df:
                    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#a855f7', width=2)), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                fig.update_layout(template='plotly_dark', height=500)
                st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

# ==================== البحث عن أقوى الفرص ====================
if find_btn:
    st.subheader("🏆 أقوى فرص التداول")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(current, total):
        progress_bar.progress(current / total)
        status_text.text(f"جاري التحليل... {current}/{total}")
    
    with st.spinner("جاري البحث..."):
        results = find_best_opportunities(update_progress)
        progress_bar.empty()
        status_text.empty()
    
    if results:
        st.markdown(f"### 📊 عدد الفرص: {len(results)}")
        
        # زر تصدير جميع النتائج
        csv_all = export_to_csv(results)
        st.download_button(
            label="📥 تصدير جميع النتائج (CSV)",
            data=csv_all,
            file_name=f"opportunities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        for i, r in enumerate(results, 1):
            if r['total_score'] >= 75:
                medal, grade = "🔥🥇", "ذهبية"
            elif r['total_score'] >= 65:
                medal, grade = "📈🥈", "فضية"
            elif r['total_score'] >= 55:
                medal, grade = "✅🥉", "برونزية"
            else:
                medal, grade = "📊", "عادية"
            
            st.markdown(f"""
            <div class="stock-card {grade.lower()}">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 18px; font-weight: bold;">{medal} #{i} [{r['symbol']}] {r['name']}</span>
                    <span style="font-size: 20px; font-weight: bold;">{r['total_score']:.1f}/100</span>
                </div>
                <div>📍 القطاع: {r.get('sector', '-')} | ⚖️ الرأي: {r.get('opinion', '-')} | 🏅 {grade}</div>
                <div>💰 السعر: {r['price']} | RSI: {r['rsi']} | ADX: {r['adx']:.1f}</div>
                <div>📌 الفترات القوية: {r['strong_count']}/4 | {', '.join(r['strong_timeframes']) if r['strong_timeframes'] else 'لا يوجد'}</div>
                <div>💧 السيولة: {r.get('liquidity', 50):.1f}/100 | 🎯 {r['recommendation']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("لم يتم العثور على فرص")
