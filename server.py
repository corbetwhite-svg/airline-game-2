from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import random
import math

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============= AIRCRAFT DATA =============
AIRCRAFT_DATABASE = {
    "Cessna": [
        {"id": "cessna_172", "brand": "Cessna", "model": "172 Skyhawk", "type": "passenger", "capacity": 3, "cargo_capacity": 120, "fuel_capacity": 212, "fuel_burn": 36, "range": 1185, "cruise_speed": 226, "price": 350000},
        {"id": "cessna_182", "brand": "Cessna", "model": "182 Skylane", "type": "passenger", "capacity": 3, "cargo_capacity": 200, "fuel_capacity": 330, "fuel_burn": 52, "range": 1574, "cruise_speed": 267, "price": 450000},
        {"id": "cessna_206", "brand": "Cessna", "model": "206 Stationair", "type": "passenger", "capacity": 5, "cargo_capacity": 350, "fuel_capacity": 348, "fuel_burn": 65, "range": 1352, "cruise_speed": 278, "price": 600000},
        {"id": "cessna_208", "brand": "Cessna", "model": "208 Caravan", "type": "both", "capacity": 9, "cargo_capacity": 1500, "fuel_capacity": 1274, "fuel_burn": 175, "range": 1982, "cruise_speed": 344, "price": 2500000},
        {"id": "cessna_citation_cj3", "brand": "Cessna", "model": "Citation CJ3+", "type": "passenger", "capacity": 8, "cargo_capacity": 500, "fuel_capacity": 2580, "fuel_burn": 400, "range": 3704, "cruise_speed": 787, "price": 9500000}
    ],
    "Boeing": [
        {"id": "boeing_737_700", "brand": "Boeing", "model": "737-700", "type": "passenger", "capacity": 126, "cargo_capacity": 18000, "fuel_capacity": 26020, "fuel_burn": 2400, "range": 6370, "cruise_speed": 830, "price": 89000000},
        {"id": "boeing_737_800", "brand": "Boeing", "model": "737-800", "type": "passenger", "capacity": 162, "cargo_capacity": 23000, "fuel_capacity": 26020, "fuel_burn": 2500, "range": 5665, "cruise_speed": 842, "price": 106000000},
        {"id": "boeing_747_400", "brand": "Boeing", "model": "747-400", "type": "both", "capacity": 416, "cargo_capacity": 80000, "fuel_capacity": 216840, "fuel_burn": 11000, "range": 13450, "cruise_speed": 913, "price": 260000000},
        {"id": "boeing_757_200", "brand": "Boeing", "model": "757-200", "type": "both", "capacity": 200, "cargo_capacity": 32000, "fuel_capacity": 43490, "fuel_burn": 3500, "range": 7250, "cruise_speed": 850, "price": 145000000},
        {"id": "boeing_767_300", "brand": "Boeing", "model": "767-300", "type": "both", "capacity": 269, "cargo_capacity": 50000, "fuel_capacity": 91000, "fuel_burn": 5500, "range": 9700, "cruise_speed": 851, "price": 218000000},
        {"id": "boeing_777_200", "brand": "Boeing", "model": "777-200", "type": "passenger", "capacity": 313, "cargo_capacity": 60000, "fuel_capacity": 171160, "fuel_burn": 7500, "range": 15843, "cruise_speed": 905, "price": 330000000},
        {"id": "boeing_787_9", "brand": "Boeing", "model": "787-9 Dreamliner", "type": "passenger", "capacity": 296, "cargo_capacity": 45000, "fuel_capacity": 126917, "fuel_burn": 5400, "range": 14140, "cruise_speed": 903, "price": 292000000}
    ],
    "Airbus": [
        {"id": "airbus_a220_100", "brand": "Airbus", "model": "A220-100", "type": "passenger", "capacity": 120, "cargo_capacity": 15000, "fuel_capacity": 21805, "fuel_burn": 2000, "range": 5460, "cruise_speed": 829, "price": 81000000},
        {"id": "airbus_a320neo", "brand": "Airbus", "model": "A320neo", "type": "passenger", "capacity": 165, "cargo_capacity": 20000, "fuel_capacity": 26730, "fuel_burn": 2300, "range": 6300, "cruise_speed": 833, "price": 110700000},
        {"id": "airbus_a321xlr", "brand": "Airbus", "model": "A321XLR", "type": "passenger", "capacity": 220, "cargo_capacity": 25000, "fuel_capacity": 32940, "fuel_burn": 2700, "range": 8700, "cruise_speed": 833, "price": 133000000},
        {"id": "airbus_a330_900", "brand": "Airbus", "model": "A330-900neo", "type": "both", "capacity": 287, "cargo_capacity": 45000, "fuel_capacity": 139090, "fuel_burn": 5200, "range": 13334, "cruise_speed": 871, "price": 296400000},
        {"id": "airbus_a350_900", "brand": "Airbus", "model": "A350-900", "type": "passenger", "capacity": 325, "cargo_capacity": 50000, "fuel_capacity": 141000, "fuel_burn": 5800, "range": 15000, "cruise_speed": 903, "price": 317400000},
        {"id": "airbus_a380_800", "brand": "Airbus", "model": "A380-800", "type": "passenger", "capacity": 555, "cargo_capacity": 100000, "fuel_capacity": 320000, "fuel_burn": 13000, "range": 14800, "cruise_speed": 903, "price": 445600000}
    ],
    "Beechcraft": [
        {"id": "beech_bonanza_g36", "brand": "Beechcraft", "model": "Bonanza G36", "type": "passenger", "capacity": 5, "cargo_capacity": 200, "fuel_capacity": 296, "fuel_burn": 58, "range": 1478, "cruise_speed": 315, "price": 850000},
        {"id": "beech_baron_g58", "brand": "Beechcraft", "model": "Baron G58", "type": "passenger", "capacity": 5, "cargo_capacity": 250, "fuel_capacity": 374, "fuel_burn": 104, "range": 1480, "cruise_speed": 372, "price": 1400000},
        {"id": "beech_king_air_250", "brand": "Beechcraft", "model": "King Air 250", "type": "both", "capacity": 8, "cargo_capacity": 800, "fuel_capacity": 1800, "fuel_burn": 260, "range": 2920, "cruise_speed": 574, "price": 6500000},
        {"id": "beech_king_air_350", "brand": "Beechcraft", "model": "King Air 350i", "type": "both", "capacity": 11, "cargo_capacity": 1200, "fuel_capacity": 2010, "fuel_burn": 350, "range": 3100, "cruise_speed": 578, "price": 9000000},
        {"id": "beech_premier_ia", "brand": "Beechcraft", "model": "Premier IA", "type": "passenger", "capacity": 6, "cargo_capacity": 400, "fuel_capacity": 1980, "fuel_burn": 380, "range": 2519, "cruise_speed": 835, "price": 5500000}
    ],
    "Piper": [
        {"id": "piper_archer", "brand": "Piper", "model": "PA-28 Archer", "type": "passenger", "capacity": 3, "cargo_capacity": 100, "fuel_capacity": 189, "fuel_burn": 38, "range": 1063, "cruise_speed": 237, "price": 330000},
        {"id": "piper_seminole", "brand": "Piper", "model": "PA-44 Seminole", "type": "passenger", "capacity": 3, "cargo_capacity": 150, "fuel_capacity": 416, "fuel_burn": 72, "range": 1527, "cruise_speed": 313, "price": 750000},
        {"id": "piper_m350", "brand": "Piper", "model": "M350", "type": "passenger", "capacity": 5, "cargo_capacity": 300, "fuel_capacity": 492, "fuel_burn": 85, "range": 2380, "cruise_speed": 398, "price": 1200000},
        {"id": "piper_m500", "brand": "Piper", "model": "M500", "type": "passenger", "capacity": 5, "cargo_capacity": 350, "fuel_capacity": 1150, "fuel_burn": 200, "range": 2350, "cruise_speed": 500, "price": 3000000},
        {"id": "piper_m600", "brand": "Piper", "model": "M600 SLS", "type": "both", "capacity": 5, "cargo_capacity": 500, "fuel_capacity": 1280, "fuel_burn": 230, "range": 2792, "cruise_speed": 500, "price": 3500000}
    ],
    "Cirrus": [
        {"id": "cirrus_sr20", "brand": "Cirrus", "model": "SR20", "type": "passenger", "capacity": 3, "cargo_capacity": 80, "fuel_capacity": 227, "fuel_burn": 42, "range": 1148, "cruise_speed": 278, "price": 500000},
        {"id": "cirrus_sr22", "brand": "Cirrus", "model": "SR22", "type": "passenger", "capacity": 3, "cargo_capacity": 100, "fuel_capacity": 372, "fuel_burn": 58, "range": 1708, "cruise_speed": 338, "price": 650000},
        {"id": "cirrus_sr22t", "brand": "Cirrus", "model": "SR22T", "type": "passenger", "capacity": 3, "cargo_capacity": 120, "fuel_capacity": 372, "fuel_burn": 75, "range": 1554, "cruise_speed": 378, "price": 750000},
        {"id": "cirrus_sf50", "brand": "Cirrus", "model": "SF50 Vision Jet", "type": "passenger", "capacity": 5, "cargo_capacity": 200, "fuel_capacity": 950, "fuel_burn": 180, "range": 2222, "cruise_speed": 556, "price": 3000000},
        {"id": "cirrus_sf50_g2", "brand": "Cirrus", "model": "SF50 Vision Jet G2+", "type": "passenger", "capacity": 6, "cargo_capacity": 250, "fuel_capacity": 1100, "fuel_burn": 200, "range": 2480, "cruise_speed": 556, "price": 3500000}
    ],
    "Embraer": [
        {"id": "embraer_e175", "brand": "Embraer", "model": "E175", "type": "passenger", "capacity": 78, "cargo_capacity": 8000, "fuel_capacity": 11200, "fuel_burn": 1800, "range": 3704, "cruise_speed": 797, "price": 46000000},
        {"id": "embraer_e190_e2", "brand": "Embraer", "model": "E190-E2", "type": "passenger", "capacity": 106, "cargo_capacity": 12000, "fuel_capacity": 16150, "fuel_burn": 2100, "range": 5278, "cruise_speed": 833, "price": 59100000},
        {"id": "embraer_e195_e2", "brand": "Embraer", "model": "E195-E2", "type": "passenger", "capacity": 132, "cargo_capacity": 14000, "fuel_capacity": 16150, "fuel_burn": 2300, "range": 4815, "cruise_speed": 833, "price": 66600000},
        {"id": "embraer_phenom_100", "brand": "Embraer", "model": "Phenom 100EV", "type": "passenger", "capacity": 4, "cargo_capacity": 300, "fuel_capacity": 1100, "fuel_burn": 200, "range": 2182, "cruise_speed": 722, "price": 4900000},
        {"id": "embraer_phenom_300", "brand": "Embraer", "model": "Phenom 300E", "type": "passenger", "capacity": 8, "cargo_capacity": 500, "fuel_capacity": 2400, "fuel_burn": 320, "range": 3724, "cruise_speed": 839, "price": 10900000}
    ]
}

# ============= AIRPORT DATA =============
AIRPORT_DATABASE = [
    # North America - USA
    {"iata": "JFK", "name": "John F. Kennedy International", "city": "New York", "country": "USA", "lat": 40.6413, "lon": -73.7781, "congestion": 0.85},
    {"iata": "LAX", "name": "Los Angeles International", "city": "Los Angeles", "country": "USA", "lat": 33.9416, "lon": -118.4085, "congestion": 0.82},
    {"iata": "ORD", "name": "O'Hare International", "city": "Chicago", "country": "USA", "lat": 41.9742, "lon": -87.9073, "congestion": 0.88},
    {"iata": "DFW", "name": "Dallas/Fort Worth International", "city": "Dallas", "country": "USA", "lat": 32.8998, "lon": -97.0403, "congestion": 0.75},
    {"iata": "DEN", "name": "Denver International", "city": "Denver", "country": "USA", "lat": 39.8561, "lon": -104.6737, "congestion": 0.70},
    {"iata": "SFO", "name": "San Francisco International", "city": "San Francisco", "country": "USA", "lat": 37.6213, "lon": -122.3790, "congestion": 0.78},
    {"iata": "SEA", "name": "Seattle-Tacoma International", "city": "Seattle", "country": "USA", "lat": 47.4502, "lon": -122.3088, "congestion": 0.65},
    {"iata": "MIA", "name": "Miami International", "city": "Miami", "country": "USA", "lat": 25.7959, "lon": -80.2870, "congestion": 0.72},
    {"iata": "ATL", "name": "Hartsfield-Jackson Atlanta International", "city": "Atlanta", "country": "USA", "lat": 33.6407, "lon": -84.4277, "congestion": 0.90},
    {"iata": "BOS", "name": "Boston Logan International", "city": "Boston", "country": "USA", "lat": 42.3656, "lon": -71.0096, "congestion": 0.68},
    {"iata": "PHX", "name": "Phoenix Sky Harbor International", "city": "Phoenix", "country": "USA", "lat": 33.4373, "lon": -112.0078, "congestion": 0.62},
    {"iata": "LAS", "name": "Harry Reid International", "city": "Las Vegas", "country": "USA", "lat": 36.0840, "lon": -115.1537, "congestion": 0.74},
    {"iata": "MCO", "name": "Orlando International", "city": "Orlando", "country": "USA", "lat": 28.4312, "lon": -81.3081, "congestion": 0.70},
    {"iata": "EWR", "name": "Newark Liberty International", "city": "Newark", "country": "USA", "lat": 40.6895, "lon": -74.1745, "congestion": 0.80},
    {"iata": "MSP", "name": "Minneapolis-Saint Paul International", "city": "Minneapolis", "country": "USA", "lat": 44.8848, "lon": -93.2223, "congestion": 0.60},
    {"iata": "DTW", "name": "Detroit Metropolitan", "city": "Detroit", "country": "USA", "lat": 42.2162, "lon": -83.3554, "congestion": 0.58},
    {"iata": "PHL", "name": "Philadelphia International", "city": "Philadelphia", "country": "USA", "lat": 39.8744, "lon": -75.2424, "congestion": 0.65},
    {"iata": "CLT", "name": "Charlotte Douglas International", "city": "Charlotte", "country": "USA", "lat": 35.2144, "lon": -80.9473, "congestion": 0.68},
    {"iata": "IAH", "name": "George Bush Intercontinental", "city": "Houston", "country": "USA", "lat": 29.9902, "lon": -95.3368, "congestion": 0.72},
    {"iata": "SAN", "name": "San Diego International", "city": "San Diego", "country": "USA", "lat": 32.7336, "lon": -117.1897, "congestion": 0.55},
    {"iata": "SLC", "name": "Salt Lake City International", "city": "Salt Lake City", "country": "USA", "lat": 40.7899, "lon": -111.9791, "congestion": 0.52},
    {"iata": "PDX", "name": "Portland International", "city": "Portland", "country": "USA", "lat": 45.5898, "lon": -122.5951, "congestion": 0.50},
    {"iata": "HNL", "name": "Daniel K. Inouye International", "city": "Honolulu", "country": "USA", "lat": 21.3245, "lon": -157.9251, "congestion": 0.55},
    {"iata": "ANC", "name": "Ted Stevens Anchorage International", "city": "Anchorage", "country": "USA", "lat": 61.1743, "lon": -149.9962, "congestion": 0.35},
    # Canada
    {"iata": "YYZ", "name": "Toronto Pearson International", "city": "Toronto", "country": "Canada", "lat": 43.6777, "lon": -79.6248, "congestion": 0.76},
    {"iata": "YVR", "name": "Vancouver International", "city": "Vancouver", "country": "Canada", "lat": 49.1947, "lon": -123.1792, "congestion": 0.58},
    {"iata": "YUL", "name": "Montreal Trudeau International", "city": "Montreal", "country": "Canada", "lat": 45.4706, "lon": -73.7408, "congestion": 0.55},
    {"iata": "YYC", "name": "Calgary International", "city": "Calgary", "country": "Canada", "lat": 51.1215, "lon": -114.0076, "congestion": 0.50},
    {"iata": "YEG", "name": "Edmonton International", "city": "Edmonton", "country": "Canada", "lat": 53.3097, "lon": -113.5800, "congestion": 0.42},
    # Mexico
    {"iata": "MEX", "name": "Mexico City International", "city": "Mexico City", "country": "Mexico", "lat": 19.4363, "lon": -99.0721, "congestion": 0.80},
    {"iata": "CUN", "name": "Cancun International", "city": "Cancun", "country": "Mexico", "lat": 21.0365, "lon": -86.8771, "congestion": 0.65},
    {"iata": "GDL", "name": "Guadalajara International", "city": "Guadalajara", "country": "Mexico", "lat": 20.5218, "lon": -103.3111, "congestion": 0.55},
    # Europe - UK
    {"iata": "LHR", "name": "London Heathrow", "city": "London", "country": "UK", "lat": 51.4700, "lon": -0.4543, "congestion": 0.92},
    {"iata": "LGW", "name": "London Gatwick", "city": "London", "country": "UK", "lat": 51.1537, "lon": -0.1821, "congestion": 0.78},
    {"iata": "MAN", "name": "Manchester Airport", "city": "Manchester", "country": "UK", "lat": 53.3588, "lon": -2.2727, "congestion": 0.62},
    {"iata": "EDI", "name": "Edinburgh Airport", "city": "Edinburgh", "country": "UK", "lat": 55.9508, "lon": -3.3615, "congestion": 0.50},
    # Europe - France
    {"iata": "CDG", "name": "Paris Charles de Gaulle", "city": "Paris", "country": "France", "lat": 49.0097, "lon": 2.5479, "congestion": 0.84},
    {"iata": "ORY", "name": "Paris Orly", "city": "Paris", "country": "France", "lat": 48.7262, "lon": 2.3652, "congestion": 0.70},
    {"iata": "NCE", "name": "Nice Cote d'Azur", "city": "Nice", "country": "France", "lat": 43.6584, "lon": 7.2159, "congestion": 0.55},
    {"iata": "LYS", "name": "Lyon-Saint Exupery", "city": "Lyon", "country": "France", "lat": 45.7256, "lon": 5.0811, "congestion": 0.48},
    # Europe - Germany
    {"iata": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany", "lat": 50.0379, "lon": 8.5622, "congestion": 0.78},
    {"iata": "MUC", "name": "Munich Airport", "city": "Munich", "country": "Germany", "lat": 48.3537, "lon": 11.7750, "congestion": 0.68},
    {"iata": "TXL", "name": "Berlin Brandenburg", "city": "Berlin", "country": "Germany", "lat": 52.3667, "lon": 13.5033, "congestion": 0.60},
    {"iata": "DUS", "name": "Dusseldorf Airport", "city": "Dusseldorf", "country": "Germany", "lat": 51.2895, "lon": 6.7668, "congestion": 0.55},
    {"iata": "HAM", "name": "Hamburg Airport", "city": "Hamburg", "country": "Germany", "lat": 53.6304, "lon": 10.0065, "congestion": 0.50},
    # Europe - Other
    {"iata": "AMS", "name": "Amsterdam Schiphol", "city": "Amsterdam", "country": "Netherlands", "lat": 52.3105, "lon": 4.7683, "congestion": 0.80},
    {"iata": "MAD", "name": "Madrid Barajas", "city": "Madrid", "country": "Spain", "lat": 40.4983, "lon": -3.5676, "congestion": 0.72},
    {"iata": "BCN", "name": "Barcelona El Prat", "city": "Barcelona", "country": "Spain", "lat": 41.2974, "lon": 2.0833, "congestion": 0.70},
    {"iata": "FCO", "name": "Rome Fiumicino", "city": "Rome", "country": "Italy", "lat": 41.8003, "lon": 12.2389, "congestion": 0.74},
    {"iata": "MXP", "name": "Milan Malpensa", "city": "Milan", "country": "Italy", "lat": 45.6306, "lon": 8.7281, "congestion": 0.65},
    {"iata": "VCE", "name": "Venice Marco Polo", "city": "Venice", "country": "Italy", "lat": 45.5053, "lon": 12.3519, "congestion": 0.52},
    {"iata": "IST", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey", "lat": 41.2608, "lon": 28.7418, "congestion": 0.82},
    {"iata": "ZRH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland", "lat": 47.4582, "lon": 8.5555, "congestion": 0.60},
    {"iata": "GVA", "name": "Geneva Airport", "city": "Geneva", "country": "Switzerland", "lat": 46.2370, "lon": 6.1092, "congestion": 0.52},
    {"iata": "VIE", "name": "Vienna International", "city": "Vienna", "country": "Austria", "lat": 48.1103, "lon": 16.5697, "congestion": 0.58},
    {"iata": "CPH", "name": "Copenhagen Airport", "city": "Copenhagen", "country": "Denmark", "lat": 55.6180, "lon": 12.6508, "congestion": 0.55},
    {"iata": "OSL", "name": "Oslo Gardermoen", "city": "Oslo", "country": "Norway", "lat": 60.1976, "lon": 11.1004, "congestion": 0.50},
    {"iata": "ARN", "name": "Stockholm Arlanda", "city": "Stockholm", "country": "Sweden", "lat": 59.6498, "lon": 17.9238, "congestion": 0.52},
    {"iata": "HEL", "name": "Helsinki-Vantaa", "city": "Helsinki", "country": "Finland", "lat": 60.3172, "lon": 24.9633, "congestion": 0.45},
    {"iata": "DUB", "name": "Dublin Airport", "city": "Dublin", "country": "Ireland", "lat": 53.4264, "lon": -6.2499, "congestion": 0.58},
    {"iata": "LIS", "name": "Lisbon Portela", "city": "Lisbon", "country": "Portugal", "lat": 38.7756, "lon": -9.1354, "congestion": 0.60},
    {"iata": "ATH", "name": "Athens International", "city": "Athens", "country": "Greece", "lat": 37.9364, "lon": 23.9445, "congestion": 0.55},
    {"iata": "PRG", "name": "Prague Vaclav Havel", "city": "Prague", "country": "Czech Republic", "lat": 50.1008, "lon": 14.2600, "congestion": 0.50},
    {"iata": "WAW", "name": "Warsaw Chopin", "city": "Warsaw", "country": "Poland", "lat": 52.1657, "lon": 20.9671, "congestion": 0.52},
    {"iata": "BUD", "name": "Budapest Ferenc Liszt", "city": "Budapest", "country": "Hungary", "lat": 47.4298, "lon": 19.2611, "congestion": 0.48},
    # Asia - Japan
    {"iata": "NRT", "name": "Narita International", "city": "Tokyo", "country": "Japan", "lat": 35.7720, "lon": 140.3929, "congestion": 0.75},
    {"iata": "HND", "name": "Tokyo Haneda", "city": "Tokyo", "country": "Japan", "lat": 35.5494, "lon": 139.7798, "congestion": 0.88},
    {"iata": "KIX", "name": "Osaka Kansai International", "city": "Osaka", "country": "Japan", "lat": 34.4347, "lon": 135.2441, "congestion": 0.65},
    {"iata": "NGO", "name": "Nagoya Chubu Centrair", "city": "Nagoya", "country": "Japan", "lat": 34.8584, "lon": 136.8124, "congestion": 0.52},
    # Asia - China
    {"iata": "PEK", "name": "Beijing Capital International", "city": "Beijing", "country": "China", "lat": 40.0799, "lon": 116.6031, "congestion": 0.86},
    {"iata": "PVG", "name": "Shanghai Pudong International", "city": "Shanghai", "country": "China", "lat": 31.1443, "lon": 121.8083, "congestion": 0.84},
    {"iata": "CAN", "name": "Guangzhou Baiyun International", "city": "Guangzhou", "country": "China", "lat": 23.3924, "lon": 113.2988, "congestion": 0.78},
    {"iata": "SZX", "name": "Shenzhen Bao'an International", "city": "Shenzhen", "country": "China", "lat": 22.6393, "lon": 113.8107, "congestion": 0.72},
    {"iata": "CTU", "name": "Chengdu Shuangliu International", "city": "Chengdu", "country": "China", "lat": 30.5785, "lon": 103.9471, "congestion": 0.68},
    {"iata": "HKG", "name": "Hong Kong International", "city": "Hong Kong", "country": "China", "lat": 22.3080, "lon": 113.9185, "congestion": 0.82},
    # Asia - Other
    {"iata": "ICN", "name": "Incheon International", "city": "Seoul", "country": "South Korea", "lat": 37.4602, "lon": 126.4407, "congestion": 0.72},
    {"iata": "GMP", "name": "Seoul Gimpo International", "city": "Seoul", "country": "South Korea", "lat": 37.5583, "lon": 126.7906, "congestion": 0.65},
    {"iata": "SIN", "name": "Singapore Changi", "city": "Singapore", "country": "Singapore", "lat": 1.3644, "lon": 103.9915, "congestion": 0.78},
    {"iata": "BKK", "name": "Bangkok Suvarnabhumi", "city": "Bangkok", "country": "Thailand", "lat": 13.6900, "lon": 100.7501, "congestion": 0.76},
    {"iata": "KUL", "name": "Kuala Lumpur International", "city": "Kuala Lumpur", "country": "Malaysia", "lat": 2.7456, "lon": 101.7099, "congestion": 0.65},
    {"iata": "CGK", "name": "Jakarta Soekarno-Hatta", "city": "Jakarta", "country": "Indonesia", "lat": -6.1256, "lon": 106.6558, "congestion": 0.72},
    {"iata": "MNL", "name": "Manila Ninoy Aquino", "city": "Manila", "country": "Philippines", "lat": 14.5086, "lon": 121.0197, "congestion": 0.70},
    {"iata": "DEL", "name": "Delhi Indira Gandhi International", "city": "Delhi", "country": "India", "lat": 28.5562, "lon": 77.1000, "congestion": 0.80},
    {"iata": "BOM", "name": "Mumbai Chhatrapati Shivaji", "city": "Mumbai", "country": "India", "lat": 19.0896, "lon": 72.8656, "congestion": 0.78},
    {"iata": "BLR", "name": "Bangalore Kempegowda International", "city": "Bangalore", "country": "India", "lat": 13.1979, "lon": 77.7063, "congestion": 0.65},
    {"iata": "MAA", "name": "Chennai International", "city": "Chennai", "country": "India", "lat": 12.9941, "lon": 80.1709, "congestion": 0.58},
    # Oceania
    {"iata": "SYD", "name": "Sydney Kingsford Smith", "city": "Sydney", "country": "Australia", "lat": -33.9399, "lon": 151.1753, "congestion": 0.74},
    {"iata": "MEL", "name": "Melbourne Tullamarine", "city": "Melbourne", "country": "Australia", "lat": -37.6690, "lon": 144.8410, "congestion": 0.68},
    {"iata": "BNE", "name": "Brisbane Airport", "city": "Brisbane", "country": "Australia", "lat": -27.3842, "lon": 153.1175, "congestion": 0.55},
    {"iata": "PER", "name": "Perth Airport", "city": "Perth", "country": "Australia", "lat": -31.9403, "lon": 115.9669, "congestion": 0.50},
    {"iata": "AKL", "name": "Auckland International", "city": "Auckland", "country": "New Zealand", "lat": -37.0082, "lon": 174.7850, "congestion": 0.55},
    {"iata": "WLG", "name": "Wellington International", "city": "Wellington", "country": "New Zealand", "lat": -41.3272, "lon": 174.8050, "congestion": 0.40},
    # Middle East
    {"iata": "DXB", "name": "Dubai International", "city": "Dubai", "country": "UAE", "lat": 25.2532, "lon": 55.3657, "congestion": 0.88},
    {"iata": "AUH", "name": "Abu Dhabi International", "city": "Abu Dhabi", "country": "UAE", "lat": 24.4330, "lon": 54.6511, "congestion": 0.62},
    {"iata": "DOH", "name": "Hamad International", "city": "Doha", "country": "Qatar", "lat": 25.2609, "lon": 51.6138, "congestion": 0.70},
    {"iata": "RUH", "name": "King Khalid International", "city": "Riyadh", "country": "Saudi Arabia", "lat": 24.9576, "lon": 46.6988, "congestion": 0.60},
    {"iata": "JED", "name": "King Abdulaziz International", "city": "Jeddah", "country": "Saudi Arabia", "lat": 21.6796, "lon": 39.1565, "congestion": 0.65},
    {"iata": "TLV", "name": "Ben Gurion International", "city": "Tel Aviv", "country": "Israel", "lat": 32.0055, "lon": 34.8854, "congestion": 0.68},
    # South America
    {"iata": "GRU", "name": "Sao Paulo Guarulhos", "city": "Sao Paulo", "country": "Brazil", "lat": -23.4356, "lon": -46.4731, "congestion": 0.78},
    {"iata": "GIG", "name": "Rio de Janeiro Galeao", "city": "Rio de Janeiro", "country": "Brazil", "lat": -22.8099, "lon": -43.2505, "congestion": 0.65},
    {"iata": "BSB", "name": "Brasilia International", "city": "Brasilia", "country": "Brazil", "lat": -15.8711, "lon": -47.9186, "congestion": 0.55},
    {"iata": "EZE", "name": "Buenos Aires Ezeiza", "city": "Buenos Aires", "country": "Argentina", "lat": -34.8222, "lon": -58.5358, "congestion": 0.65},
    {"iata": "SCL", "name": "Santiago Arturo Merino Benitez", "city": "Santiago", "country": "Chile", "lat": -33.3930, "lon": -70.7858, "congestion": 0.60},
    {"iata": "LIM", "name": "Lima Jorge Chavez International", "city": "Lima", "country": "Peru", "lat": -12.0219, "lon": -77.1143, "congestion": 0.58},
    {"iata": "BOG", "name": "Bogota El Dorado", "city": "Bogota", "country": "Colombia", "lat": 4.7016, "lon": -74.1469, "congestion": 0.72},
    {"iata": "UIO", "name": "Quito Mariscal Sucre", "city": "Quito", "country": "Ecuador", "lat": -0.1292, "lon": -78.3575, "congestion": 0.50},
    {"iata": "CCS", "name": "Caracas Simon Bolivar", "city": "Caracas", "country": "Venezuela", "lat": 10.6031, "lon": -66.9906, "congestion": 0.55},
    # Africa
    {"iata": "JNB", "name": "Johannesburg O.R. Tambo", "city": "Johannesburg", "country": "South Africa", "lat": -26.1367, "lon": 28.2411, "congestion": 0.68},
    {"iata": "CPT", "name": "Cape Town International", "city": "Cape Town", "country": "South Africa", "lat": -33.9715, "lon": 18.6021, "congestion": 0.55},
    {"iata": "CAI", "name": "Cairo International", "city": "Cairo", "country": "Egypt", "lat": 30.1219, "lon": 31.4056, "congestion": 0.72},
    {"iata": "NBO", "name": "Nairobi Jomo Kenyatta", "city": "Nairobi", "country": "Kenya", "lat": -1.3192, "lon": 36.9278, "congestion": 0.58},
    {"iata": "ADD", "name": "Addis Ababa Bole", "city": "Addis Ababa", "country": "Ethiopia", "lat": 8.9779, "lon": 38.7993, "congestion": 0.52},
    {"iata": "CMN", "name": "Casablanca Mohammed V", "city": "Casablanca", "country": "Morocco", "lat": 33.3675, "lon": -7.5898, "congestion": 0.55},
    {"iata": "LOS", "name": "Lagos Murtala Muhammed", "city": "Lagos", "country": "Nigeria", "lat": 6.5774, "lon": 3.3212, "congestion": 0.65},
    # Caribbean
    {"iata": "SJU", "name": "San Juan Luis Munoz Marin", "city": "San Juan", "country": "Puerto Rico", "lat": 18.4394, "lon": -66.0018, "congestion": 0.55},
    {"iata": "NAS", "name": "Nassau Lynden Pindling", "city": "Nassau", "country": "Bahamas", "lat": 25.0390, "lon": -77.4662, "congestion": 0.48},
    {"iata": "MBJ", "name": "Montego Bay Sangster", "city": "Montego Bay", "country": "Jamaica", "lat": 18.5037, "lon": -77.9134, "congestion": 0.50},
    {"iata": "PUJ", "name": "Punta Cana International", "city": "Punta Cana", "country": "Dominican Republic", "lat": 18.5674, "lon": -68.3634, "congestion": 0.55},
    
    # More US Regional Airports
    {"iata": "BNA", "name": "Nashville International", "city": "Nashville", "country": "USA", "lat": 36.1263, "lon": -86.6774, "congestion": 0.58},
    {"iata": "AUS", "name": "Austin-Bergstrom International", "city": "Austin", "country": "USA", "lat": 30.1975, "lon": -97.6664, "congestion": 0.62},
    {"iata": "RDU", "name": "Raleigh-Durham International", "city": "Raleigh", "country": "USA", "lat": 35.8776, "lon": -78.7875, "congestion": 0.52},
    {"iata": "SNA", "name": "John Wayne Airport", "city": "Santa Ana", "country": "USA", "lat": 33.6757, "lon": -117.8678, "congestion": 0.55},
    {"iata": "SMF", "name": "Sacramento International", "city": "Sacramento", "country": "USA", "lat": 38.6954, "lon": -121.5908, "congestion": 0.48},
    {"iata": "OAK", "name": "Oakland International", "city": "Oakland", "country": "USA", "lat": 37.7213, "lon": -122.2208, "congestion": 0.52},
    {"iata": "SJC", "name": "San Jose International", "city": "San Jose", "country": "USA", "lat": 37.3626, "lon": -121.9291, "congestion": 0.55},
    {"iata": "MCI", "name": "Kansas City International", "city": "Kansas City", "country": "USA", "lat": 39.2976, "lon": -94.7139, "congestion": 0.48},
    {"iata": "STL", "name": "St. Louis Lambert International", "city": "St. Louis", "country": "USA", "lat": 38.7487, "lon": -90.3700, "congestion": 0.52},
    {"iata": "IND", "name": "Indianapolis International", "city": "Indianapolis", "country": "USA", "lat": 39.7173, "lon": -86.2944, "congestion": 0.45},
    {"iata": "CVG", "name": "Cincinnati/Northern Kentucky", "city": "Cincinnati", "country": "USA", "lat": 39.0488, "lon": -84.6678, "congestion": 0.48},
    {"iata": "CLE", "name": "Cleveland Hopkins International", "city": "Cleveland", "country": "USA", "lat": 41.4117, "lon": -81.8498, "congestion": 0.50},
    {"iata": "PIT", "name": "Pittsburgh International", "city": "Pittsburgh", "country": "USA", "lat": 40.4915, "lon": -80.2329, "congestion": 0.48},
    {"iata": "CMH", "name": "John Glenn Columbus International", "city": "Columbus", "country": "USA", "lat": 39.9980, "lon": -82.8919, "congestion": 0.45},
    {"iata": "JAX", "name": "Jacksonville International", "city": "Jacksonville", "country": "USA", "lat": 30.4941, "lon": -81.6879, "congestion": 0.42},
    {"iata": "TPA", "name": "Tampa International", "city": "Tampa", "country": "USA", "lat": 27.9755, "lon": -82.5332, "congestion": 0.55},
    {"iata": "FLL", "name": "Fort Lauderdale-Hollywood", "city": "Fort Lauderdale", "country": "USA", "lat": 26.0726, "lon": -80.1527, "congestion": 0.62},
    {"iata": "RSW", "name": "Southwest Florida International", "city": "Fort Myers", "country": "USA", "lat": 26.5362, "lon": -81.7552, "congestion": 0.48},
    {"iata": "MSY", "name": "Louis Armstrong New Orleans", "city": "New Orleans", "country": "USA", "lat": 29.9934, "lon": -90.2580, "congestion": 0.55},
    {"iata": "SAT", "name": "San Antonio International", "city": "San Antonio", "country": "USA", "lat": 29.5337, "lon": -98.4698, "congestion": 0.45},
    {"iata": "ABQ", "name": "Albuquerque International Sunport", "city": "Albuquerque", "country": "USA", "lat": 35.0402, "lon": -106.6094, "congestion": 0.40},
    {"iata": "TUS", "name": "Tucson International", "city": "Tucson", "country": "USA", "lat": 32.1161, "lon": -110.9410, "congestion": 0.38},
    {"iata": "OKC", "name": "Will Rogers World Airport", "city": "Oklahoma City", "country": "USA", "lat": 35.3931, "lon": -97.6007, "congestion": 0.42},
    {"iata": "OMA", "name": "Eppley Airfield", "city": "Omaha", "country": "USA", "lat": 41.3032, "lon": -95.8941, "congestion": 0.40},
    {"iata": "MEM", "name": "Memphis International", "city": "Memphis", "country": "USA", "lat": 35.0424, "lon": -89.9767, "congestion": 0.52},
    {"iata": "BUF", "name": "Buffalo Niagara International", "city": "Buffalo", "country": "USA", "lat": 42.9405, "lon": -78.7322, "congestion": 0.42},
    {"iata": "ALB", "name": "Albany International", "city": "Albany", "country": "USA", "lat": 42.7483, "lon": -73.8017, "congestion": 0.38},
    {"iata": "BDL", "name": "Bradley International", "city": "Hartford", "country": "USA", "lat": 41.9389, "lon": -72.6832, "congestion": 0.45},
    {"iata": "PVD", "name": "T.F. Green Airport", "city": "Providence", "country": "USA", "lat": 41.7326, "lon": -71.4204, "congestion": 0.42},
    {"iata": "PWM", "name": "Portland International Jetport", "city": "Portland", "country": "USA", "lat": 43.6462, "lon": -70.3093, "congestion": 0.35},
    {"iata": "BTV", "name": "Burlington International", "city": "Burlington", "country": "USA", "lat": 44.4720, "lon": -73.1533, "congestion": 0.32},
    {"iata": "RNO", "name": "Reno-Tahoe International", "city": "Reno", "country": "USA", "lat": 39.4991, "lon": -119.7681, "congestion": 0.45},
    {"iata": "BOI", "name": "Boise Airport", "city": "Boise", "country": "USA", "lat": 43.5644, "lon": -116.2228, "congestion": 0.40},
    {"iata": "GEG", "name": "Spokane International", "city": "Spokane", "country": "USA", "lat": 47.6199, "lon": -117.5338, "congestion": 0.38},
    {"iata": "BZN", "name": "Bozeman Yellowstone International", "city": "Bozeman", "country": "USA", "lat": 45.7775, "lon": -111.1530, "congestion": 0.35},
    {"iata": "FAT", "name": "Fresno Yosemite International", "city": "Fresno", "country": "USA", "lat": 36.7762, "lon": -119.7181, "congestion": 0.38},
    {"iata": "BUR", "name": "Hollywood Burbank Airport", "city": "Burbank", "country": "USA", "lat": 34.2007, "lon": -118.3585, "congestion": 0.48},
    {"iata": "ONT", "name": "Ontario International", "city": "Ontario", "country": "USA", "lat": 34.0560, "lon": -117.6012, "congestion": 0.52},
    {"iata": "LGB", "name": "Long Beach Airport", "city": "Long Beach", "country": "USA", "lat": 33.8177, "lon": -118.1516, "congestion": 0.45},
    {"iata": "PSP", "name": "Palm Springs International", "city": "Palm Springs", "country": "USA", "lat": 33.8297, "lon": -116.5067, "congestion": 0.42},
    
    # More European Airports
    {"iata": "VIE", "name": "Vienna International", "city": "Vienna", "country": "Austria", "lat": 48.1103, "lon": 16.5697, "congestion": 0.65},
    {"iata": "ZRH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland", "lat": 47.4582, "lon": 8.5555, "congestion": 0.68},
    {"iata": "GVA", "name": "Geneva Airport", "city": "Geneva", "country": "Switzerland", "lat": 46.2381, "lon": 6.1089, "congestion": 0.58},
    {"iata": "BRU", "name": "Brussels Airport", "city": "Brussels", "country": "Belgium", "lat": 50.9014, "lon": 4.4844, "congestion": 0.62},
    {"iata": "LIS", "name": "Lisbon Portela Airport", "city": "Lisbon", "country": "Portugal", "lat": 38.7813, "lon": -9.1359, "congestion": 0.65},
    {"iata": "OPO", "name": "Porto Airport", "city": "Porto", "country": "Portugal", "lat": 41.2481, "lon": -8.6814, "congestion": 0.52},
    {"iata": "ATH", "name": "Athens International", "city": "Athens", "country": "Greece", "lat": 37.9364, "lon": 23.9445, "congestion": 0.62},
    {"iata": "PRG", "name": "Vaclav Havel Airport Prague", "city": "Prague", "country": "Czech Republic", "lat": 50.1008, "lon": 14.2600, "congestion": 0.58},
    {"iata": "WAW", "name": "Warsaw Chopin Airport", "city": "Warsaw", "country": "Poland", "lat": 52.1657, "lon": 20.9671, "congestion": 0.55},
    {"iata": "KRK", "name": "Krakow Airport", "city": "Krakow", "country": "Poland", "lat": 50.0777, "lon": 19.7848, "congestion": 0.45},
    {"iata": "BUD", "name": "Budapest Airport", "city": "Budapest", "country": "Hungary", "lat": 47.4369, "lon": 19.2556, "congestion": 0.52},
    {"iata": "OSL", "name": "Oslo Gardermoen", "city": "Oslo", "country": "Norway", "lat": 60.1976, "lon": 11.1004, "congestion": 0.55},
    {"iata": "ARN", "name": "Stockholm Arlanda", "city": "Stockholm", "country": "Sweden", "lat": 59.6519, "lon": 17.9186, "congestion": 0.58},
    {"iata": "CPH", "name": "Copenhagen Airport", "city": "Copenhagen", "country": "Denmark", "lat": 55.6181, "lon": 12.6561, "congestion": 0.62},
    {"iata": "HEL", "name": "Helsinki-Vantaa", "city": "Helsinki", "country": "Finland", "lat": 60.3172, "lon": 24.9633, "congestion": 0.52},
    {"iata": "DUB", "name": "Dublin Airport", "city": "Dublin", "country": "Ireland", "lat": 53.4264, "lon": -6.2499, "congestion": 0.65},
    {"iata": "VCE", "name": "Venice Marco Polo", "city": "Venice", "country": "Italy", "lat": 45.5053, "lon": 12.3519, "congestion": 0.55},
    {"iata": "NAP", "name": "Naples International", "city": "Naples", "country": "Italy", "lat": 40.8860, "lon": 14.2908, "congestion": 0.52},
    {"iata": "PMI", "name": "Palma de Mallorca Airport", "city": "Palma", "country": "Spain", "lat": 39.5517, "lon": 2.7388, "congestion": 0.62},
    {"iata": "AGP", "name": "Malaga Airport", "city": "Malaga", "country": "Spain", "lat": 36.6749, "lon": -4.4991, "congestion": 0.55},
    {"iata": "SVQ", "name": "Seville Airport", "city": "Seville", "country": "Spain", "lat": 37.4180, "lon": -5.8931, "congestion": 0.48},
    {"iata": "BIO", "name": "Bilbao Airport", "city": "Bilbao", "country": "Spain", "lat": 43.3011, "lon": -2.9106, "congestion": 0.45},
    
    # More Asian Airports
    {"iata": "ICN", "name": "Incheon International", "city": "Seoul", "country": "South Korea", "lat": 37.4602, "lon": 126.4407, "congestion": 0.82},
    {"iata": "GMP", "name": "Gimpo International", "city": "Seoul", "country": "South Korea", "lat": 37.5583, "lon": 126.7906, "congestion": 0.72},
    {"iata": "CJU", "name": "Jeju International", "city": "Jeju", "country": "South Korea", "lat": 33.5114, "lon": 126.4929, "congestion": 0.55},
    {"iata": "PUS", "name": "Gimhae International", "city": "Busan", "country": "South Korea", "lat": 35.1795, "lon": 128.9382, "congestion": 0.58},
    {"iata": "TPE", "name": "Taiwan Taoyuan International", "city": "Taipei", "country": "Taiwan", "lat": 25.0797, "lon": 121.2342, "congestion": 0.75},
    {"iata": "TSA", "name": "Taipei Songshan", "city": "Taipei", "country": "Taiwan", "lat": 25.0694, "lon": 121.5525, "congestion": 0.58},
    {"iata": "KHH", "name": "Kaohsiung International", "city": "Kaohsiung", "country": "Taiwan", "lat": 22.5771, "lon": 120.3500, "congestion": 0.52},
    {"iata": "HAN", "name": "Noi Bai International", "city": "Hanoi", "country": "Vietnam", "lat": 21.2212, "lon": 105.8072, "congestion": 0.65},
    {"iata": "SGN", "name": "Tan Son Nhat International", "city": "Ho Chi Minh City", "country": "Vietnam", "lat": 10.8188, "lon": 106.6520, "congestion": 0.72},
    {"iata": "DAD", "name": "Da Nang International", "city": "Da Nang", "country": "Vietnam", "lat": 16.0439, "lon": 108.1992, "congestion": 0.52},
    {"iata": "PNH", "name": "Phnom Penh International", "city": "Phnom Penh", "country": "Cambodia", "lat": 11.5466, "lon": 104.8441, "congestion": 0.48},
    {"iata": "REP", "name": "Siem Reap International", "city": "Siem Reap", "country": "Cambodia", "lat": 13.4106, "lon": 103.8128, "congestion": 0.42},
    {"iata": "RGN", "name": "Yangon International", "city": "Yangon", "country": "Myanmar", "lat": 16.9073, "lon": 96.1332, "congestion": 0.52},
    {"iata": "VTE", "name": "Wattay International", "city": "Vientiane", "country": "Laos", "lat": 17.9883, "lon": 102.5633, "congestion": 0.35},
    {"iata": "CMB", "name": "Bandaranaike International", "city": "Colombo", "country": "Sri Lanka", "lat": 7.1808, "lon": 79.8841, "congestion": 0.58},
    {"iata": "CCU", "name": "Netaji Subhas Chandra Bose", "city": "Kolkata", "country": "India", "lat": 22.6547, "lon": 88.4467, "congestion": 0.65},
    {"iata": "HYD", "name": "Rajiv Gandhi International", "city": "Hyderabad", "country": "India", "lat": 17.2403, "lon": 78.4294, "congestion": 0.58},
    {"iata": "AMD", "name": "Sardar Vallabhbhai Patel", "city": "Ahmedabad", "country": "India", "lat": 23.0772, "lon": 72.6347, "congestion": 0.52},
    {"iata": "GOI", "name": "Goa International", "city": "Goa", "country": "India", "lat": 15.3808, "lon": 73.8314, "congestion": 0.48},
    {"iata": "COK", "name": "Cochin International", "city": "Kochi", "country": "India", "lat": 10.1520, "lon": 76.4019, "congestion": 0.52},
    {"iata": "KTM", "name": "Tribhuvan International", "city": "Kathmandu", "country": "Nepal", "lat": 27.6966, "lon": 85.3591, "congestion": 0.55},
    {"iata": "DAC", "name": "Hazrat Shahjalal International", "city": "Dhaka", "country": "Bangladesh", "lat": 23.8433, "lon": 90.3978, "congestion": 0.68},
    {"iata": "ISB", "name": "Islamabad International", "city": "Islamabad", "country": "Pakistan", "lat": 33.5607, "lon": 72.8498, "congestion": 0.58},
    {"iata": "KHI", "name": "Jinnah International", "city": "Karachi", "country": "Pakistan", "lat": 24.9065, "lon": 67.1609, "congestion": 0.65},
    {"iata": "LHE", "name": "Allama Iqbal International", "city": "Lahore", "country": "Pakistan", "lat": 31.5216, "lon": 74.4036, "congestion": 0.58},
    
    # More African Airports
    {"iata": "DUR", "name": "King Shaka International", "city": "Durban", "country": "South Africa", "lat": -29.6144, "lon": 31.1197, "congestion": 0.48},
    {"iata": "ACC", "name": "Kotoka International", "city": "Accra", "country": "Ghana", "lat": 5.6052, "lon": -0.1668, "congestion": 0.55},
    {"iata": "ABV", "name": "Nnamdi Azikiwe International", "city": "Abuja", "country": "Nigeria", "lat": 9.0065, "lon": 7.2632, "congestion": 0.52},
    {"iata": "DSS", "name": "Blaise Diagne International", "city": "Dakar", "country": "Senegal", "lat": 14.6708, "lon": -17.0667, "congestion": 0.48},
    {"iata": "EBB", "name": "Entebbe International", "city": "Entebbe", "country": "Uganda", "lat": 0.0424, "lon": 32.4435, "congestion": 0.45},
    {"iata": "DAR", "name": "Julius Nyerere International", "city": "Dar es Salaam", "country": "Tanzania", "lat": -6.8781, "lon": 39.2026, "congestion": 0.48},
    {"iata": "MBA", "name": "Moi International", "city": "Mombasa", "country": "Kenya", "lat": -4.0348, "lon": 39.5942, "congestion": 0.42},
    {"iata": "TUN", "name": "Tunis Carthage International", "city": "Tunis", "country": "Tunisia", "lat": 36.8510, "lon": 10.2272, "congestion": 0.52},
    {"iata": "ALG", "name": "Houari Boumediene Airport", "city": "Algiers", "country": "Algeria", "lat": 36.6910, "lon": 3.2154, "congestion": 0.55},
    {"iata": "RAK", "name": "Marrakech Menara Airport", "city": "Marrakech", "country": "Morocco", "lat": 31.6069, "lon": -8.0363, "congestion": 0.52},
    {"iata": "MRU", "name": "Sir Seewoosagur Ramgoolam", "city": "Mauritius", "country": "Mauritius", "lat": -20.4302, "lon": 57.6836, "congestion": 0.55},
    {"iata": "SEZ", "name": "Seychelles International", "city": "Mahe", "country": "Seychelles", "lat": -4.6743, "lon": 55.5218, "congestion": 0.45},
    
    # More South American Airports
    {"iata": "CNF", "name": "Belo Horizonte International", "city": "Belo Horizonte", "country": "Brazil", "lat": -19.6244, "lon": -43.9719, "congestion": 0.52},
    {"iata": "POA", "name": "Porto Alegre International", "city": "Porto Alegre", "country": "Brazil", "lat": -29.9944, "lon": -51.1714, "congestion": 0.48},
    {"iata": "REC", "name": "Recife/Guararapes International", "city": "Recife", "country": "Brazil", "lat": -8.1264, "lon": -34.9236, "congestion": 0.52},
    {"iata": "FOR", "name": "Fortaleza Pinto Martins", "city": "Fortaleza", "country": "Brazil", "lat": -3.7763, "lon": -38.5326, "congestion": 0.48},
    {"iata": "CWB", "name": "Curitiba International", "city": "Curitiba", "country": "Brazil", "lat": -25.5285, "lon": -49.1758, "congestion": 0.45},
    {"iata": "SDU", "name": "Santos Dumont Airport", "city": "Rio de Janeiro", "country": "Brazil", "lat": -22.9105, "lon": -43.1631, "congestion": 0.58},
    {"iata": "CGH", "name": "Congonhas Airport", "city": "Sao Paulo", "country": "Brazil", "lat": -23.6261, "lon": -46.6564, "congestion": 0.72},
    {"iata": "COR", "name": "Ingeniero Ambrosio Taravella", "city": "Cordoba", "country": "Argentina", "lat": -31.3236, "lon": -64.2081, "congestion": 0.48},
    {"iata": "AEP", "name": "Jorge Newbery Airfield", "city": "Buenos Aires", "country": "Argentina", "lat": -34.5592, "lon": -58.4156, "congestion": 0.65},
    {"iata": "MVD", "name": "Carrasco International", "city": "Montevideo", "country": "Uruguay", "lat": -34.8384, "lon": -56.0308, "congestion": 0.48},
    {"iata": "ASU", "name": "Silvio Pettirossi International", "city": "Asuncion", "country": "Paraguay", "lat": -25.2400, "lon": -57.5200, "congestion": 0.42},
    {"iata": "VVI", "name": "Viru Viru International", "city": "Santa Cruz", "country": "Bolivia", "lat": -17.6448, "lon": -63.1354, "congestion": 0.45},
    {"iata": "LPB", "name": "El Alto International", "city": "La Paz", "country": "Bolivia", "lat": -16.5133, "lon": -68.1922, "congestion": 0.42},
    {"iata": "CUZ", "name": "Alejandro Velasco Astete", "city": "Cusco", "country": "Peru", "lat": -13.5357, "lon": -71.9388, "congestion": 0.52},
    {"iata": "MDE", "name": "Jose Maria Cordova International", "city": "Medellin", "country": "Colombia", "lat": 6.1645, "lon": -75.4231, "congestion": 0.55},
    {"iata": "CLO", "name": "Alfonso Bonilla Aragon", "city": "Cali", "country": "Colombia", "lat": 3.5432, "lon": -76.3816, "congestion": 0.48},
    {"iata": "CTG", "name": "Rafael Nunez International", "city": "Cartagena", "country": "Colombia", "lat": 10.4424, "lon": -75.5130, "congestion": 0.52},
    {"iata": "GYE", "name": "Jose Joaquin de Olmedo", "city": "Guayaquil", "country": "Ecuador", "lat": -2.1574, "lon": -79.8837, "congestion": 0.52},
    {"iata": "PTY", "name": "Tocumen International", "city": "Panama City", "country": "Panama", "lat": 9.0714, "lon": -79.3835, "congestion": 0.62},
    {"iata": "SJO", "name": "Juan Santamaria International", "city": "San Jose", "country": "Costa Rica", "lat": 9.9939, "lon": -84.2088, "congestion": 0.55},
    {"iata": "GUA", "name": "La Aurora International", "city": "Guatemala City", "country": "Guatemala", "lat": 14.5833, "lon": -90.5275, "congestion": 0.52},
    {"iata": "SAL", "name": "El Salvador International", "city": "San Salvador", "country": "El Salvador", "lat": 13.4409, "lon": -89.0557, "congestion": 0.48},
    {"iata": "TGU", "name": "Toncontin International", "city": "Tegucigalpa", "country": "Honduras", "lat": 14.0608, "lon": -87.2172, "congestion": 0.42},
    {"iata": "MGA", "name": "Augusto C. Sandino", "city": "Managua", "country": "Nicaragua", "lat": 12.1415, "lon": -86.1682, "congestion": 0.40},
    
    # Middle East & Central Asia
    {"iata": "AMM", "name": "Queen Alia International", "city": "Amman", "country": "Jordan", "lat": 31.7226, "lon": 35.9932, "congestion": 0.55},
    {"iata": "BEY", "name": "Beirut Rafic Hariri", "city": "Beirut", "country": "Lebanon", "lat": 33.8209, "lon": 35.4884, "congestion": 0.52},
    {"iata": "BAH", "name": "Bahrain International", "city": "Manama", "country": "Bahrain", "lat": 26.2708, "lon": 50.6336, "congestion": 0.55},
    {"iata": "MCT", "name": "Muscat International", "city": "Muscat", "country": "Oman", "lat": 23.5933, "lon": 58.2844, "congestion": 0.52},
    {"iata": "KWI", "name": "Kuwait International", "city": "Kuwait City", "country": "Kuwait", "lat": 29.2266, "lon": 47.9689, "congestion": 0.58},
    {"iata": "IKA", "name": "Imam Khomeini International", "city": "Tehran", "country": "Iran", "lat": 35.4161, "lon": 51.1522, "congestion": 0.62},
    {"iata": "TAS", "name": "Tashkent International", "city": "Tashkent", "country": "Uzbekistan", "lat": 41.2579, "lon": 69.2812, "congestion": 0.48},
    {"iata": "ALA", "name": "Almaty International", "city": "Almaty", "country": "Kazakhstan", "lat": 43.3521, "lon": 77.0405, "congestion": 0.52},
    {"iata": "TSE", "name": "Astana International", "city": "Astana", "country": "Kazakhstan", "lat": 51.0222, "lon": 71.4669, "congestion": 0.45},
    {"iata": "TBS", "name": "Tbilisi International", "city": "Tbilisi", "country": "Georgia", "lat": 41.6692, "lon": 44.9547, "congestion": 0.48},
    {"iata": "EVN", "name": "Zvartnots International", "city": "Yerevan", "country": "Armenia", "lat": 40.1473, "lon": 44.3959, "congestion": 0.45},
    {"iata": "GYD", "name": "Heydar Aliyev International", "city": "Baku", "country": "Azerbaijan", "lat": 40.4675, "lon": 50.0467, "congestion": 0.52},
    
    # CHINA - Major Airports
    {"iata": "PEK", "name": "Beijing Capital International", "city": "Beijing", "country": "China", "lat": 40.0799, "lon": 116.6031, "congestion": 0.92},
    {"iata": "PKX", "name": "Beijing Daxing International", "city": "Beijing", "country": "China", "lat": 39.5098, "lon": 116.4105, "congestion": 0.78},
    {"iata": "PVG", "name": "Shanghai Pudong International", "city": "Shanghai", "country": "China", "lat": 31.1443, "lon": 121.8083, "congestion": 0.88},
    {"iata": "SHA", "name": "Shanghai Hongqiao International", "city": "Shanghai", "country": "China", "lat": 31.1979, "lon": 121.3363, "congestion": 0.82},
    {"iata": "CAN", "name": "Guangzhou Baiyun International", "city": "Guangzhou", "country": "China", "lat": 23.3924, "lon": 113.2988, "congestion": 0.85},
    {"iata": "SZX", "name": "Shenzhen Bao'an International", "city": "Shenzhen", "country": "China", "lat": 22.6393, "lon": 113.8108, "congestion": 0.80},
    {"iata": "CTU", "name": "Chengdu Shuangliu International", "city": "Chengdu", "country": "China", "lat": 30.5785, "lon": 103.9471, "congestion": 0.78},
    {"iata": "TFU", "name": "Chengdu Tianfu International", "city": "Chengdu", "country": "China", "lat": 30.3197, "lon": 104.4412, "congestion": 0.65},
    {"iata": "KMG", "name": "Kunming Changshui International", "city": "Kunming", "country": "China", "lat": 25.1019, "lon": 102.9292, "congestion": 0.72},
    {"iata": "XIY", "name": "Xi'an Xianyang International", "city": "Xi'an", "country": "China", "lat": 34.4471, "lon": 108.7516, "congestion": 0.75},
    {"iata": "HGH", "name": "Hangzhou Xiaoshan International", "city": "Hangzhou", "country": "China", "lat": 30.2295, "lon": 120.4344, "congestion": 0.72},
    {"iata": "NKG", "name": "Nanjing Lukou International", "city": "Nanjing", "country": "China", "lat": 31.7420, "lon": 118.8620, "congestion": 0.68},
    {"iata": "CKG", "name": "Chongqing Jiangbei International", "city": "Chongqing", "country": "China", "lat": 29.7192, "lon": 106.6417, "congestion": 0.75},
    {"iata": "WUH", "name": "Wuhan Tianhe International", "city": "Wuhan", "country": "China", "lat": 30.7838, "lon": 114.2081, "congestion": 0.70},
    {"iata": "TSN", "name": "Tianjin Binhai International", "city": "Tianjin", "country": "China", "lat": 39.1244, "lon": 117.3469, "congestion": 0.65},
    {"iata": "SHE", "name": "Shenyang Taoxian International", "city": "Shenyang", "country": "China", "lat": 41.6398, "lon": 123.4833, "congestion": 0.62},
    {"iata": "DLC", "name": "Dalian Zhoushuizi International", "city": "Dalian", "country": "China", "lat": 38.9657, "lon": 121.5386, "congestion": 0.58},
    {"iata": "TAO", "name": "Qingdao Jiaodong International", "city": "Qingdao", "country": "China", "lat": 36.2661, "lon": 120.3744, "congestion": 0.62},
    {"iata": "XMN", "name": "Xiamen Gaoqi International", "city": "Xiamen", "country": "China", "lat": 24.5440, "lon": 118.1277, "congestion": 0.65},
    {"iata": "NNG", "name": "Nanning Wuxu International", "city": "Nanning", "country": "China", "lat": 22.6083, "lon": 108.1722, "congestion": 0.55},
    {"iata": "HAK", "name": "Haikou Meilan International", "city": "Haikou", "country": "China", "lat": 19.9349, "lon": 110.4590, "congestion": 0.58},
    {"iata": "SYX", "name": "Sanya Phoenix International", "city": "Sanya", "country": "China", "lat": 18.3029, "lon": 109.4122, "congestion": 0.62},
    {"iata": "CGO", "name": "Zhengzhou Xinzheng International", "city": "Zhengzhou", "country": "China", "lat": 34.5197, "lon": 113.8408, "congestion": 0.65},
    {"iata": "CSX", "name": "Changsha Huanghua International", "city": "Changsha", "country": "China", "lat": 28.1892, "lon": 113.2200, "congestion": 0.62},
    {"iata": "URC", "name": "Urumqi Diwopu International", "city": "Urumqi", "country": "China", "lat": 43.9071, "lon": 87.4742, "congestion": 0.55},
    {"iata": "HRB", "name": "Harbin Taiping International", "city": "Harbin", "country": "China", "lat": 45.6234, "lon": 126.2503, "congestion": 0.58},
    {"iata": "FOC", "name": "Fuzhou Changle International", "city": "Fuzhou", "country": "China", "lat": 25.9351, "lon": 119.6633, "congestion": 0.55},
    {"iata": "LXA", "name": "Lhasa Gonggar Airport", "city": "Lhasa", "country": "China", "lat": 29.2978, "lon": 90.9119, "congestion": 0.42},
    
    # JAPAN - All Major Airports
    {"iata": "NRT", "name": "Narita International", "city": "Tokyo", "country": "Japan", "lat": 35.7720, "lon": 140.3929, "congestion": 0.85},
    {"iata": "HND", "name": "Tokyo Haneda", "city": "Tokyo", "country": "Japan", "lat": 35.5494, "lon": 139.7798, "congestion": 0.90},
    {"iata": "KIX", "name": "Kansai International", "city": "Osaka", "country": "Japan", "lat": 34.4347, "lon": 135.2441, "congestion": 0.78},
    {"iata": "ITM", "name": "Osaka Itami", "city": "Osaka", "country": "Japan", "lat": 34.7855, "lon": 135.4380, "congestion": 0.72},
    {"iata": "NGO", "name": "Chubu Centrair International", "city": "Nagoya", "country": "Japan", "lat": 34.8584, "lon": 136.8125, "congestion": 0.68},
    {"iata": "FUK", "name": "Fukuoka Airport", "city": "Fukuoka", "country": "Japan", "lat": 33.5859, "lon": 130.4511, "congestion": 0.72},
    {"iata": "CTS", "name": "New Chitose Airport", "city": "Sapporo", "country": "Japan", "lat": 42.7752, "lon": 141.6925, "congestion": 0.68},
    {"iata": "OKA", "name": "Naha Airport", "city": "Okinawa", "country": "Japan", "lat": 26.1958, "lon": 127.6459, "congestion": 0.65},
    {"iata": "HIJ", "name": "Hiroshima Airport", "city": "Hiroshima", "country": "Japan", "lat": 34.4361, "lon": 132.9194, "congestion": 0.52},
    {"iata": "KOJ", "name": "Kagoshima Airport", "city": "Kagoshima", "country": "Japan", "lat": 31.8034, "lon": 130.7194, "congestion": 0.48},
    {"iata": "SDJ", "name": "Sendai Airport", "city": "Sendai", "country": "Japan", "lat": 38.1397, "lon": 140.9170, "congestion": 0.52},
    {"iata": "KMQ", "name": "Komatsu Airport", "city": "Kanazawa", "country": "Japan", "lat": 36.3946, "lon": 136.4067, "congestion": 0.45},
    {"iata": "MYJ", "name": "Matsuyama Airport", "city": "Matsuyama", "country": "Japan", "lat": 33.8272, "lon": 132.6997, "congestion": 0.42},
    {"iata": "NGS", "name": "Nagasaki Airport", "city": "Nagasaki", "country": "Japan", "lat": 32.9169, "lon": 129.9136, "congestion": 0.45},
    {"iata": "TAK", "name": "Takamatsu Airport", "city": "Takamatsu", "country": "Japan", "lat": 34.2142, "lon": 134.0156, "congestion": 0.40},
    {"iata": "OIT", "name": "Oita Airport", "city": "Oita", "country": "Japan", "lat": 33.4794, "lon": 131.7372, "congestion": 0.38},
    {"iata": "KMI", "name": "Miyazaki Airport", "city": "Miyazaki", "country": "Japan", "lat": 31.8772, "lon": 131.4486, "congestion": 0.40},
    {"iata": "NKM", "name": "Nagoya Komaki Airport", "city": "Nagoya", "country": "Japan", "lat": 35.2550, "lon": 136.9239, "congestion": 0.38},
    {"iata": "AOJ", "name": "Aomori Airport", "city": "Aomori", "country": "Japan", "lat": 40.7347, "lon": 140.6908, "congestion": 0.35},
    {"iata": "AKJ", "name": "Asahikawa Airport", "city": "Asahikawa", "country": "Japan", "lat": 43.6708, "lon": 142.4475, "congestion": 0.35},
    
    # RUSSIA - Major Airports
    {"iata": "SVO", "name": "Sheremetyevo International", "city": "Moscow", "country": "Russia", "lat": 55.9726, "lon": 37.4146, "congestion": 0.82},
    {"iata": "DME", "name": "Domodedovo International", "city": "Moscow", "country": "Russia", "lat": 55.4088, "lon": 37.9063, "congestion": 0.78},
    {"iata": "VKO", "name": "Vnukovo International", "city": "Moscow", "country": "Russia", "lat": 55.5915, "lon": 37.2615, "congestion": 0.72},
    {"iata": "LED", "name": "Pulkovo Airport", "city": "St. Petersburg", "country": "Russia", "lat": 59.8003, "lon": 30.2625, "congestion": 0.70},
    {"iata": "SVX", "name": "Koltsovo Airport", "city": "Yekaterinburg", "country": "Russia", "lat": 56.7431, "lon": 60.8027, "congestion": 0.55},
    {"iata": "OVB", "name": "Tolmachevo Airport", "city": "Novosibirsk", "country": "Russia", "lat": 55.0126, "lon": 82.6507, "congestion": 0.52},
    {"iata": "KJA", "name": "Yemelyanovo Airport", "city": "Krasnoyarsk", "country": "Russia", "lat": 56.1729, "lon": 92.4933, "congestion": 0.48},
    {"iata": "VVO", "name": "Vladivostok International", "city": "Vladivostok", "country": "Russia", "lat": 43.3990, "lon": 132.1483, "congestion": 0.52},
    {"iata": "IKT", "name": "Irkutsk International", "city": "Irkutsk", "country": "Russia", "lat": 52.2680, "lon": 104.3889, "congestion": 0.45},
    {"iata": "KHV", "name": "Khabarovsk Novy Airport", "city": "Khabarovsk", "country": "Russia", "lat": 48.5280, "lon": 135.1883, "congestion": 0.48},
    {"iata": "UFA", "name": "Ufa International", "city": "Ufa", "country": "Russia", "lat": 54.5575, "lon": 55.8744, "congestion": 0.45},
    {"iata": "ROV", "name": "Platov International", "city": "Rostov-on-Don", "country": "Russia", "lat": 47.4939, "lon": 39.9247, "congestion": 0.50},
    {"iata": "AER", "name": "Sochi International", "city": "Sochi", "country": "Russia", "lat": 43.4499, "lon": 39.9566, "congestion": 0.58},
    {"iata": "KZN", "name": "Kazan International", "city": "Kazan", "country": "Russia", "lat": 55.6062, "lon": 49.2787, "congestion": 0.52},
    {"iata": "GOJ", "name": "Strigino International", "city": "Nizhny Novgorod", "country": "Russia", "lat": 56.2301, "lon": 43.7840, "congestion": 0.45},
    {"iata": "KGD", "name": "Khrabrovo Airport", "city": "Kaliningrad", "country": "Russia", "lat": 54.8900, "lon": 20.5926, "congestion": 0.48},
    {"iata": "PKC", "name": "Petropavlovsk-Kamchatsky", "city": "Petropavlovsk", "country": "Russia", "lat": 53.1679, "lon": 158.4536, "congestion": 0.35},
    
    # More Canadian Airports
    {"iata": "YOW", "name": "Ottawa Macdonald-Cartier", "city": "Ottawa", "country": "Canada", "lat": 45.3225, "lon": -75.6692, "congestion": 0.55},
    {"iata": "YWG", "name": "Winnipeg James Armstrong Richardson", "city": "Winnipeg", "country": "Canada", "lat": 49.9100, "lon": -97.2399, "congestion": 0.48},
    {"iata": "YHZ", "name": "Halifax Stanfield International", "city": "Halifax", "country": "Canada", "lat": 44.8808, "lon": -63.5086, "congestion": 0.45},
    {"iata": "YQB", "name": "Quebec City Jean Lesage", "city": "Quebec City", "country": "Canada", "lat": 46.7911, "lon": -71.3933, "congestion": 0.42},
    {"iata": "YXE", "name": "Saskatoon John G. Diefenbaker", "city": "Saskatoon", "country": "Canada", "lat": 52.1708, "lon": -106.6997, "congestion": 0.38},
    {"iata": "YQR", "name": "Regina International", "city": "Regina", "country": "Canada", "lat": 50.4319, "lon": -104.6658, "congestion": 0.35},
    {"iata": "YYT", "name": "St. John's International", "city": "St. John's", "country": "Canada", "lat": 47.6186, "lon": -52.7519, "congestion": 0.38},
    {"iata": "YKA", "name": "Kamloops Airport", "city": "Kamloops", "country": "Canada", "lat": 50.7022, "lon": -120.4444, "congestion": 0.32},
    {"iata": "YLW", "name": "Kelowna International", "city": "Kelowna", "country": "Canada", "lat": 49.9561, "lon": -119.3778, "congestion": 0.42},
    {"iata": "YXX", "name": "Abbotsford International", "city": "Abbotsford", "country": "Canada", "lat": 49.0253, "lon": -122.3611, "congestion": 0.38},
    {"iata": "YYJ", "name": "Victoria International", "city": "Victoria", "country": "Canada", "lat": 48.6469, "lon": -123.4258, "congestion": 0.45},
    {"iata": "YXS", "name": "Prince George Airport", "city": "Prince George", "country": "Canada", "lat": 53.8894, "lon": -122.6789, "congestion": 0.28},
    {"iata": "YZF", "name": "Yellowknife Airport", "city": "Yellowknife", "country": "Canada", "lat": 62.4628, "lon": -114.4403, "congestion": 0.25},
    {"iata": "YXY", "name": "Erik Nielsen Whitehorse", "city": "Whitehorse", "country": "Canada", "lat": 60.7096, "lon": -135.0675, "congestion": 0.22},
    
    # More Mexican Airports
    {"iata": "MTY", "name": "Monterrey International", "city": "Monterrey", "country": "Mexico", "lat": 25.7785, "lon": -100.1069, "congestion": 0.62},
    {"iata": "TIJ", "name": "Tijuana International", "city": "Tijuana", "country": "Mexico", "lat": 32.5411, "lon": -116.9700, "congestion": 0.58},
    {"iata": "SJD", "name": "Los Cabos International", "city": "San Jose del Cabo", "country": "Mexico", "lat": 23.1518, "lon": -109.7215, "congestion": 0.55},
    {"iata": "PVR", "name": "Puerto Vallarta International", "city": "Puerto Vallarta", "country": "Mexico", "lat": 20.6801, "lon": -105.2544, "congestion": 0.58},
    {"iata": "MID", "name": "Merida International", "city": "Merida", "country": "Mexico", "lat": 20.9370, "lon": -89.6577, "congestion": 0.48},
    {"iata": "CZM", "name": "Cozumel International", "city": "Cozumel", "country": "Mexico", "lat": 20.5224, "lon": -86.9256, "congestion": 0.42},
    {"iata": "HMO", "name": "Hermosillo International", "city": "Hermosillo", "country": "Mexico", "lat": 29.0959, "lon": -111.0478, "congestion": 0.42},
    {"iata": "BJX", "name": "Del Bajio International", "city": "Leon", "country": "Mexico", "lat": 20.9935, "lon": -101.4808, "congestion": 0.48},
    {"iata": "OAX", "name": "Oaxaca International", "city": "Oaxaca", "country": "Mexico", "lat": 16.9999, "lon": -96.7266, "congestion": 0.35},
    {"iata": "CUL", "name": "Culiacan International", "city": "Culiacan", "country": "Mexico", "lat": 24.7645, "lon": -107.4749, "congestion": 0.40},
    {"iata": "ACA", "name": "Acapulco International", "city": "Acapulco", "country": "Mexico", "lat": 16.7571, "lon": -99.7540, "congestion": 0.45},
    {"iata": "ZIH", "name": "Ixtapa-Zihuatanejo International", "city": "Zihuatanejo", "country": "Mexico", "lat": 17.6016, "lon": -101.4606, "congestion": 0.38},
    
    # More Caribbean & Central America
    {"iata": "HAV", "name": "Jose Marti International", "city": "Havana", "country": "Cuba", "lat": 22.9892, "lon": -82.4091, "congestion": 0.62},
    {"iata": "VRA", "name": "Juan Gualberto Gomez", "city": "Varadero", "country": "Cuba", "lat": 23.0344, "lon": -81.4353, "congestion": 0.52},
    {"iata": "SDQ", "name": "Las Americas International", "city": "Santo Domingo", "country": "Dominican Republic", "lat": 18.4297, "lon": -69.6689, "congestion": 0.58},
    {"iata": "STI", "name": "Cibao International", "city": "Santiago", "country": "Dominican Republic", "lat": 19.4061, "lon": -70.6047, "congestion": 0.45},
    {"iata": "KIN", "name": "Norman Manley International", "city": "Kingston", "country": "Jamaica", "lat": 17.9357, "lon": -76.7875, "congestion": 0.52},
    {"iata": "AUA", "name": "Queen Beatrix International", "city": "Oranjestad", "country": "Aruba", "lat": 12.5014, "lon": -70.0152, "congestion": 0.55},
    {"iata": "CUR", "name": "Curacao International", "city": "Willemstad", "country": "Curacao", "lat": 12.1889, "lon": -68.9598, "congestion": 0.48},
    {"iata": "SXM", "name": "Princess Juliana International", "city": "Philipsburg", "country": "Sint Maarten", "lat": 18.0410, "lon": -63.1089, "congestion": 0.52},
    {"iata": "POS", "name": "Piarco International", "city": "Port of Spain", "country": "Trinidad", "lat": 10.5954, "lon": -61.3372, "congestion": 0.52},
    {"iata": "BGI", "name": "Grantley Adams International", "city": "Bridgetown", "country": "Barbados", "lat": 13.0746, "lon": -59.4925, "congestion": 0.55},
    {"iata": "GND", "name": "Maurice Bishop International", "city": "St. George's", "country": "Grenada", "lat": 12.0042, "lon": -61.7862, "congestion": 0.42},
    {"iata": "UVF", "name": "Hewanorra International", "city": "Vieux Fort", "country": "Saint Lucia", "lat": 13.7332, "lon": -60.9526, "congestion": 0.48},
    {"iata": "ANU", "name": "V.C. Bird International", "city": "St. John's", "country": "Antigua", "lat": 17.1367, "lon": -61.7926, "congestion": 0.50},
    {"iata": "BDA", "name": "L.F. Wade International", "city": "Hamilton", "country": "Bermuda", "lat": 32.3640, "lon": -64.6787, "congestion": 0.52},
    {"iata": "GCM", "name": "Owen Roberts International", "city": "George Town", "country": "Cayman Islands", "lat": 19.2928, "lon": -81.3577, "congestion": 0.55},
    {"iata": "FPO", "name": "Grand Bahama International", "city": "Freeport", "country": "Bahamas", "lat": 26.5587, "lon": -78.6956, "congestion": 0.42},
    {"iata": "BZE", "name": "Philip S.W. Goldson International", "city": "Belize City", "country": "Belize", "lat": 17.5391, "lon": -88.3082, "congestion": 0.42},
    {"iata": "RTB", "name": "Juan Manuel Galvez International", "city": "Roatan", "country": "Honduras", "lat": 16.3168, "lon": -86.5230, "congestion": 0.38},
    
    # Pacific Islands & Oceania
    {"iata": "NAN", "name": "Nadi International", "city": "Nadi", "country": "Fiji", "lat": -17.7554, "lon": 177.4436, "congestion": 0.52},
    {"iata": "SUV", "name": "Nausori International", "city": "Suva", "country": "Fiji", "lat": -18.0433, "lon": 178.5592, "congestion": 0.38},
    {"iata": "PPT", "name": "Tahiti Faa'a International", "city": "Papeete", "country": "French Polynesia", "lat": -17.5537, "lon": -149.6073, "congestion": 0.52},
    {"iata": "GUM", "name": "Antonio B. Won Pat International", "city": "Hagatna", "country": "Guam", "lat": 13.4834, "lon": 144.7959, "congestion": 0.55},
    {"iata": "SPN", "name": "Francisco C. Ada/Saipan", "city": "Saipan", "country": "Northern Mariana Islands", "lat": 15.1190, "lon": 145.7295, "congestion": 0.42},
    {"iata": "APW", "name": "Faleolo International", "city": "Apia", "country": "Samoa", "lat": -13.8299, "lon": -172.0078, "congestion": 0.38},
    {"iata": "TBU", "name": "Fua'amotu International", "city": "Nuku'alofa", "country": "Tonga", "lat": -21.2412, "lon": -175.1497, "congestion": 0.35},
    {"iata": "VLI", "name": "Bauerfield International", "city": "Port Vila", "country": "Vanuatu", "lat": -17.6993, "lon": 168.3199, "congestion": 0.38},
    {"iata": "HIR", "name": "Honiara International", "city": "Honiara", "country": "Solomon Islands", "lat": -9.4280, "lon": 160.0549, "congestion": 0.32},
    {"iata": "POM", "name": "Jacksons International", "city": "Port Moresby", "country": "Papua New Guinea", "lat": -9.4434, "lon": 147.2200, "congestion": 0.52},
    {"iata": "ROR", "name": "Roman Tmetuchl International", "city": "Koror", "country": "Palau", "lat": 7.3674, "lon": 134.5443, "congestion": 0.38},
    {"iata": "INU", "name": "Nauru International", "city": "Yaren", "country": "Nauru", "lat": -0.5472, "lon": 166.9191, "congestion": 0.25},
    {"iata": "TRW", "name": "Bonriki International", "city": "Tarawa", "country": "Kiribati", "lat": 1.3816, "lon": 173.1470, "congestion": 0.28},
    {"iata": "RAR", "name": "Rarotonga International", "city": "Avarua", "country": "Cook Islands", "lat": -21.2027, "lon": -159.8061, "congestion": 0.42},
    {"iata": "CHC", "name": "Christchurch International", "city": "Christchurch", "country": "New Zealand", "lat": -43.4894, "lon": 172.5322, "congestion": 0.55},
    {"iata": "ZQN", "name": "Queenstown Airport", "city": "Queenstown", "country": "New Zealand", "lat": -45.0211, "lon": 168.7392, "congestion": 0.52},
    {"iata": "DUD", "name": "Dunedin Airport", "city": "Dunedin", "country": "New Zealand", "lat": -45.9281, "lon": 170.1975, "congestion": 0.38},
    
    # More Australian Airports
    {"iata": "ADL", "name": "Adelaide Airport", "city": "Adelaide", "country": "Australia", "lat": -34.9450, "lon": 138.5306, "congestion": 0.55},
    {"iata": "CNS", "name": "Cairns Airport", "city": "Cairns", "country": "Australia", "lat": -16.8858, "lon": 145.7553, "congestion": 0.52},
    {"iata": "OOL", "name": "Gold Coast Airport", "city": "Gold Coast", "country": "Australia", "lat": -28.1644, "lon": 153.5047, "congestion": 0.55},
    {"iata": "CBR", "name": "Canberra Airport", "city": "Canberra", "country": "Australia", "lat": -35.3069, "lon": 149.1950, "congestion": 0.45},
    {"iata": "HBA", "name": "Hobart International", "city": "Hobart", "country": "Australia", "lat": -42.8361, "lon": 147.5103, "congestion": 0.42},
    {"iata": "DRW", "name": "Darwin International", "city": "Darwin", "country": "Australia", "lat": -12.4147, "lon": 130.8769, "congestion": 0.45},
    {"iata": "TSV", "name": "Townsville Airport", "city": "Townsville", "country": "Australia", "lat": -19.2525, "lon": 146.7653, "congestion": 0.38},
    {"iata": "NTL", "name": "Newcastle Airport", "city": "Newcastle", "country": "Australia", "lat": -32.7953, "lon": 151.8347, "congestion": 0.42},
    {"iata": "LST", "name": "Launceston Airport", "city": "Launceston", "country": "Australia", "lat": -41.5453, "lon": 147.2142, "congestion": 0.35},
    {"iata": "ASP", "name": "Alice Springs Airport", "city": "Alice Springs", "country": "Australia", "lat": -23.8067, "lon": 133.9028, "congestion": 0.32},
    {"iata": "AYQ", "name": "Ayers Rock Airport", "city": "Uluru", "country": "Australia", "lat": -25.1861, "lon": 130.9756, "congestion": 0.35},
    {"iata": "MCY", "name": "Sunshine Coast Airport", "city": "Maroochydore", "country": "Australia", "lat": -26.6033, "lon": 153.0914, "congestion": 0.42},
    
    # More Southeast Asian Airports
    {"iata": "DPS", "name": "Ngurah Rai International", "city": "Bali", "country": "Indonesia", "lat": -8.7482, "lon": 115.1672, "congestion": 0.72},
    {"iata": "SUB", "name": "Juanda International", "city": "Surabaya", "country": "Indonesia", "lat": -7.3798, "lon": 112.7868, "congestion": 0.62},
    {"iata": "UPG", "name": "Sultan Hasanuddin International", "city": "Makassar", "country": "Indonesia", "lat": -5.0617, "lon": 119.5542, "congestion": 0.52},
    {"iata": "BDO", "name": "Husein Sastranegara International", "city": "Bandung", "country": "Indonesia", "lat": -6.9006, "lon": 107.5764, "congestion": 0.55},
    {"iata": "JOG", "name": "Adisucipto International", "city": "Yogyakarta", "country": "Indonesia", "lat": -7.7882, "lon": 110.4317, "congestion": 0.52},
    {"iata": "PEN", "name": "Penang International", "city": "Penang", "country": "Malaysia", "lat": 5.2972, "lon": 100.2767, "congestion": 0.55},
    {"iata": "LGK", "name": "Langkawi International", "city": "Langkawi", "country": "Malaysia", "lat": 6.3297, "lon": 99.7286, "congestion": 0.48},
    {"iata": "BKI", "name": "Kota Kinabalu International", "city": "Kota Kinabalu", "country": "Malaysia", "lat": 5.9372, "lon": 116.0519, "congestion": 0.52},
    {"iata": "KCH", "name": "Kuching International", "city": "Kuching", "country": "Malaysia", "lat": 1.4847, "lon": 110.3472, "congestion": 0.48},
    {"iata": "DMK", "name": "Don Mueang International", "city": "Bangkok", "country": "Thailand", "lat": 13.9126, "lon": 100.6068, "congestion": 0.72},
    {"iata": "HKT", "name": "Phuket International", "city": "Phuket", "country": "Thailand", "lat": 8.1132, "lon": 98.3169, "congestion": 0.68},
    {"iata": "CNX", "name": "Chiang Mai International", "city": "Chiang Mai", "country": "Thailand", "lat": 18.7668, "lon": 98.9626, "congestion": 0.58},
    {"iata": "USM", "name": "Samui Airport", "city": "Koh Samui", "country": "Thailand", "lat": 9.5478, "lon": 100.0622, "congestion": 0.52},
    {"iata": "KBV", "name": "Krabi International", "city": "Krabi", "country": "Thailand", "lat": 8.0986, "lon": 98.9861, "congestion": 0.52},
    {"iata": "CEB", "name": "Mactan-Cebu International", "city": "Cebu", "country": "Philippines", "lat": 10.3076, "lon": 123.9792, "congestion": 0.62},
    {"iata": "DVO", "name": "Francisco Bangoy International", "city": "Davao", "country": "Philippines", "lat": 7.1255, "lon": 125.6456, "congestion": 0.52},
    {"iata": "CRK", "name": "Clark International", "city": "Angeles", "country": "Philippines", "lat": 15.1860, "lon": 120.5603, "congestion": 0.55},
    {"iata": "ILO", "name": "Iloilo International", "city": "Iloilo", "country": "Philippines", "lat": 10.7133, "lon": 122.5454, "congestion": 0.42},
    {"iata": "PPS", "name": "Puerto Princesa International", "city": "Puerto Princesa", "country": "Philippines", "lat": 9.7421, "lon": 118.7587, "congestion": 0.42},
    {"iata": "TAG", "name": "Tagbilaran Airport", "city": "Tagbilaran", "country": "Philippines", "lat": 9.6641, "lon": 123.8533, "congestion": 0.35},
    
    # More European Regional
    {"iata": "STN", "name": "London Stansted", "city": "London", "country": "UK", "lat": 51.8850, "lon": 0.2350, "congestion": 0.72},
    {"iata": "LTN", "name": "London Luton", "city": "London", "country": "UK", "lat": 51.8747, "lon": -0.3683, "congestion": 0.68},
    {"iata": "BRS", "name": "Bristol Airport", "city": "Bristol", "country": "UK", "lat": 51.3827, "lon": -2.7190, "congestion": 0.52},
    {"iata": "BHX", "name": "Birmingham Airport", "city": "Birmingham", "country": "UK", "lat": 52.4539, "lon": -1.7480, "congestion": 0.58},
    {"iata": "GLA", "name": "Glasgow Airport", "city": "Glasgow", "country": "UK", "lat": 55.8719, "lon": -4.4331, "congestion": 0.55},
    {"iata": "BFS", "name": "Belfast International", "city": "Belfast", "country": "UK", "lat": 54.6575, "lon": -6.2158, "congestion": 0.48},
    {"iata": "NCL", "name": "Newcastle International", "city": "Newcastle", "country": "UK", "lat": 55.0375, "lon": -1.6917, "congestion": 0.48},
    {"iata": "LPL", "name": "Liverpool John Lennon", "city": "Liverpool", "country": "UK", "lat": 53.3336, "lon": -2.8497, "congestion": 0.52},
    {"iata": "SNN", "name": "Shannon Airport", "city": "Shannon", "country": "Ireland", "lat": 52.7020, "lon": -8.9248, "congestion": 0.42},
    {"iata": "ORK", "name": "Cork Airport", "city": "Cork", "country": "Ireland", "lat": 51.8413, "lon": -8.4911, "congestion": 0.45},
    {"iata": "MRS", "name": "Marseille Provence Airport", "city": "Marseille", "country": "France", "lat": 43.4393, "lon": 5.2214, "congestion": 0.55},
    {"iata": "TLS", "name": "Toulouse-Blagnac Airport", "city": "Toulouse", "country": "France", "lat": 43.6291, "lon": 1.3678, "congestion": 0.52},
    {"iata": "BOD", "name": "Bordeaux-Merignac Airport", "city": "Bordeaux", "country": "France", "lat": 44.8283, "lon": -0.7156, "congestion": 0.48},
    {"iata": "NTE", "name": "Nantes Atlantique Airport", "city": "Nantes", "country": "France", "lat": 47.1569, "lon": -1.6108, "congestion": 0.45},
    {"iata": "STR", "name": "Stuttgart Airport", "city": "Stuttgart", "country": "Germany", "lat": 48.6899, "lon": 9.2220, "congestion": 0.55},
    {"iata": "CGN", "name": "Cologne Bonn Airport", "city": "Cologne", "country": "Germany", "lat": 50.8659, "lon": 7.1427, "congestion": 0.58},
    {"iata": "NUE", "name": "Nuremberg Airport", "city": "Nuremberg", "country": "Germany", "lat": 49.4987, "lon": 11.0669, "congestion": 0.45},
    {"iata": "LEJ", "name": "Leipzig/Halle Airport", "city": "Leipzig", "country": "Germany", "lat": 51.4324, "lon": 12.2416, "congestion": 0.48},
    {"iata": "HAN", "name": "Hannover Airport", "city": "Hannover", "country": "Germany", "lat": 52.4611, "lon": 9.6850, "congestion": 0.48},
    {"iata": "BRE", "name": "Bremen Airport", "city": "Bremen", "country": "Germany", "lat": 53.0475, "lon": 8.7867, "congestion": 0.42},
    {"iata": "PSA", "name": "Pisa International", "city": "Pisa", "country": "Italy", "lat": 43.6839, "lon": 10.3927, "congestion": 0.52},
    {"iata": "CTA", "name": "Catania-Fontanarossa", "city": "Catania", "country": "Italy", "lat": 37.4668, "lon": 15.0664, "congestion": 0.55},
    {"iata": "BLQ", "name": "Bologna Guglielmo Marconi", "city": "Bologna", "country": "Italy", "lat": 44.5354, "lon": 11.2887, "congestion": 0.52},
    {"iata": "TRN", "name": "Turin Airport", "city": "Turin", "country": "Italy", "lat": 45.2008, "lon": 7.6496, "congestion": 0.48},
    {"iata": "GOT", "name": "Gothenburg Landvetter", "city": "Gothenburg", "country": "Sweden", "lat": 57.6628, "lon": 12.2798, "congestion": 0.48},
    {"iata": "BGO", "name": "Bergen Airport Flesland", "city": "Bergen", "country": "Norway", "lat": 60.2934, "lon": 5.2181, "congestion": 0.45},
    {"iata": "TRD", "name": "Trondheim Airport Vaernes", "city": "Trondheim", "country": "Norway", "lat": 63.4578, "lon": 10.9239, "congestion": 0.40},
    {"iata": "SVG", "name": "Stavanger Airport Sola", "city": "Stavanger", "country": "Norway", "lat": 58.8767, "lon": 5.6378, "congestion": 0.42},
    {"iata": "AAL", "name": "Aalborg Airport", "city": "Aalborg", "country": "Denmark", "lat": 57.0928, "lon": 9.8492, "congestion": 0.38},
    {"iata": "BLL", "name": "Billund Airport", "city": "Billund", "country": "Denmark", "lat": 55.7403, "lon": 9.1518, "congestion": 0.42},
    {"iata": "TMP", "name": "Tampere-Pirkkala Airport", "city": "Tampere", "country": "Finland", "lat": 61.4141, "lon": 23.6044, "congestion": 0.35},
    {"iata": "OUL", "name": "Oulu Airport", "city": "Oulu", "country": "Finland", "lat": 64.9301, "lon": 25.3546, "congestion": 0.32},
    {"iata": "TLL", "name": "Tallinn Airport", "city": "Tallinn", "country": "Estonia", "lat": 59.4133, "lon": 24.8328, "congestion": 0.48},
    {"iata": "RIX", "name": "Riga International", "city": "Riga", "country": "Latvia", "lat": 56.9236, "lon": 23.9711, "congestion": 0.48},
    {"iata": "VNO", "name": "Vilnius International", "city": "Vilnius", "country": "Lithuania", "lat": 54.6341, "lon": 25.2858, "congestion": 0.45},
    {"iata": "OTP", "name": "Henri Coanda International", "city": "Bucharest", "country": "Romania", "lat": 44.5711, "lon": 26.0850, "congestion": 0.55},
    {"iata": "CLJ", "name": "Cluj International", "city": "Cluj-Napoca", "country": "Romania", "lat": 46.7852, "lon": 23.6862, "congestion": 0.45},
    {"iata": "SOF", "name": "Sofia Airport", "city": "Sofia", "country": "Bulgaria", "lat": 42.6967, "lon": 23.4114, "congestion": 0.52},
    {"iata": "VAR", "name": "Varna Airport", "city": "Varna", "country": "Bulgaria", "lat": 43.2321, "lon": 27.8251, "congestion": 0.42},
    {"iata": "BEG", "name": "Belgrade Nikola Tesla", "city": "Belgrade", "country": "Serbia", "lat": 44.8184, "lon": 20.3091, "congestion": 0.52},
    {"iata": "ZAG", "name": "Zagreb Airport", "city": "Zagreb", "country": "Croatia", "lat": 45.7429, "lon": 16.0688, "congestion": 0.48},
    {"iata": "SPU", "name": "Split Airport", "city": "Split", "country": "Croatia", "lat": 43.5389, "lon": 16.2980, "congestion": 0.52},
    {"iata": "DBV", "name": "Dubrovnik Airport", "city": "Dubrovnik", "country": "Croatia", "lat": 42.5614, "lon": 18.2682, "congestion": 0.55},
    {"iata": "LJU", "name": "Ljubljana Joze Pucnik", "city": "Ljubljana", "country": "Slovenia", "lat": 46.2237, "lon": 14.4576, "congestion": 0.42},
    {"iata": "SKP", "name": "Skopje International", "city": "Skopje", "country": "North Macedonia", "lat": 41.9616, "lon": 21.6214, "congestion": 0.42},
    {"iata": "TIA", "name": "Tirana International", "city": "Tirana", "country": "Albania", "lat": 41.4147, "lon": 19.7206, "congestion": 0.45},
    {"iata": "SKG", "name": "Thessaloniki Airport", "city": "Thessaloniki", "country": "Greece", "lat": 40.5197, "lon": 22.9709, "congestion": 0.55},
    {"iata": "HER", "name": "Heraklion International", "city": "Heraklion", "country": "Greece", "lat": 35.3397, "lon": 25.1803, "congestion": 0.58},
    {"iata": "RHO", "name": "Rhodes International", "city": "Rhodes", "country": "Greece", "lat": 36.4054, "lon": 28.0862, "congestion": 0.52},
    {"iata": "CFU", "name": "Corfu International", "city": "Corfu", "country": "Greece", "lat": 39.6019, "lon": 19.9117, "congestion": 0.48},
    {"iata": "JMK", "name": "Mykonos Airport", "city": "Mykonos", "country": "Greece", "lat": 37.4351, "lon": 25.3481, "congestion": 0.52},
    {"iata": "JTR", "name": "Santorini Airport", "city": "Santorini", "country": "Greece", "lat": 36.3992, "lon": 25.4793, "congestion": 0.55},
    {"iata": "LCA", "name": "Larnaca International", "city": "Larnaca", "country": "Cyprus", "lat": 34.8751, "lon": 33.6249, "congestion": 0.55},
    {"iata": "PFO", "name": "Paphos International", "city": "Paphos", "country": "Cyprus", "lat": 34.7180, "lon": 32.4857, "congestion": 0.48},
    {"iata": "MLA", "name": "Malta International", "city": "Valletta", "country": "Malta", "lat": 35.8575, "lon": 14.4775, "congestion": 0.55},
    {"iata": "LUX", "name": "Luxembourg Airport", "city": "Luxembourg", "country": "Luxembourg", "lat": 49.6233, "lon": 6.2044, "congestion": 0.48},
    {"iata": "KEF", "name": "Keflavik International", "city": "Reykjavik", "country": "Iceland", "lat": 63.9850, "lon": -22.6056, "congestion": 0.55},
    {"iata": "FAO", "name": "Faro Airport", "city": "Faro", "country": "Portugal", "lat": 37.0144, "lon": -7.9659, "congestion": 0.55},
    {"iata": "FNC", "name": "Madeira Airport", "city": "Funchal", "country": "Portugal", "lat": 32.6979, "lon": -16.7745, "congestion": 0.52},
    {"iata": "PDL", "name": "Ponta Delgada Airport", "city": "Ponta Delgada", "country": "Portugal", "lat": 37.7412, "lon": -25.6979, "congestion": 0.42},
    {"iata": "TFS", "name": "Tenerife South Airport", "city": "Tenerife", "country": "Spain", "lat": 28.0445, "lon": -16.5725, "congestion": 0.58},
    {"iata": "TFN", "name": "Tenerife North Airport", "city": "Tenerife", "country": "Spain", "lat": 28.4827, "lon": -16.3415, "congestion": 0.48},
    {"iata": "LPA", "name": "Gran Canaria Airport", "city": "Las Palmas", "country": "Spain", "lat": 27.9319, "lon": -15.3866, "congestion": 0.58},
    {"iata": "ACE", "name": "Lanzarote Airport", "city": "Arrecife", "country": "Spain", "lat": 28.9455, "lon": -13.6052, "congestion": 0.52},
    {"iata": "FUE", "name": "Fuerteventura Airport", "city": "Puerto del Rosario", "country": "Spain", "lat": 28.4527, "lon": -13.8638, "congestion": 0.48},
    {"iata": "IBZ", "name": "Ibiza Airport", "city": "Ibiza", "country": "Spain", "lat": 38.8729, "lon": 1.3731, "congestion": 0.58},
    {"iata": "MAH", "name": "Menorca Airport", "city": "Mahon", "country": "Spain", "lat": 39.8626, "lon": 4.2186, "congestion": 0.48},
    {"iata": "VLC", "name": "Valencia Airport", "city": "Valencia", "country": "Spain", "lat": 39.4893, "lon": -0.4816, "congestion": 0.55},
    {"iata": "ALC", "name": "Alicante-Elche Airport", "city": "Alicante", "country": "Spain", "lat": 38.2822, "lon": -0.5582, "congestion": 0.58},
    
    # SOUTH AMERICA - Brazil & Region
    {"iata": "MAO", "name": "Eduardo Gomes International", "city": "Manaus", "country": "Brazil", "lat": -3.0386, "lon": -60.0497, "congestion": 0.52},
    {"iata": "BEL", "name": "Val de Cans International", "city": "Belem", "country": "Brazil", "lat": -1.3792, "lon": -48.4763, "congestion": 0.48},
    {"iata": "SLZ", "name": "Marechal Cunha Machado", "city": "Sao Luis", "country": "Brazil", "lat": -2.5853, "lon": -44.2341, "congestion": 0.42},
    {"iata": "THE", "name": "Teresina Airport", "city": "Teresina", "country": "Brazil", "lat": -5.0599, "lon": -42.8235, "congestion": 0.35},
    {"iata": "NAT", "name": "Sao Goncalo do Amarante", "city": "Natal", "country": "Brazil", "lat": -5.7680, "lon": -35.3651, "congestion": 0.45},
    {"iata": "JPA", "name": "Presidente Castro Pinto", "city": "Joao Pessoa", "country": "Brazil", "lat": -7.1461, "lon": -34.9486, "congestion": 0.38},
    {"iata": "MCZ", "name": "Zumbi dos Palmares", "city": "Maceio", "country": "Brazil", "lat": -9.5108, "lon": -35.7917, "congestion": 0.42},
    {"iata": "AJU", "name": "Santa Maria Airport", "city": "Aracaju", "country": "Brazil", "lat": -10.9840, "lon": -37.0703, "congestion": 0.38},
    {"iata": "SSA", "name": "Deputado Luis Eduardo Magalhaes", "city": "Salvador", "country": "Brazil", "lat": -12.9086, "lon": -38.3225, "congestion": 0.62},
    {"iata": "VIX", "name": "Eurico de Aguiar Salles", "city": "Vitoria", "country": "Brazil", "lat": -20.2581, "lon": -40.2864, "congestion": 0.45},
    {"iata": "CGR", "name": "Campo Grande International", "city": "Campo Grande", "country": "Brazil", "lat": -20.4687, "lon": -54.6725, "congestion": 0.42},
    {"iata": "CGB", "name": "Marechal Rondon International", "city": "Cuiaba", "country": "Brazil", "lat": -15.6529, "lon": -56.1167, "congestion": 0.45},
    {"iata": "GYN", "name": "Santa Genoveva Airport", "city": "Goiania", "country": "Brazil", "lat": -16.6320, "lon": -49.2206, "congestion": 0.48},
    {"iata": "PVH", "name": "Governador Jorge Teixeira", "city": "Porto Velho", "country": "Brazil", "lat": -8.7093, "lon": -63.9024, "congestion": 0.35},
    {"iata": "RBR", "name": "Placido de Castro International", "city": "Rio Branco", "country": "Brazil", "lat": -9.8689, "lon": -67.8981, "congestion": 0.32},
    {"iata": "FLN", "name": "Hercilio Luz International", "city": "Florianopolis", "country": "Brazil", "lat": -27.6703, "lon": -48.5525, "congestion": 0.52},
    {"iata": "IGU", "name": "Foz do Iguacu International", "city": "Foz do Iguacu", "country": "Brazil", "lat": -25.5963, "lon": -54.4872, "congestion": 0.48},
    {"iata": "LDB", "name": "Governador Jose Richa", "city": "Londrina", "country": "Brazil", "lat": -23.3336, "lon": -51.1301, "congestion": 0.38},
    {"iata": "MGF", "name": "Silvio Name Junior", "city": "Maringa", "country": "Brazil", "lat": -23.4761, "lon": -52.0122, "congestion": 0.35},
    {"iata": "JOI", "name": "Lauro Carneiro de Loyola", "city": "Joinville", "country": "Brazil", "lat": -26.2245, "lon": -48.7974, "congestion": 0.38},
    {"iata": "NVT", "name": "Ministro Victor Konder", "city": "Navegantes", "country": "Brazil", "lat": -26.8800, "lon": -48.6514, "congestion": 0.42},
    {"iata": "PMW", "name": "Brigadeiro Lysias Rodrigues", "city": "Palmas", "country": "Brazil", "lat": -10.2915, "lon": -48.3570, "congestion": 0.32},
    {"iata": "STM", "name": "Maestro Wilson Fonseca", "city": "Santarem", "country": "Brazil", "lat": -2.4247, "lon": -54.7859, "congestion": 0.28},
    {"iata": "MCP", "name": "Alberto Alcolumbre International", "city": "Macapa", "country": "Brazil", "lat": 0.0507, "lon": -51.0722, "congestion": 0.32},
    {"iata": "BVB", "name": "Atlas Brasil Cantanhede", "city": "Boa Vista", "country": "Brazil", "lat": 2.8413, "lon": -60.6922, "congestion": 0.28},
    
    # More Argentina & Paraguay
    {"iata": "MDZ", "name": "El Plumerillo International", "city": "Mendoza", "country": "Argentina", "lat": -32.8317, "lon": -68.7929, "congestion": 0.48},
    {"iata": "SLA", "name": "Martin Miguel de Guemes", "city": "Salta", "country": "Argentina", "lat": -24.8560, "lon": -65.4862, "congestion": 0.42},
    {"iata": "TUC", "name": "Teniente Benjamin Matienzo", "city": "Tucuman", "country": "Argentina", "lat": -26.8409, "lon": -65.1049, "congestion": 0.40},
    {"iata": "IGR", "name": "Cataratas del Iguazu", "city": "Puerto Iguazu", "country": "Argentina", "lat": -25.7373, "lon": -54.4734, "congestion": 0.45},
    {"iata": "BRC", "name": "San Carlos de Bariloche", "city": "Bariloche", "country": "Argentina", "lat": -41.1512, "lon": -71.1575, "congestion": 0.48},
    {"iata": "USH", "name": "Malvinas Argentinas", "city": "Ushuaia", "country": "Argentina", "lat": -54.8433, "lon": -68.2958, "congestion": 0.42},
    {"iata": "CTC", "name": "Coronel Felipe Varela", "city": "Catamarca", "country": "Argentina", "lat": -28.5956, "lon": -65.7517, "congestion": 0.28},
    {"iata": "NQN", "name": "Presidente Peron International", "city": "Neuquen", "country": "Argentina", "lat": -38.9490, "lon": -68.1557, "congestion": 0.42},
    {"iata": "RGL", "name": "Piloto Civil Norberto Fernandez", "city": "Rio Gallegos", "country": "Argentina", "lat": -51.6089, "lon": -69.3126, "congestion": 0.32},
    {"iata": "FTE", "name": "Comandante Armando Tola", "city": "El Calafate", "country": "Argentina", "lat": -50.2803, "lon": -72.0531, "congestion": 0.45},
    
    # GREENLAND
    {"iata": "SFJ", "name": "Kangerlussuaq Airport", "city": "Kangerlussuaq", "country": "Greenland", "lat": 67.0122, "lon": -50.7116, "congestion": 0.25},
    {"iata": "GOH", "name": "Nuuk Airport", "city": "Nuuk", "country": "Greenland", "lat": 64.1909, "lon": -51.6781, "congestion": 0.28},
    {"iata": "JAV", "name": "Ilulissat Airport", "city": "Ilulissat", "country": "Greenland", "lat": 69.2432, "lon": -51.0571, "congestion": 0.22},
    {"iata": "THU", "name": "Thule Air Base", "city": "Pituffik", "country": "Greenland", "lat": 76.5312, "lon": -68.7032, "congestion": 0.15},
    {"iata": "UAK", "name": "Narsarsuaq Airport", "city": "Narsarsuaq", "country": "Greenland", "lat": 61.1605, "lon": -45.4260, "congestion": 0.18},
    {"iata": "KUS", "name": "Kulusuk Airport", "city": "Kulusuk", "country": "Greenland", "lat": 65.5736, "lon": -37.1236, "congestion": 0.15},
    
    # CANADA - Northern & Remote
    {"iata": "YFB", "name": "Iqaluit Airport", "city": "Iqaluit", "country": "Canada", "lat": 63.7561, "lon": -68.5558, "congestion": 0.25},
    {"iata": "YYQ", "name": "Churchill Airport", "city": "Churchill", "country": "Canada", "lat": 58.7392, "lon": -94.0650, "congestion": 0.22},
    {"iata": "YEV", "name": "Inuvik Mike Zubko", "city": "Inuvik", "country": "Canada", "lat": 68.3042, "lon": -133.4831, "congestion": 0.20},
    {"iata": "YCB", "name": "Cambridge Bay Airport", "city": "Cambridge Bay", "country": "Canada", "lat": 69.1081, "lon": -105.1383, "congestion": 0.15},
    {"iata": "YRB", "name": "Resolute Bay Airport", "city": "Resolute", "country": "Canada", "lat": 74.7169, "lon": -94.9694, "congestion": 0.12},
    {"iata": "YFS", "name": "Fort Simpson Airport", "city": "Fort Simpson", "country": "Canada", "lat": 61.7602, "lon": -121.2364, "congestion": 0.18},
    {"iata": "YDA", "name": "Dawson City Airport", "city": "Dawson City", "country": "Canada", "lat": 64.0431, "lon": -139.1281, "congestion": 0.15},
    {"iata": "YOJ", "name": "High Level Airport", "city": "High Level", "country": "Canada", "lat": 58.6214, "lon": -117.1647, "congestion": 0.18},
    {"iata": "YMM", "name": "Fort McMurray International", "city": "Fort McMurray", "country": "Canada", "lat": 56.6533, "lon": -111.2219, "congestion": 0.45},
    {"iata": "YQU", "name": "Grande Prairie Airport", "city": "Grande Prairie", "country": "Canada", "lat": 55.1797, "lon": -118.8850, "congestion": 0.38},
    {"iata": "YXJ", "name": "Fort St. John Airport", "city": "Fort St. John", "country": "Canada", "lat": 56.2381, "lon": -120.7403, "congestion": 0.35},
    {"iata": "YPR", "name": "Prince Rupert Airport", "city": "Prince Rupert", "country": "Canada", "lat": 54.2861, "lon": -130.4447, "congestion": 0.28},
    {"iata": "YQQ", "name": "Comox Valley Airport", "city": "Comox", "country": "Canada", "lat": 49.7108, "lon": -124.8867, "congestion": 0.32},
    {"iata": "YCD", "name": "Nanaimo Airport", "city": "Nanaimo", "country": "Canada", "lat": 49.0547, "lon": -123.8700, "congestion": 0.35},
    {"iata": "YXT", "name": "Terrace Airport", "city": "Terrace", "country": "Canada", "lat": 54.4686, "lon": -128.5764, "congestion": 0.28},
    {"iata": "YYE", "name": "Fort Nelson Airport", "city": "Fort Nelson", "country": "Canada", "lat": 58.8364, "lon": -122.5969, "congestion": 0.22},
    {"iata": "YYR", "name": "Goose Bay Airport", "city": "Happy Valley-Goose Bay", "country": "Canada", "lat": 53.3192, "lon": -60.4258, "congestion": 0.28},
    {"iata": "YVO", "name": "Val-d'Or Airport", "city": "Val-d'Or", "country": "Canada", "lat": 48.0533, "lon": -77.7828, "congestion": 0.32},
    {"iata": "YGP", "name": "Gaspe Airport", "city": "Gaspe", "country": "Canada", "lat": 48.7753, "lon": -64.4786, "congestion": 0.22},
    {"iata": "YUL", "name": "Montreal-Trudeau International", "city": "Montreal", "country": "Canada", "lat": 45.4706, "lon": -73.7408, "congestion": 0.72},
    
    # ALASKA
    {"iata": "ANC", "name": "Ted Stevens Anchorage", "city": "Anchorage", "country": "USA", "lat": 61.1743, "lon": -149.9962, "congestion": 0.55},
    {"iata": "FAI", "name": "Fairbanks International", "city": "Fairbanks", "country": "USA", "lat": 64.8151, "lon": -147.8561, "congestion": 0.42},
    {"iata": "JNU", "name": "Juneau International", "city": "Juneau", "country": "USA", "lat": 58.3550, "lon": -134.5762, "congestion": 0.38},
    {"iata": "KTN", "name": "Ketchikan International", "city": "Ketchikan", "country": "USA", "lat": 55.3556, "lon": -131.7139, "congestion": 0.32},
    {"iata": "SIT", "name": "Sitka Rocky Gutierrez", "city": "Sitka", "country": "USA", "lat": 57.0471, "lon": -135.3617, "congestion": 0.28},
    {"iata": "BRW", "name": "Wiley Post-Will Rogers Memorial", "city": "Barrow", "country": "USA", "lat": 71.2854, "lon": -156.7660, "congestion": 0.22},
    {"iata": "OME", "name": "Nome Airport", "city": "Nome", "country": "USA", "lat": 64.5122, "lon": -165.4453, "congestion": 0.25},
    {"iata": "OTZ", "name": "Ralph Wien Memorial", "city": "Kotzebue", "country": "USA", "lat": 66.8847, "lon": -162.5986, "congestion": 0.22},
    {"iata": "BET", "name": "Bethel Airport", "city": "Bethel", "country": "USA", "lat": 60.7798, "lon": -161.8380, "congestion": 0.28},
    {"iata": "ADQ", "name": "Kodiak Airport", "city": "Kodiak", "country": "USA", "lat": 57.7500, "lon": -152.4939, "congestion": 0.32},
    {"iata": "CDV", "name": "Merle K. Smith Airport", "city": "Cordova", "country": "USA", "lat": 60.4917, "lon": -145.4776, "congestion": 0.22},
    {"iata": "YAK", "name": "Yakutat Airport", "city": "Yakutat", "country": "USA", "lat": 59.5033, "lon": -139.6603, "congestion": 0.18},
    {"iata": "DLG", "name": "Dillingham Airport", "city": "Dillingham", "country": "USA", "lat": 59.0447, "lon": -158.5053, "congestion": 0.22},
    {"iata": "AKN", "name": "King Salmon Airport", "city": "King Salmon", "country": "USA", "lat": 58.6768, "lon": -156.6492, "congestion": 0.25},
    {"iata": "DUT", "name": "Unalaska Airport", "city": "Dutch Harbor", "country": "USA", "lat": 53.9001, "lon": -166.5435, "congestion": 0.22},
    {"iata": "ADK", "name": "Adak Airport", "city": "Adak", "country": "USA", "lat": 51.8780, "lon": -176.6461, "congestion": 0.15},
    
    # CENTRAL & NORTHERN AFRICA
    {"iata": "CAI", "name": "Cairo International", "city": "Cairo", "country": "Egypt", "lat": 30.1219, "lon": 31.4056, "congestion": 0.78},
    {"iata": "HRG", "name": "Hurghada International", "city": "Hurghada", "country": "Egypt", "lat": 27.1783, "lon": 33.7994, "congestion": 0.58},
    {"iata": "SSH", "name": "Sharm el-Sheikh International", "city": "Sharm el-Sheikh", "country": "Egypt", "lat": 27.9773, "lon": 34.3950, "congestion": 0.55},
    {"iata": "LXR", "name": "Luxor International", "city": "Luxor", "country": "Egypt", "lat": 25.6710, "lon": 32.7066, "congestion": 0.48},
    {"iata": "ASW", "name": "Aswan International", "city": "Aswan", "country": "Egypt", "lat": 23.9644, "lon": 32.8200, "congestion": 0.38},
    {"iata": "HBE", "name": "Borg El Arab Airport", "city": "Alexandria", "country": "Egypt", "lat": 30.9177, "lon": 29.6964, "congestion": 0.52},
    {"iata": "TIP", "name": "Tripoli International", "city": "Tripoli", "country": "Libya", "lat": 32.6635, "lon": 13.1590, "congestion": 0.45},
    {"iata": "BEN", "name": "Benina International", "city": "Benghazi", "country": "Libya", "lat": 32.0968, "lon": 20.2695, "congestion": 0.38},
    {"iata": "KRT", "name": "Khartoum International", "city": "Khartoum", "country": "Sudan", "lat": 15.5895, "lon": 32.5532, "congestion": 0.52},
    {"iata": "JUB", "name": "Juba International", "city": "Juba", "country": "South Sudan", "lat": 4.8721, "lon": 31.6011, "congestion": 0.42},
    {"iata": "ADD", "name": "Bole International", "city": "Addis Ababa", "country": "Ethiopia", "lat": 8.9779, "lon": 38.7994, "congestion": 0.68},
    {"iata": "ASM", "name": "Asmara International", "city": "Asmara", "country": "Eritrea", "lat": 15.2919, "lon": 38.9107, "congestion": 0.35},
    {"iata": "MGQ", "name": "Aden Adde International", "city": "Mogadishu", "country": "Somalia", "lat": 2.0144, "lon": 45.3047, "congestion": 0.38},
    {"iata": "DJI", "name": "Djibouti-Ambouli International", "city": "Djibouti City", "country": "Djibouti", "lat": 11.5473, "lon": 43.1594, "congestion": 0.42},
    {"iata": "NDJ", "name": "N'Djamena International", "city": "N'Djamena", "country": "Chad", "lat": 12.1337, "lon": 15.0340, "congestion": 0.38},
    {"iata": "OUA", "name": "Ouagadougou Airport", "city": "Ouagadougou", "country": "Burkina Faso", "lat": 12.3532, "lon": -1.5124, "congestion": 0.42},
    {"iata": "NIM", "name": "Diori Hamani International", "city": "Niamey", "country": "Niger", "lat": 13.4815, "lon": 2.1836, "congestion": 0.35},
    {"iata": "BKO", "name": "Modibo Keita International", "city": "Bamako", "country": "Mali", "lat": 12.5335, "lon": -7.9499, "congestion": 0.42},
    {"iata": "NKC", "name": "Nouakchott-Oumtounsy", "city": "Nouakchott", "country": "Mauritania", "lat": 18.3100, "lon": -15.9697, "congestion": 0.35},
    {"iata": "FNA", "name": "Lungi International", "city": "Freetown", "country": "Sierra Leone", "lat": 8.6164, "lon": -13.1956, "congestion": 0.38},
    {"iata": "ROB", "name": "Roberts International", "city": "Monrovia", "country": "Liberia", "lat": 6.2338, "lon": -10.3623, "congestion": 0.35},
    {"iata": "ABJ", "name": "Felix-Houphouet-Boigny", "city": "Abidjan", "country": "Ivory Coast", "lat": 5.2614, "lon": -3.9262, "congestion": 0.55},
    {"iata": "COO", "name": "Cadjehoun Airport", "city": "Cotonou", "country": "Benin", "lat": 6.3573, "lon": 2.3844, "congestion": 0.42},
    {"iata": "LFW", "name": "Lome-Tokoin Airport", "city": "Lome", "country": "Togo", "lat": 6.1656, "lon": 1.2545, "congestion": 0.38},
    {"iata": "DLA", "name": "Douala International", "city": "Douala", "country": "Cameroon", "lat": 4.0061, "lon": 9.7195, "congestion": 0.52},
    {"iata": "NSI", "name": "Yaounde Nsimalen", "city": "Yaounde", "country": "Cameroon", "lat": 3.7226, "lon": 11.5533, "congestion": 0.48},
    {"iata": "LBV", "name": "Leon-Mba International", "city": "Libreville", "country": "Gabon", "lat": 0.4586, "lon": 9.4123, "congestion": 0.45},
    {"iata": "BGF", "name": "Bangui M'Poko International", "city": "Bangui", "country": "Central African Republic", "lat": 4.3985, "lon": 18.5188, "congestion": 0.32},
    {"iata": "BZV", "name": "Maya-Maya Airport", "city": "Brazzaville", "country": "Republic of Congo", "lat": -4.2517, "lon": 15.2530, "congestion": 0.42},
    {"iata": "PNR", "name": "Pointe Noire Airport", "city": "Pointe-Noire", "country": "Republic of Congo", "lat": -4.8160, "lon": 11.8866, "congestion": 0.38},
    {"iata": "FIH", "name": "N'djili International", "city": "Kinshasa", "country": "DR Congo", "lat": -4.3858, "lon": 15.4446, "congestion": 0.55},
    {"iata": "FBM", "name": "Lubumbashi International", "city": "Lubumbashi", "country": "DR Congo", "lat": -11.5913, "lon": 27.5309, "congestion": 0.42},
    {"iata": "KGL", "name": "Kigali International", "city": "Kigali", "country": "Rwanda", "lat": -1.9686, "lon": 30.1395, "congestion": 0.48},
    {"iata": "BJM", "name": "Bujumbura International", "city": "Bujumbura", "country": "Burundi", "lat": -3.3240, "lon": 29.3185, "congestion": 0.35},
    {"iata": "LUN", "name": "Kenneth Kaunda International", "city": "Lusaka", "country": "Zambia", "lat": -15.3308, "lon": 28.4526, "congestion": 0.48},
    {"iata": "LLW", "name": "Lilongwe International", "city": "Lilongwe", "country": "Malawi", "lat": -13.7894, "lon": 33.7811, "congestion": 0.38},
    {"iata": "HRE", "name": "Robert Gabriel Mugabe", "city": "Harare", "country": "Zimbabwe", "lat": -17.9318, "lon": 31.0928, "congestion": 0.48},
    {"iata": "VFA", "name": "Victoria Falls Airport", "city": "Victoria Falls", "country": "Zimbabwe", "lat": -18.0959, "lon": 25.8390, "congestion": 0.42},
    {"iata": "WDH", "name": "Hosea Kutako International", "city": "Windhoek", "country": "Namibia", "lat": -22.4799, "lon": 17.4709, "congestion": 0.42},
    {"iata": "GBE", "name": "Sir Seretse Khama International", "city": "Gaborone", "country": "Botswana", "lat": -24.5552, "lon": 25.9182, "congestion": 0.38},
    {"iata": "MQP", "name": "Kruger Mpumalanga International", "city": "Nelspruit", "country": "South Africa", "lat": -25.3832, "lon": 31.1056, "congestion": 0.42},
    {"iata": "PLZ", "name": "Port Elizabeth Airport", "city": "Port Elizabeth", "country": "South Africa", "lat": -33.9849, "lon": 25.6173, "congestion": 0.45},
    {"iata": "BFN", "name": "Bloemfontein Airport", "city": "Bloemfontein", "country": "South Africa", "lat": -29.0927, "lon": 26.3024, "congestion": 0.38},
    {"iata": "ELS", "name": "East London Airport", "city": "East London", "country": "South Africa", "lat": -33.0356, "lon": 27.8259, "congestion": 0.35},
    
    # MORE MIDDLE EAST
    {"iata": "RUH", "name": "King Khalid International", "city": "Riyadh", "country": "Saudi Arabia", "lat": 24.9576, "lon": 46.6988, "congestion": 0.72},
    {"iata": "JED", "name": "King Abdulaziz International", "city": "Jeddah", "country": "Saudi Arabia", "lat": 21.6796, "lon": 39.1565, "congestion": 0.75},
    {"iata": "DMM", "name": "King Fahd International", "city": "Dammam", "country": "Saudi Arabia", "lat": 26.4712, "lon": 49.7979, "congestion": 0.58},
    {"iata": "MED", "name": "Prince Mohammad bin Abdulaziz", "city": "Medina", "country": "Saudi Arabia", "lat": 24.5534, "lon": 39.7051, "congestion": 0.52},
    {"iata": "AUH", "name": "Abu Dhabi International", "city": "Abu Dhabi", "country": "UAE", "lat": 24.4330, "lon": 54.6511, "congestion": 0.72},
    {"iata": "SHJ", "name": "Sharjah International", "city": "Sharjah", "country": "UAE", "lat": 25.3286, "lon": 55.5172, "congestion": 0.58},
    {"iata": "DWC", "name": "Al Maktoum International", "city": "Dubai", "country": "UAE", "lat": 24.8960, "lon": 55.1614, "congestion": 0.55},
    {"iata": "DOH", "name": "Hamad International", "city": "Doha", "country": "Qatar", "lat": 25.2731, "lon": 51.6081, "congestion": 0.75},
    {"iata": "SLL", "name": "Salalah Airport", "city": "Salalah", "country": "Oman", "lat": 17.0387, "lon": 54.0914, "congestion": 0.38},
    {"iata": "ADE", "name": "Aden International", "city": "Aden", "country": "Yemen", "lat": 12.8295, "lon": 45.0288, "congestion": 0.35},
    {"iata": "SAH", "name": "Sana'a International", "city": "Sana'a", "country": "Yemen", "lat": 15.4763, "lon": 44.2197, "congestion": 0.38},
    {"iata": "BGW", "name": "Baghdad International", "city": "Baghdad", "country": "Iraq", "lat": 33.2625, "lon": 44.2346, "congestion": 0.52},
    {"iata": "BSR", "name": "Basra International", "city": "Basra", "country": "Iraq", "lat": 30.5491, "lon": 47.6621, "congestion": 0.42},
    {"iata": "EBL", "name": "Erbil International", "city": "Erbil", "country": "Iraq", "lat": 36.2376, "lon": 43.9632, "congestion": 0.48},
    {"iata": "NJF", "name": "Al Najaf International", "city": "Najaf", "country": "Iraq", "lat": 31.9896, "lon": 44.4043, "congestion": 0.38},
    {"iata": "SYZ", "name": "Shiraz International", "city": "Shiraz", "country": "Iran", "lat": 29.5392, "lon": 52.5898, "congestion": 0.52},
    {"iata": "MHD", "name": "Mashhad International", "city": "Mashhad", "country": "Iran", "lat": 36.2352, "lon": 59.6410, "congestion": 0.58},
    {"iata": "ISF", "name": "Isfahan International", "city": "Isfahan", "country": "Iran", "lat": 32.7508, "lon": 51.8613, "congestion": 0.48},
    {"iata": "TBZ", "name": "Tabriz International", "city": "Tabriz", "country": "Iran", "lat": 38.1339, "lon": 46.2350, "congestion": 0.45},
    {"iata": "AWZ", "name": "Ahvaz International", "city": "Ahvaz", "country": "Iran", "lat": 31.3374, "lon": 48.7620, "congestion": 0.42},
]

# ============= PYDANTIC MODELS =============
class Aircraft(BaseModel):
    id: str
    brand: str
    model: str
    type: str  # passenger, cargo, both
    capacity: int
    cargo_capacity: int  # kg
    fuel_capacity: int  # liters
    fuel_burn: int  # liters per hour
    range: int  # km
    cruise_speed: int  # km/h
    price: int

class Airport(BaseModel):
    iata: str
    name: str
    city: str
    country: str
    lat: float
    lon: float
    congestion: float

class WeatherCondition(BaseModel):
    airport_iata: str
    condition: str  # clear, cloudy, rain, storm, fog, snow
    wind_speed: int  # km/h
    visibility: float  # km
    temperature: int  # celsius
    delay_hours: float = 0
    extra_cost_percent: float = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class LoanCreate(BaseModel):
    amount: int
    term_months: int  # loan term in months

class Loan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: int
    remaining: float
    interest_rate: float = 0.07  # 7% APR
    monthly_payment: float
    term_months: int
    months_paid: int = 0
    last_payment_month: Optional[int] = None  # Track which month last payment was made
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OwnedAircraft(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aircraft_id: str
    name: str  # Custom name given by player
    current_airport: str  # IATA code
    status: str = "idle"  # idle, flying, maintenance
    purchased_at: datetime = Field(default_factory=datetime.utcnow)

class RouteCreate(BaseModel):
    aircraft_id: str  # Owned aircraft ID
    origin: str  # IATA code
    destination: str  # IATA code
    flight_type: str  # passenger, cargo
    flight_mode: str = "charter"  # charter (Part 135) or scheduled (Part 121)
    ticket_price: Optional[int] = None
    cargo_rate: Optional[int] = None  # $ per kg

class Route(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aircraft_id: str
    origin: str
    destination: str
    distance: float  # km
    flight_type: str
    flight_mode: str = "charter"  # charter or scheduled
    ticket_price: int = 0
    cargo_rate: int = 0
    fuel_required: float
    flight_duration: float  # hours
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    progress: float = 0  # 0 to 1
    revenue: float = 0
    costs: float = 0
    passengers: int = 0
    cargo_weight: int = 0
    is_return_leg: bool = False  # For scheduled flights - is this the return trip?
    parent_route_id: Optional[str] = None  # For scheduled return legs
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GameState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    balance: float = 0
    home_airport: str = ""
    current_date: datetime = Field(default_factory=datetime.utcnow)
    total_revenue: float = 0
    total_expenses: float = 0
    flights_completed: int = 0
    tutorial_seen: bool = False
    theme: str = "dark"  # dark, light
    difficulty: str = ""  # easy, medium, hard
    # Certifications (Hard mode)
    certifications: dict = Field(default_factory=lambda: {
        "medical_certificate": False,          # FAA Class 1 Medical
        "private_pilot": False,                # PPL - Private Pilot License
        "instrument_rating": False,            # IFR Rating
        "commercial_pilot": False,             # CPL - Commercial Pilot License
        "atp_certificate": False,              # ATP - Airline Transport Pilot
        "part_135": False,                     # Part 135 Air Carrier Certificate
        "part_121": False,                     # Part 121 Air Carrier Certificate  
        "drug_testing_program": False,         # DOT Drug & Alcohol Testing
        "dispatcher_certificate": False,       # Aircraft Dispatcher Certificate
    })
    certification_in_progress: Optional[str] = None
    certification_start_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Certification requirements and costs (realistic based on FAA)
CERTIFICATIONS = {
    "medical_certificate": {
        "name": "FAA Class 1 Medical Certificate",
        "form": "FAA Form 8500-8",
        "cost": 200,
        "time_seconds": 10,
        "description": "Required medical examination for all pilots",
        "prerequisites": [],
        "unlocks": "Can begin flight training"
    },
    "private_pilot": {
        "name": "Private Pilot License (PPL)",
        "form": "FAA Form 8710-1",
        "cost": 12000,
        "time_seconds": 30,
        "description": "Basic pilot certification - 40 flight hours minimum",
        "prerequisites": ["medical_certificate"],
        "unlocks": "Can fly single-engine aircraft"
    },
    "instrument_rating": {
        "name": "Instrument Rating (IFR)",
        "form": "FAA Form 8710-1",
        "cost": 8000,
        "time_seconds": 25,
        "description": "Fly in instrument conditions - 50 hours instrument time",
        "prerequisites": ["private_pilot"],
        "unlocks": "Can fly in bad weather/clouds"
    },
    "commercial_pilot": {
        "name": "Commercial Pilot License (CPL)",
        "form": "FAA Form 8710-1",
        "cost": 35000,
        "time_seconds": 45,
        "description": "Fly for compensation - 250 flight hours minimum",
        "prerequisites": ["instrument_rating"],
        "unlocks": "Can fly passengers for money"
    },
    "atp_certificate": {
        "name": "Airline Transport Pilot (ATP)",
        "form": "FAA Form 8710-1 / ATP-CTP",
        "cost": 10000,
        "time_seconds": 30,
        "description": "Highest pilot certificate - 1500 hours total time",
        "prerequisites": ["commercial_pilot"],
        "unlocks": "Can command Part 121 aircraft"
    },
    "drug_testing_program": {
        "name": "DOT Drug & Alcohol Testing Program",
        "form": "DOT Form 49 CFR Part 40",
        "cost": 2500,
        "time_seconds": 15,
        "description": "Required testing program enrollment",
        "prerequisites": ["commercial_pilot"],
        "unlocks": "Compliance for Part 135/121"
    },
    "dispatcher_certificate": {
        "name": "Aircraft Dispatcher Certificate",
        "form": "FAA Form 8060-56",
        "cost": 5000,
        "time_seconds": 20,
        "description": "Required for Part 121 operations",
        "prerequisites": ["commercial_pilot"],
        "unlocks": "Can dispatch Part 121 flights"
    },
    "part_135": {
        "name": "Part 135 Air Carrier Certificate",
        "form": "FAA Form 8400-6 / OpSpecs",
        "cost": 50000,
        "time_seconds": 60,
        "description": "On-demand charter operations certificate",
        "prerequisites": ["commercial_pilot", "drug_testing_program"],
        "unlocks": "Can operate charter flights"
    },
    "part_121": {
        "name": "Part 121 Air Carrier Certificate",
        "form": "FAA Form 8400-6 / WebOPSS",
        "cost": 150000,
        "time_seconds": 90,
        "description": "Scheduled airline operations certificate",
        "prerequisites": ["atp_certificate", "dispatcher_certificate", "drug_testing_program", "part_135"],
        "unlocks": "Full airline operations"
    }
}

class DifficultySelect(BaseModel):
    difficulty: str  # easy, medium, hard
    home_airport: str

class AircraftPurchase(BaseModel):
    aircraft_id: str
    name: str
    use_loan: bool = False
    loan_amount: Optional[int] = None
    loan_term: Optional[int] = None

class SetHomeAirport(BaseModel):
    iata: str

class LoanPayment(BaseModel):
    amount: int

class CalculateProfitRequest(BaseModel):
    aircraft_id: str
    origin: str
    destination: str
    flight_type: str
    ticket_price: Optional[int] = None
    cargo_rate: Optional[int] = None

# ============= HELPER FUNCTIONS =============
def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        result = {}
        for k, v in doc.items():
            if k == "_id":
                result[k] = str(v)
            elif hasattr(v, 'isoformat'):
                result[k] = v.isoformat()
            else:
                result[k] = v
        return result
    return doc

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in km
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def get_aircraft_by_id(aircraft_id: str) -> Optional[dict]:
    """Get aircraft data from database by ID"""
    for brand_aircraft in AIRCRAFT_DATABASE.values():
        for aircraft in brand_aircraft:
            if aircraft["id"] == aircraft_id:
                return aircraft
    return None

def get_airport_by_iata(iata: str) -> Optional[dict]:
    """Get airport data by IATA code"""
    for airport in AIRPORT_DATABASE:
        if airport["iata"] == iata:
            return airport
    return None

def generate_weather(airport_iata: str) -> dict:
    """Generate random weather for an airport"""
    conditions = ["clear", "cloudy", "rain", "storm", "fog", "snow"]
    weights = [0.4, 0.25, 0.15, 0.08, 0.07, 0.05]
    condition = random.choices(conditions, weights=weights)[0]
    
    wind_speed = random.randint(0, 80)
    if condition == "storm":
        wind_speed = random.randint(50, 120)
    
    visibility = {
        "clear": random.uniform(10, 20),
        "cloudy": random.uniform(8, 15),
        "rain": random.uniform(5, 10),
        "storm": random.uniform(1, 5),
        "fog": random.uniform(0.5, 3),
        "snow": random.uniform(2, 8)
    }[condition]
    
    temperature = random.randint(-10, 40)
    
    # Calculate delays and extra costs
    delay_hours = {
        "clear": 0,
        "cloudy": 0,
        "rain": random.uniform(0.1, 0.3),
        "storm": random.uniform(0.5, 2.0),
        "fog": random.uniform(0.3, 1.0),
        "snow": random.uniform(0.2, 0.8)
    }[condition]
    
    extra_cost_percent = {
        "clear": 0,
        "cloudy": 0,
        "rain": 5,
        "storm": 20,
        "fog": 10,
        "snow": 15
    }[condition]
    
    return {
        "airport_iata": airport_iata,
        "condition": condition,
        "wind_speed": wind_speed,
        "visibility": round(visibility, 1),
        "temperature": temperature,
        "delay_hours": round(delay_hours, 2),
        "extra_cost_percent": extra_cost_percent,
        "timestamp": datetime.utcnow()
    }

def find_alternate_airport(exclude_iata: str, lat: float, lon: float) -> dict:
    """Find nearest alternate airport that's not the excluded one"""
    min_distance = float('inf')
    alternate = None
    
    for airport in airports_data:
        if airport["iata"] == exclude_iata:
            continue
        
        # Check if this airport has good weather
        weather = generate_weather(airport["iata"])
        if weather["condition"] == "storm" and weather["wind_speed"] > 50:
            continue  # Skip airports with bad weather too
        
        dist = calculate_distance(lat, lon, airport["lat"], airport["lon"])
        if dist < min_distance and dist < 500:  # Within 500km
            min_distance = dist
            alternate = airport
    
    return alternate

def calculate_monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """Calculate monthly payment for a loan"""
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return principal / months
    payment = principal * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    return round(payment, 2)

def calculate_optimal_ticket_price(distance: float, aircraft: dict, flight_type: str, min_profit: int = 500) -> int:
    """Calculate optimal ticket price that ensures profit even with 1 passenger"""
    flight_duration = distance / aircraft["cruise_speed"]
    fuel_required = flight_duration * aircraft["fuel_burn"]
    
    # AVGas vs Jet-A pricing based on aircraft type
    # AVGas (piston engines - Cessna, Piper): ~$7.00/gallon = $1.85/liter
    # Jet-A (turboprops, jets - Boeing, Airbus): ~$5.50/gallon = $1.45/liter
    piston_aircraft = ["Cessna", "Piper"]
    is_piston = aircraft.get("brand", "") in piston_aircraft
    fuel_price = 1.85 if is_piston else 1.45  # $ per liter (AVGas vs Jet-A)
    
    fuel_cost = fuel_required * fuel_price
    operating_cost = flight_duration * 500  # Base operating cost per hour
    total_cost = fuel_cost + operating_cost
    
    if flight_type == "passenger":
        # Price must cover ALL costs + profit even with just 1 passenger
        # This ensures ANY number of passengers is profitable
        min_price_per_pax = total_cost + min_profit
        # Also add a small per-distance component
        distance_bonus = distance * 0.05
        return int(min_price_per_pax + distance_bonus)
    else:
        # Cargo: rate per kg must cover costs even with minimal cargo (100kg)
        min_cargo = 100
        min_rate = (total_cost + min_profit) / min_cargo
        return int(min_rate) + 1

def calculate_flight_profit(aircraft: dict, distance: float, flight_type: str, ticket_price: int = None, cargo_rate: int = None) -> dict:
    """Calculate expected profit for a flight"""
    flight_duration = distance / aircraft["cruise_speed"]
    fuel_required = flight_duration * aircraft["fuel_burn"]
    
    # AVGas vs Jet-A pricing based on aircraft type
    piston_aircraft = ["Cessna", "Piper"]
    is_piston = aircraft.get("brand", "") in piston_aircraft
    fuel_price = 1.85 if is_piston else 1.45  # $ per liter (AVGas vs Jet-A)
    fuel_type = "AVGas" if is_piston else "Jet-A"
    
    fuel_cost = fuel_required * fuel_price
    operating_cost = flight_duration * 500
    total_cost = fuel_cost + operating_cost
    
    # Get the default price (ensures $500 profit on full plane)
    default_price = calculate_optimal_ticket_price(distance, aircraft, flight_type)
    
    if flight_type == "passenger":
        price = ticket_price if ticket_price else default_price
        avg_passengers = int(aircraft["capacity"] * 0.75)
        full_passengers = aircraft["capacity"]
        revenue = avg_passengers * price
        full_revenue = full_passengers * price
    else:
        rate = cargo_rate if cargo_rate else default_price
        avg_cargo = int(aircraft["cargo_capacity"] * 0.7)
        full_cargo = aircraft["cargo_capacity"]
        revenue = avg_cargo * rate
        full_revenue = full_cargo * rate
    
    profit = revenue - total_cost
    full_profit = full_revenue - total_cost
    
    return {
        "estimated_revenue": round(revenue, 2),
        "estimated_cost": round(total_cost, 2),
        "estimated_profit": round(profit, 2),
        "full_plane_profit": round(full_profit, 2),
        "is_profitable": profit > 0,
        "default_price": default_price,
        "fuel_type": fuel_type,
        "fuel_cost": round(fuel_cost, 2),
        "fuel_price_per_liter": fuel_price,
        "fuel_liters": round(fuel_required, 1)
    }

# ============= API ROUTES =============

@api_router.get("/")
async def root():
    return {"message": "Airline Simulator API"}

# Aircraft routes
@api_router.get("/aircraft", response_model=dict)
async def get_all_aircraft():
    """Get all available aircraft grouped by brand"""
    return AIRCRAFT_DATABASE

@api_router.get("/aircraft/brands", response_model=List[str])
async def get_aircraft_brands():
    """Get list of all aircraft brands"""
    return list(AIRCRAFT_DATABASE.keys())

@api_router.get("/aircraft/owned")
async def get_owned_aircraft():
    """Get all owned aircraft"""
    owned = await db.owned_aircraft.find().to_list(100)
    # Enrich with aircraft details
    result = []
    for o in owned:
        aircraft = get_aircraft_by_id(o["aircraft_id"])
        if aircraft:
            item = serialize_doc(o)
            item["details"] = aircraft
            result.append(item)
    return result

@api_router.get("/aircraft/store/{brand}", response_model=List[dict])
async def get_aircraft_by_brand(brand: str):
    """Get aircraft by brand"""
    if brand not in AIRCRAFT_DATABASE:
        raise HTTPException(status_code=404, detail="Brand not found")
    return AIRCRAFT_DATABASE[brand]

# Airport routes
@api_router.get("/airports", response_model=List[Airport])
async def get_all_airports():
    """Get all airports"""
    return [Airport(**airport) for airport in AIRPORT_DATABASE]

@api_router.get("/airports/search")
async def search_airports(q: str):
    """Search airports by name, city, or IATA code"""
    q = q.lower()
    results = []
    for airport in AIRPORT_DATABASE:
        if (q in airport["iata"].lower() or 
            q in airport["name"].lower() or 
            q in airport["city"].lower()):
            results.append(airport)
    return results

@api_router.get("/airports/{iata}", response_model=Airport)
async def get_airport(iata: str):
    """Get airport by IATA code"""
    airport = get_airport_by_iata(iata.upper())
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return Airport(**airport)

# Weather routes
@api_router.get("/weather/{iata}")
async def get_weather(iata: str):
    """Get current weather for an airport"""
    airport = get_airport_by_iata(iata.upper())
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return generate_weather(iata.upper())

@api_router.get("/weather")
async def get_all_weather():
    """Get weather for all airports"""
    return [generate_weather(airport["iata"]) for airport in AIRPORT_DATABASE]

@api_router.get("/weather/alerts/bad")
async def get_bad_weather_airports():
    """Get airports with poor weather conditions"""
    bad_conditions = ["storm", "fog", "snow", "rain"]
    alerts = []
    for airport in AIRPORT_DATABASE:
        weather = generate_weather(airport["iata"])
        if weather["condition"] in bad_conditions:
            alerts.append({
                **airport,
                "weather": weather
            })
    return alerts

# Game state routes
@api_router.get("/game")
async def get_game_state():
    """Get current game state"""
    game = await db.game_state.find_one()
    if not game:
        # Create new game state
        new_game = GameState(balance=50000).dict()
        await db.game_state.insert_one(new_game)
        game = await db.game_state.find_one()
    return serialize_doc(game)

@api_router.post("/game/reset")
async def reset_game():
    """Reset game to initial state"""
    await db.game_state.delete_many({})
    await db.owned_aircraft.delete_many({})
    await db.loans.delete_many({})
    await db.routes.delete_many({})
    
    new_game = GameState(balance=0).dict()
    await db.game_state.insert_one(new_game)
    game = await db.game_state.find_one()
    return serialize_doc(game)

@api_router.post("/game/start")
async def start_game_with_difficulty(data: DifficultySelect):
    """Start a new game with selected difficulty"""
    airport = get_airport_by_iata(data.home_airport.upper())
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    if data.difficulty not in ["easy", "medium", "hard"]:
        raise HTTPException(status_code=400, detail="Invalid difficulty. Choose: easy, medium, hard")
    
    # Clear existing game data
    await db.game_state.delete_many({})
    await db.owned_aircraft.delete_many({})
    await db.loans.delete_many({})
    await db.routes.delete_many({})
    
    # Set up certifications based on difficulty
    all_certs_complete = {key: True for key in CERTIFICATIONS.keys()}
    all_certs_none = {key: False for key in CERTIFICATIONS.keys()}
    
    # Set up game based on difficulty
    if data.difficulty == "easy":
        # Easy: Start with Cessna 172 + $15,000 + all certifications
        balance = 15000
        certifications = all_certs_complete
        
    elif data.difficulty == "medium":
        # Medium: Start with Cessna 172 + $0 + all certifications
        balance = 0
        certifications = all_certs_complete
        
    else:  # hard
        # Hard: No plane, no money, need to get all certifications
        balance = 0
        certifications = all_certs_none
    
    new_game = GameState(
        balance=balance,
        home_airport=data.home_airport.upper(),
        difficulty=data.difficulty,
        certifications=certifications
    ).dict()
    await db.game_state.insert_one(new_game)
    
    # Give starting plane for easy and medium
    if data.difficulty in ["easy", "medium"]:
        # Find Cessna 172
        cessna_172 = None
        for model in AIRCRAFT_DATABASE.get("Cessna", []):
            if model["model"] == "172 Skyhawk":
                cessna_172 = model
                break
        
        if cessna_172:
            owned_aircraft = {
                "id": str(uuid.uuid4()),
                "aircraft_id": cessna_172["id"],
                "name": "172",
                "home_airport": data.home_airport.upper(),
                "current_airport": data.home_airport.upper(),
                "status": "idle",
                "total_flights": 0,
                "total_distance": 0,
                "purchased_at": datetime.utcnow()
            }
            await db.owned_aircraft.insert_one(owned_aircraft)
    
    game = await db.game_state.find_one()
    return serialize_doc(game)

# Certification endpoints
@api_router.get("/certifications")
async def get_certifications_list():
    """Get all available certifications with their requirements"""
    game = await db.game_state.find_one()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    current_certs = game.get("certifications", {})
    cert_in_progress = game.get("certification_in_progress")
    cert_start_time = game.get("certification_start_time")
    
    result = []
    for cert_id, cert_data in CERTIFICATIONS.items():
        # Check if prerequisites are met
        prereqs_met = all(current_certs.get(prereq, False) for prereq in cert_data["prerequisites"])
        
        # Check if currently training this cert
        training_remaining = 0
        if cert_in_progress == cert_id and cert_start_time:
            start_time = cert_start_time
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            training_remaining = max(0, cert_data["time_seconds"] - elapsed)
        
        result.append({
            "id": cert_id,
            "name": cert_data["name"],
            "form": cert_data["form"],
            "cost": cert_data["cost"],
            "time_seconds": cert_data["time_seconds"],
            "description": cert_data["description"],
            "prerequisites": cert_data["prerequisites"],
            "unlocks": cert_data["unlocks"],
            "completed": current_certs.get(cert_id, False),
            "available": prereqs_met and not current_certs.get(cert_id, False),
            "in_progress": cert_in_progress == cert_id,
            "training_remaining": training_remaining
        })
    
    return result

@api_router.post("/certifications/{cert_id}/start")
async def start_certification(cert_id: str):
    """Start a certification training"""
    if cert_id not in CERTIFICATIONS:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    game = await db.game_state.find_one()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    current_certs = game.get("certifications", {})
    cert_data = CERTIFICATIONS[cert_id]
    
    # Check if already has this cert
    if current_certs.get(cert_id):
        raise HTTPException(status_code=400, detail="You already have this certification")
    
    # Check if another cert is in progress
    if game.get("certification_in_progress"):
        raise HTTPException(status_code=400, detail="Another certification is in progress. Complete it first.")
    
    # Check prerequisites
    for prereq in cert_data["prerequisites"]:
        if not current_certs.get(prereq):
            prereq_name = CERTIFICATIONS[prereq]["name"]
            raise HTTPException(status_code=400, detail=f"You need {prereq_name} first")
    
    # Check balance
    if game["balance"] < cert_data["cost"]:
        raise HTTPException(status_code=400, detail=f"You need ${cert_data['cost']:,} for this certification. Take a loan!")
    
    # Deduct cost and start training
    await db.game_state.update_one({}, {
        "$inc": {"balance": -cert_data["cost"], "total_expenses": cert_data["cost"]},
        "$set": {
            "certification_in_progress": cert_id,
            "certification_start_time": datetime.utcnow()
        }
    })
    
    return {
        "message": f"Started training for {cert_data['name']}. Come back in {cert_data['time_seconds']} seconds.",
        "certification": cert_id,
        "time_seconds": cert_data["time_seconds"]
    }

@api_router.post("/certifications/{cert_id}/complete")
async def complete_certification(cert_id: str):
    """Check and complete a certification if training is done"""
    if cert_id not in CERTIFICATIONS:
        raise HTTPException(status_code=404, detail="Certification not found")
    
    game = await db.game_state.find_one()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check if this cert is in progress
    if game.get("certification_in_progress") != cert_id:
        raise HTTPException(status_code=400, detail="This certification is not in progress")
    
    cert_data = CERTIFICATIONS[cert_id]
    start_time = game.get("certification_start_time")
    
    if not start_time:
        raise HTTPException(status_code=400, detail="Certification not started")
    
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    
    elapsed = (datetime.utcnow() - start_time).total_seconds()
    
    if elapsed < cert_data["time_seconds"]:
        remaining = cert_data["time_seconds"] - elapsed
        return {
            "complete": False,
            "remaining": remaining,
            "message": f"Training in progress... {int(remaining)} seconds remaining"
        }
    
    # Complete the certification
    current_certs = game.get("certifications", {})
    current_certs[cert_id] = True
    
    await db.game_state.update_one({}, {
        "$set": {
            "certifications": current_certs,
            "certification_in_progress": None,
            "certification_start_time": None
        }
    })
    
    return {
        "complete": True,
        "message": f"Congratulations! You've earned your {cert_data['name']}!",
        "unlocks": cert_data["unlocks"]
    }

@api_router.get("/certifications/status")
async def get_certification_status():
    """Get current certification training status"""
    game = await db.game_state.find_one()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    current_certs = game.get("certifications", {})
    cert_in_progress = game.get("certification_in_progress")
    cert_start_time = game.get("certification_start_time")
    
    # Check if training is complete
    if cert_in_progress and cert_start_time:
        cert_data = CERTIFICATIONS[cert_in_progress]
        start_time = cert_start_time
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        
        if elapsed >= cert_data["time_seconds"]:
            # Auto-complete
            current_certs[cert_in_progress] = True
            await db.game_state.update_one({}, {
                "$set": {
                    "certifications": current_certs,
                    "certification_in_progress": None,
                    "certification_start_time": None
                }
            })
            return {
                "in_progress": None,
                "remaining": 0,
                "just_completed": cert_in_progress,
                "certifications": current_certs
            }
        else:
            return {
                "in_progress": cert_in_progress,
                "remaining": max(0, cert_data["time_seconds"] - elapsed),
                "certifications": current_certs
            }
    
    return {
        "in_progress": None,
        "remaining": 0,
        "certifications": current_certs
    }

@api_router.get("/certifications/can-fly")
async def check_can_fly():
    """Check if player has minimum certifications to fly"""
    game = await db.game_state.find_one()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    certs = game.get("certifications", {})
    
    # Minimum requirements to fly (need commercial pilot to fly for money)
    can_fly_private = certs.get("private_pilot", False) and certs.get("medical_certificate", False)
    can_fly_commercial = can_fly_private and certs.get("commercial_pilot", False)
    can_fly_part135 = can_fly_commercial and certs.get("part_135", False)
    can_fly_part121 = can_fly_part135 and certs.get("part_121", False)
    
    return {
        "can_fly_private": can_fly_private,
        "can_fly_commercial": can_fly_commercial,
        "can_operate_charter": can_fly_part135,
        "can_operate_airline": can_fly_part121,
        "certifications": certs
    }

@api_router.post("/game/home-airport")
async def set_home_airport(data: SetHomeAirport):
    """Set home airport"""
    airport = get_airport_by_iata(data.iata.upper())
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    await db.game_state.update_one({}, {"$set": {"home_airport": data.iata.upper()}})
    return {"message": f"Home airport set to {airport['name']}"}

@api_router.post("/game/tutorial-seen")
async def mark_tutorial_seen():
    """Mark tutorial as seen"""
    await db.game_state.update_one({}, {"$set": {"tutorial_seen": True}})
    return {"message": "Tutorial marked as seen"}

@api_router.post("/game/theme")
async def set_theme(theme: str):
    """Set game theme"""
    if theme not in ["dark", "light"]:
        raise HTTPException(status_code=400, detail="Invalid theme")
    await db.game_state.update_one({}, {"$set": {"theme": theme}})
    return {"message": f"Theme set to {theme}"}

@api_router.post("/game/advance-day")
async def advance_day():
    """Advance game time by one day"""
    game = await db.game_state.find_one()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    new_date = datetime.fromisoformat(str(game["current_date"])) + timedelta(days=1)
    current_month = new_date.month
    
    # Process monthly loan payments on the 1st of each month
    if new_date.day == 1:
        loans = await db.loans.find({"remaining": {"$gt": 0}}).to_list(100)
        for loan in loans:
            # Check if already paid this month
            last_payment_month = loan.get("last_payment_month")
            if last_payment_month != current_month:
                payment = loan["monthly_payment"]
                # Deduct from balance
                await db.game_state.update_one({}, {
                    "$inc": {"balance": -payment, "total_expenses": payment}
                })
                # Update loan
                new_remaining = max(0, loan["remaining"] - payment + (loan["remaining"] * (loan["interest_rate"] / 12)))
                await db.loans.update_one(
                    {"id": loan["id"]},
                    {"$set": {"remaining": new_remaining, "last_payment_month": current_month}, "$inc": {"months_paid": 1}}
                )
    
    await db.game_state.update_one({}, {"$set": {"current_date": new_date}})
    game = await db.game_state.find_one()
    return serialize_doc(game)

@api_router.post("/game/advance-time")
async def advance_time(hours: float = 1):
    """Advance game time by specified hours and update flights"""
    game = await db.game_state.find_one()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    new_date = datetime.fromisoformat(str(game["current_date"])) + timedelta(hours=hours)
    
    # Update in-progress flights
    routes = await db.routes.find({"status": "in_progress"}).to_list(100)
    for route in routes:
        # Calculate new progress
        elapsed_hours = hours
        flight_duration = route["flight_duration"]
        progress_increment = elapsed_hours / flight_duration
        new_progress = min(1.0, route["progress"] + progress_increment)
        
        # Check for severe weather at destination when flight is near completion (>80%)
        dest_weather = generate_weather(route["destination"])
        is_severe_storm = dest_weather["condition"] == "storm" and dest_weather["wind_speed"] > 60
        
        delay_compensation = 0
        flight_delayed = route.get("delayed", False)
        diverted_to = route.get("diverted_to")
        
        if new_progress >= 0.80 and is_severe_storm and not flight_delayed and not diverted_to:
            # Severe storm - either divert or delay
            if dest_weather["wind_speed"] > 80:
                # Very severe - must divert to alternate airport
                # Find nearest alternate airport
                dest_airport = get_airport_by_iata(route["destination"])
                alternate = find_alternate_airport(route["destination"], dest_airport["lat"], dest_airport["lon"])
                
                if alternate:
                    # Divert to alternate
                    diversion_compensation = route.get("passengers", 0) * 50  # $50 per passenger
                    await db.routes.update_one(
                        {"id": route["id"]},
                        {"$set": {
                            "diverted_to": alternate["iata"],
                            "diversion_compensation": diversion_compensation,
                            "diversion_reason": f"Severe storm at {route['destination']} (winds {dest_weather['wind_speed']}km/h)"
                        }}
                    )
                    # Deduct compensation from revenue
                    delay_compensation = diversion_compensation
            else:
                # Storm but not severe enough to divert - delay the flight
                delay_hours = dest_weather["wind_speed"] / 30  # 1-2 hour delay
                compensation = route.get("passengers", 0) * 25  # $25 per passenger for delay
                
                new_duration = route["flight_duration"] + delay_hours
                await db.routes.update_one(
                    {"id": route["id"]},
                    {"$set": {
                        "flight_duration": new_duration,
                        "delayed": True,
                        "delay_hours": delay_hours,
                        "delay_compensation": compensation,
                        "delay_reason": f"Storm at {route['destination']} (winds {dest_weather['wind_speed']}km/h)"
                    }}
                )
                delay_compensation = compensation
        
        # Round 95-99% to 100%
        if new_progress >= 0.95 and new_progress < 1.0:
            new_progress = 1.0
        
        if new_progress >= 1.0:
            # Flight completed - check for diversions and compensations
            final_destination = route.get("diverted_to") or route["destination"]
            total_compensation = route.get("delay_compensation", 0) + route.get("diversion_compensation", 0) + delay_compensation
            
            await db.routes.update_one(
                {"id": route["id"]},
                {"$set": {
                    "status": "completed",
                    "progress": 1.0,
                    "arrival_time": new_date,
                    "final_destination": final_destination,
                    "total_compensation": total_compensation
                }}
            )
            
            # Add revenue to balance, minus any compensation paid
            actual_revenue = route["revenue"] - total_compensation
            profit = actual_revenue - route["costs"]
            await db.game_state.update_one({}, {
                "$inc": {
                    "balance": profit,
                    "total_revenue": actual_revenue,
                    "total_expenses": route["costs"] + total_compensation,
                    "flights_completed": 1
                }
            })
            
            flight_mode = route.get("flight_mode", "charter")
            
            if flight_mode == "scheduled" and not route.get("is_return_leg"):
                # Scheduled flight completed outbound - create return flight
                # First, keep aircraft flying (don't set to idle)
                # Create return route
                origin_airport = get_airport_by_iata(route["destination"])
                dest_airport = get_airport_by_iata(route["origin"])
                owned = await db.owned_aircraft.find_one({"id": route["aircraft_id"]})
                aircraft = get_aircraft_by_id(owned["aircraft_id"]) if owned else None
                
                if aircraft and origin_airport and dest_airport:
                    distance = route["distance"]  # Same distance
                    flight_duration = distance / aircraft["cruise_speed"]
                    fuel_required = flight_duration * aircraft["fuel_burn"]
                    fuel_cost = fuel_required * 1.5
                    operating_cost = flight_duration * 500
                    total_cost = fuel_cost + operating_cost
                    
                    # Calculate new revenue for return leg
                    if route["flight_type"] == "passenger":
                        passengers = int(aircraft["capacity"] * random.uniform(0.65, 0.95))
                        revenue = passengers * route["ticket_price"]
                        cargo_weight = 0
                    else:
                        cargo_weight = int(aircraft["cargo_capacity"] * random.uniform(0.55, 0.9))
                        revenue = cargo_weight * route["cargo_rate"]
                        passengers = 0
                    
                    return_route = {
                        "id": str(uuid.uuid4()),
                        "aircraft_id": route["aircraft_id"],
                        "origin": route["destination"],
                        "destination": route["origin"],
                        "distance": distance,
                        "flight_type": route["flight_type"],
                        "flight_mode": "scheduled",
                        "ticket_price": route["ticket_price"],
                        "cargo_rate": route["cargo_rate"],
                        "fuel_required": round(fuel_required, 2),
                        "flight_duration": round(flight_duration, 2),
                        "status": "in_progress",
                        "departure_time": new_date,
                        "progress": 0,
                        "revenue": round(revenue, 2),
                        "costs": round(total_cost, 2),
                        "passengers": passengers,
                        "cargo_weight": cargo_weight,
                        "is_return_leg": True,
                        "parent_route_id": route["id"],
                        "created_at": new_date
                    }
                    await db.routes.insert_one(return_route)
                    # Keep aircraft flying - update location only
                    await db.owned_aircraft.update_one(
                        {"id": route["aircraft_id"]},
                        {"$set": {"current_airport": route["destination"]}}
                    )
                else:
                    # Fallback - set aircraft to idle at destination
                    await db.owned_aircraft.update_one(
                        {"id": route["aircraft_id"]},
                        {"$set": {"status": "idle", "current_airport": route["destination"]}}
                    )
                    
            elif flight_mode == "scheduled" and route.get("is_return_leg"):
                # Scheduled return leg completed - schedule next outbound tomorrow
                # Set aircraft to idle for now, scheduled route will restart next day
                await db.owned_aircraft.update_one(
                    {"id": route["aircraft_id"]},
                    {"$set": {"status": "idle", "current_airport": route["destination"]}}
                )
                
                # Create next day's outbound flight (using parent route info)
                parent_route = await db.routes.find_one({"id": route.get("parent_route_id")})
                if parent_route:
                    owned = await db.owned_aircraft.find_one({"id": route["aircraft_id"]})
                    aircraft = get_aircraft_by_id(owned["aircraft_id"]) if owned else None
                    
                    if aircraft:
                        distance = route["distance"]
                        flight_duration = distance / aircraft["cruise_speed"]
                        fuel_required = flight_duration * aircraft["fuel_burn"]
                        fuel_cost = fuel_required * 1.5
                        operating_cost = flight_duration * 500
                        total_cost = fuel_cost + operating_cost
                        
                        # Price-based frequency: cheaper tickets = more frequent flights
                        # Base turnaround is 8 hours, adjust based on ticket price
                        ticket_price = route.get("ticket_price", 500)
                        optimal_price = calculate_optimal_ticket_price(distance, aircraft, route["flight_type"])
                        
                        # If price is lower than optimal, shorter turnaround (more demand)
                        # If price is higher, longer turnaround (less demand)
                        price_ratio = ticket_price / max(optimal_price, 1)
                        
                        if price_ratio < 0.8:
                            # Very cheap - high demand, quick turnaround (2-4 hours)
                            turnaround_hours = random.uniform(2, 4)
                            load_factor = random.uniform(0.85, 0.98)  # Higher load factor
                        elif price_ratio < 1.0:
                            # Cheap - good demand (4-6 hours)
                            turnaround_hours = random.uniform(4, 6)
                            load_factor = random.uniform(0.75, 0.95)
                        elif price_ratio < 1.2:
                            # Optimal price (6-10 hours)
                            turnaround_hours = random.uniform(6, 10)
                            load_factor = random.uniform(0.65, 0.90)
                        elif price_ratio < 1.5:
                            # Expensive - lower demand (10-16 hours)
                            turnaround_hours = random.uniform(10, 16)
                            load_factor = random.uniform(0.50, 0.80)
                        else:
                            # Very expensive - low demand (16-24 hours)
                            turnaround_hours = random.uniform(16, 24)
                            load_factor = random.uniform(0.35, 0.65)
                        
                        if route["flight_type"] == "passenger":
                            passengers = int(aircraft["capacity"] * load_factor)
                            revenue = passengers * route["ticket_price"]
                            cargo_weight = 0
                        else:
                            cargo_weight = int(aircraft["cargo_capacity"] * load_factor)
                            revenue = cargo_weight * route["cargo_rate"]
                            passengers = 0
                        
                        # Schedule based on price-adjusted turnaround
                        next_departure = new_date + timedelta(hours=turnaround_hours)
                        
                        next_outbound = {
                            "id": str(uuid.uuid4()),
                            "aircraft_id": route["aircraft_id"],
                            "origin": route["destination"],  # Return leg destination = original origin
                            "destination": parent_route["destination"],
                            "distance": distance,
                            "flight_type": route["flight_type"],
                            "flight_mode": "scheduled",
                            "ticket_price": route["ticket_price"],
                            "cargo_rate": route["cargo_rate"],
                            "fuel_required": round(fuel_required, 2),
                            "flight_duration": round(flight_duration, 2),
                            "status": "in_progress",
                            "departure_time": next_departure,
                            "progress": 0,
                            "revenue": round(revenue, 2),
                            "costs": round(total_cost, 2),
                            "passengers": passengers,
                            "cargo_weight": cargo_weight,
                            "is_return_leg": False,
                            "parent_route_id": None,
                            "turnaround_hours": round(turnaround_hours, 1),
                            "created_at": new_date
                        }
                        await db.routes.insert_one(next_outbound)
                        await db.owned_aircraft.update_one(
                            {"id": route["aircraft_id"]},
                            {"$set": {"status": "flying"}}
                        )
            else:
                # Charter flight - aircraft stays at destination until new route
                await db.owned_aircraft.update_one(
                    {"id": route["aircraft_id"]},
                    {"$set": {"status": "idle", "current_airport": route["destination"]}}
                )
        else:
            # Update progress
            await db.routes.update_one(
                {"id": route["id"]},
                {"$set": {"progress": new_progress}}
            )
    
    await db.game_state.update_one({}, {"$set": {"current_date": new_date}})
    game = await db.game_state.find_one()
    return serialize_doc(game)

# Loan routes
@api_router.post("/loans")
async def create_loan(loan_data: LoanCreate):
    """Create a new loan"""
    monthly_payment = calculate_monthly_payment(loan_data.amount, 0.07, loan_data.term_months)
    loan = Loan(
        amount=loan_data.amount,
        remaining=loan_data.amount,
        monthly_payment=monthly_payment,
        term_months=loan_data.term_months
    )
    
    await db.loans.insert_one(loan.dict())
    # Add loan amount to balance
    await db.game_state.update_one({}, {"$inc": {"balance": loan_data.amount}})
    
    return loan.dict()

@api_router.get("/loans")
async def get_loans():
    """Get all loans"""
    loans = await db.loans.find().to_list(100)
    return serialize_doc(loans)

@api_router.post("/loans/{loan_id}/pay")
async def pay_loan(loan_id: str, payment: LoanPayment):
    """Make extra payment on loan"""
    loan = await db.loans.find_one({"id": loan_id})
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    game = await db.game_state.find_one()
    if game["balance"] < payment.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    new_remaining = max(0, loan["remaining"] - payment.amount)
    
    # Get current month to track payment
    current_date = datetime.fromisoformat(str(game["current_date"]))
    current_month = current_date.month
    
    await db.loans.update_one(
        {"id": loan_id}, 
        {"$set": {"remaining": new_remaining, "last_payment_month": current_month}}
    )
    await db.game_state.update_one({}, {"$inc": {"balance": -payment.amount, "total_expenses": payment.amount}})
    
    return {"message": f"Payment of ${payment.amount} applied to loan", "remaining": new_remaining}

# Owned aircraft routes
@api_router.post("/aircraft/purchase")
async def purchase_aircraft(purchase: AircraftPurchase):
    """Purchase an aircraft"""
    aircraft = get_aircraft_by_id(purchase.aircraft_id)
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    
    game = await db.game_state.find_one()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if not game.get("home_airport"):
        raise HTTPException(status_code=400, detail="Please set home airport first")
    
    price = aircraft["price"]
    
    if purchase.use_loan and purchase.loan_amount and purchase.loan_term:
        # Create loan for the purchase
        if purchase.loan_amount > price:
            raise HTTPException(status_code=400, detail="Loan amount cannot exceed aircraft price")
        
        down_payment = price - purchase.loan_amount
        if game["balance"] < down_payment:
            raise HTTPException(status_code=400, detail="Insufficient funds for down payment")
        
        # Create loan
        monthly_payment = calculate_monthly_payment(purchase.loan_amount, 0.07, purchase.loan_term)
        loan = Loan(
            amount=purchase.loan_amount,
            remaining=purchase.loan_amount,
            monthly_payment=monthly_payment,
            term_months=purchase.loan_term
        )
        await db.loans.insert_one(loan.dict())
        
        # Deduct down payment
        await db.game_state.update_one({}, {"$inc": {"balance": -down_payment, "total_expenses": down_payment}})
    else:
        # Full purchase
        if game["balance"] < price:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        await db.game_state.update_one({}, {"$inc": {"balance": -price, "total_expenses": price}})
    
    # Create owned aircraft
    owned = OwnedAircraft(
        aircraft_id=purchase.aircraft_id,
        name=purchase.name,
        current_airport=game["home_airport"]
    )
    await db.owned_aircraft.insert_one(owned.dict())
    
    return owned.dict()

@api_router.delete("/aircraft/owned/{aircraft_id}")
async def sell_aircraft(aircraft_id: str):
    """Sell an owned aircraft"""
    owned = await db.owned_aircraft.find_one({"id": aircraft_id})
    if not owned:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    
    if owned["status"] == "flying":
        raise HTTPException(status_code=400, detail="Cannot sell aircraft while in flight")
    
    aircraft = get_aircraft_by_id(owned["aircraft_id"])
    sell_price = int(aircraft["price"] * 0.7)  # Sell for 70% of original price
    
    await db.owned_aircraft.delete_one({"id": aircraft_id})
    await db.game_state.update_one({}, {"$inc": {"balance": sell_price, "total_revenue": sell_price}})
    
    return {"message": f"Aircraft sold for ${sell_price:,}", "amount": sell_price}

# Route routes
@api_router.post("/routes/calculate-profit")
async def calculate_profit(data: CalculateProfitRequest):
    """Calculate expected profit for a potential flight"""
    owned = await db.owned_aircraft.find_one({"id": data.aircraft_id})
    if not owned:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    
    aircraft = get_aircraft_by_id(owned["aircraft_id"])
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft details not found")
    
    origin = get_airport_by_iata(data.origin.upper())
    destination = get_airport_by_iata(data.destination.upper())
    if not origin or not destination:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    distance = calculate_distance(origin["lat"], origin["lon"], destination["lat"], destination["lon"])
    
    return calculate_flight_profit(aircraft, distance, data.flight_type, data.ticket_price, data.cargo_rate)

@api_router.post("/routes")
async def create_route(route_data: RouteCreate):
    """Create a new route and start the flight"""
    # Get game state for certification check
    game = await db.game_state.find_one()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check certifications for hard mode
    if game.get("difficulty") == "hard":
        certs = game.get("certifications", {})
        
        # Always need commercial pilot and medical to fly for money
        if not certs.get("commercial_pilot"):
            raise HTTPException(status_code=403, detail="You need a Commercial Pilot License (CPL) to fly for money")
        if not certs.get("medical_certificate"):
            raise HTTPException(status_code=403, detail="You need a valid Medical Certificate to fly")
        
        # Check flight mode specific certifications
        if route_data.flight_mode == "charter" and not certs.get("part_135"):
            raise HTTPException(status_code=403, detail="You need a Part 135 Air Carrier Certificate for charter flights")
        if route_data.flight_mode == "scheduled" and not certs.get("part_121"):
            raise HTTPException(status_code=403, detail="You need a Part 121 Air Carrier Certificate for scheduled flights")
    
    # Validate owned aircraft
    owned = await db.owned_aircraft.find_one({"id": route_data.aircraft_id})
    if not owned:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    
    if owned["status"] == "flying":
        raise HTTPException(status_code=400, detail="Aircraft is already in flight")
    
    # Validate airports
    origin = get_airport_by_iata(route_data.origin.upper())
    destination = get_airport_by_iata(route_data.destination.upper())
    if not origin or not destination:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    # Check aircraft is at origin
    if owned["current_airport"] != route_data.origin.upper():
        raise HTTPException(status_code=400, detail=f"Aircraft is at {owned['current_airport']}, not {route_data.origin.upper()}")
    
    # Get aircraft details
    aircraft = get_aircraft_by_id(owned["aircraft_id"])
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft details not found")
    
    # Calculate distance and fuel
    distance = calculate_distance(origin["lat"], origin["lon"], destination["lat"], destination["lon"])
    flight_duration = distance / aircraft["cruise_speed"]
    fuel_required = flight_duration * aircraft["fuel_burn"]
    
    # Check range
    if distance > aircraft["range"]:
        raise HTTPException(status_code=400, detail=f"Distance ({int(distance)} km) exceeds aircraft range ({aircraft['range']} km)")
    
    # Calculate revenue and costs
    fuel_price = 1.5  # $ per liter
    fuel_cost = fuel_required * fuel_price
    
    # Weather impact
    origin_weather = generate_weather(route_data.origin.upper())
    dest_weather = generate_weather(route_data.destination.upper())
    weather_delay = origin_weather["delay_hours"] + dest_weather["delay_hours"]
    weather_extra_cost = (origin_weather["extra_cost_percent"] + dest_weather["extra_cost_percent"]) / 2
    
    # Congestion impact
    congestion_factor = (origin["congestion"] + destination["congestion"]) / 2
    congestion_delay = congestion_factor * 0.3  # Up to 30% delay
    
    total_flight_duration = flight_duration * (1 + congestion_delay) + weather_delay
    
    # Use optimal pricing if not specified
    if route_data.flight_type == "passenger":
        ticket_price = route_data.ticket_price or calculate_optimal_ticket_price(distance, aircraft, "passenger")
        passengers = int(aircraft["capacity"] * random.uniform(0.65, 0.95))  # 65-95% load factor
        revenue = passengers * ticket_price
        cargo_weight = 0
    else:
        cargo_rate = route_data.cargo_rate or calculate_optimal_ticket_price(distance, aircraft, "cargo")
        passengers = 0
        cargo_weight = int(aircraft["cargo_capacity"] * random.uniform(0.55, 0.9))  # 55-90% load factor
        revenue = cargo_weight * cargo_rate
    
    # Operating costs
    operating_cost = total_flight_duration * 500  # Base operating cost per hour
    total_cost = (fuel_cost + operating_cost) * (1 + weather_extra_cost / 100)
    
    # Create route
    route = Route(
        aircraft_id=route_data.aircraft_id,
        origin=route_data.origin.upper(),
        destination=route_data.destination.upper(),
        distance=round(distance, 2),
        flight_type=route_data.flight_type,
        flight_mode=route_data.flight_mode,
        ticket_price=ticket_price if route_data.flight_type == "passenger" else 0,
        cargo_rate=cargo_rate if route_data.flight_type == "cargo" else 0,
        fuel_required=round(fuel_required, 2),
        flight_duration=round(total_flight_duration, 2),
        status="in_progress",
        departure_time=datetime.fromisoformat(str(game["current_date"])),
        revenue=round(revenue, 2),
        costs=round(total_cost, 2),
        passengers=passengers,
        cargo_weight=cargo_weight
    )
    
    await db.routes.insert_one(route.dict())
    
    # Update aircraft status
    await db.owned_aircraft.update_one(
        {"id": route_data.aircraft_id},
        {"$set": {"status": "flying"}}
    )
    
    return {
        **route.dict(),
        "weather": {
            "origin": origin_weather,
            "destination": dest_weather
        }
    }

@api_router.get("/routes")
async def get_routes():
    """Get all routes, with in-progress first"""
    routes = await db.routes.find().to_list(1000)
    # Sort: in_progress first, then by created_at desc
    serialized = serialize_doc(routes)
    serialized.sort(key=lambda x: (0 if x.get("status") == "in_progress" else 1, x.get("created_at", "")), reverse=False)
    return serialized

@api_router.get("/routes/active")
async def get_active_routes():
    """Get all in-progress routes with current position"""
    routes = await db.routes.find({"status": "in_progress"}).to_list(100)
    result = []
    for route in routes:
        origin = get_airport_by_iata(route["origin"])
        destination = get_airport_by_iata(route["destination"])
        if origin and destination:
            # Calculate current position based on progress
            progress = route["progress"]
            current_lat = origin["lat"] + (destination["lat"] - origin["lat"]) * progress
            current_lon = origin["lon"] + (destination["lon"] - origin["lon"]) * progress
            
            # Calculate heading angle
            heading = math.degrees(math.atan2(
                destination["lon"] - origin["lon"],
                destination["lat"] - origin["lat"]
            ))
            
            owned = await db.owned_aircraft.find_one({"id": route["aircraft_id"]})
            aircraft = get_aircraft_by_id(owned["aircraft_id"]) if owned else None
            
            item = serialize_doc(route)
            item["current_position"] = {"lat": current_lat, "lon": current_lon}
            item["origin_coords"] = {"lat": origin["lat"], "lon": origin["lon"]}
            item["destination_coords"] = {"lat": destination["lat"], "lon": destination["lon"]}
            item["heading"] = heading
            item["aircraft_name"] = owned["name"] if owned else "Unknown"
            item["aircraft_details"] = aircraft
            result.append(item)
    return result

@api_router.delete("/routes/{route_id}")
async def cancel_route(route_id: str):
    """Cancel a route (including in-progress flights)"""
    route = await db.routes.find_one({"id": route_id})
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Get the aircraft to update its status
    aircraft = await db.owned_aircraft.find_one({"id": route["aircraft_id"]})
    
    if route["status"] == "in_progress":
        # For in-progress flights, divert the plane to the nearest airport (origin or destination)
        # Based on progress, decide where to land
        progress = route.get("progress", 0)
        
        if progress < 0.5:
            # Less than halfway - return to origin
            landing_airport = route["origin"]
        else:
            # More than halfway - continue to destination
            landing_airport = route["destination"]
        
        # Update aircraft status to idle at the landing airport
        if aircraft:
            await db.owned_aircraft.update_one(
                {"id": route["aircraft_id"]},
                {"$set": {"status": "idle", "current_airport": landing_airport}}
            )
        
        # Delete any related return legs or future scheduled flights
        if route.get("flight_mode") == "scheduled":
            # Delete return leg if this is an outbound
            await db.routes.delete_many({"parent_route_id": route_id})
            # Delete if this is a return leg
            if route.get("is_return_leg") and route.get("parent_route_id"):
                pass  # Just delete this one
    else:
        # For pending flights, just update aircraft to idle
        if aircraft:
            await db.owned_aircraft.update_one(
                {"id": route["aircraft_id"]},
                {"$set": {"status": "idle"}}
            )
    
    # Delete the route
    await db.routes.delete_one({"id": route_id})
    
    return {"message": "Flight cancelled", "aircraft_landed_at": route["origin"] if route.get("progress", 0) < 0.5 else route["destination"]}

@api_router.get("/distance")
async def get_distance(origin: str, destination: str):
    """Calculate distance between two airports"""
    origin_airport = get_airport_by_iata(origin.upper())
    dest_airport = get_airport_by_iata(destination.upper())
    
    if not origin_airport or not dest_airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    
    distance = calculate_distance(
        origin_airport["lat"], origin_airport["lon"],
        dest_airport["lat"], dest_airport["lon"]
    )
    
    return {
        "origin": origin.upper(),
        "destination": destination.upper(),
        "distance_km": round(distance, 2),
        "distance_nm": round(distance * 0.539957, 2)  # Convert to nautical miles
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
