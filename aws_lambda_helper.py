import mysql.connector
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta
import pytz

### data requests
def get_city_information(cities):
    rows = []
    data_keys = ["name","country","lat","lon","log"]
    for i in range(0, len(cities)):
        data_dict = dict.fromkeys(data_keys, None)
        data_dict["name"] = cities[i]

        url = "https://en.wikipedia.org/wiki/" + cities[i]
        page = requests.get(url)
        if(page.status_code != 200):
            data_keys["log"] = f"web-page for {cities[i]} not accessed with status-code {page.status_code}"
        else:
            try:
                soup = BeautifulSoup(page.content, "html.parser")
                info_box = soup.select(".infobox")
                info = info_box[0].find_all("tr")

                for i in range(0,len(info)):
                    
                    # Country (look for label)
                    lab = info[i].select(".infobox-label")
                    try:
                        tmp = lab[0].get_text()
                        if tmp == "Country": data_dict["country"] = info[i].select(".infobox-data")[0].find("a").get_text()
                    except: pass
                    
                    # lat, lon (look for class)
                    try:
                        lat = info[i].select(".latitude")[0].get_text()
                        data_dict["lat"] = degree_to_decimal_coords(lat)
                    except: pass
                    try:
                        lon = info[i].select(".longitude")[0].get_text()
                        data_dict["lon"] = degree_to_decimal_coords(lon)
                    except: pass
            except:
                data_keys["log"] = f"Failed to extract data for {cities[i]}"
        rows.append(data_dict)       
    return rows


def airports(cities, lat, lon, api_key):
	rows = []
	keys_li = ["city_id", "iata"]


	url = "https://aerodatabox.p.rapidapi.com/airports/search/location"
	headers = { "X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"}

	for i in range(0, len(cities)):
		data_dict = dict.fromkeys(keys_li, None)
		data_dict["city_id"] = cities[i]
		if lat[i] is not None and lon[i] is not None:
			querystring = {"lat": lat[i],"lon": lon[i],"radiusKm":"50","limit":"10","withFlightInfoOnly":"true"}
			response = requests.get(url, headers=headers, params=querystring)
			if response.status_code == 200:
				try:
					airports = response.json()
					for item in airports["items"]:
						data_dict["iata"] = item["iata"]
						rows.append(data_dict)
				except: pass
			else: pass
		else: pass
	return rows

def arrival_flights(airports, api_key):
	rows = []
	keys_li = ["iata","flight_no", "sceduled_arrival_time", "revised_arrival_time",
				"terminal", "status", "depatured_from", "depatured_from_name", "airline", "log"]

	start_time_1 = str(date_tomorrow()) + "T00:00"
	end_time_1 = str(date_tomorrow()) + "T11:59"
	start_time_2 = str(date_tomorrow()) + "T12:00"
	end_time_2 = str(date_tomorrow()) + "T23:59"

	querystring = {"withLeg":"true","direction":"Arrival","withCancelled":"false","withCodeshared":"true","withCargo":"false","withPrivate":"false","withLocation":"false"}

	headers = {
		"X-RapidAPI-Key": api_key,
		"X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
	}

	for iata in airports:
		url_1 = f"https://aerodatabox.p.rapidapi.com/flights/airports/iata/{iata}/{start_time_1}/{end_time_1}"
		url_2 = f"https://aerodatabox.p.rapidapi.com/flights/airports/iata/{iata}/{start_time_2}/{end_time_2}"

		response_1 = requests.get(url_1, headers=headers, params=querystring)
		response_2 = requests.get(url_2, headers=headers, params=querystring)

		if response_1.status_code == 200 & response_2.status_code == 200:
			flights = response_1.json().get("arrivals") + response_2.json().get("arrivals")

			for flight in flights:
				data_dict = dict.fromkeys(keys_li, None)
				data_dict["iata"] = iata
				data_dict["flight_no"] = flight.get("number")
				try: 
					dt_val = flight.get("arrival").get("scheduledTime").get("local")
					data_dict["sceduled_arrival_time"] = remove_timezone_offset(dt_val)
				except: pass
				try:					
					dt_val = flight.get("arrival").get("revisedTime").get("local")
					data_dict["revised_arrival_time"] = remove_timezone_offset(dt_val)
				except: pass
				try: data_dict["terminal"] = int(flight.get("arrival").get("terminal"))
				except: pass
				data_dict["status"] = flight.get("status")
				try: data_dict["depatured_from"] = flight.get("departure").get("airport").get("iata")
				except: pass
				try: data_dict["depatured_from_name"] = flight.get("departure").get("airport").get("name")
				except: pass
				try: data_dict["airline"] = flight.get("airline").get("name")
				except: pass
				rows.append(data_dict)
		else:
			data_dict = dict.fromkeys(keys_li, None)
			data_dict["iata"] = iata 
			data_dict["log"] = f"Warning: No data found for airport {iata}, with status {response_1.status_code} & {response_2.status_code}"
			rows.append(data_dict)

	return rows

def weather_forecast(cities, lat, lon, api_key):

    data_keys = ["timestamp", "city_id", "time", "temp", "felt_temp", 
                 "humidity", "wind_speed", "weather_class", "weather_description"]
    rows = []
    timerange = start_end_day(date_tomorrow())
    for i in range(0,len(cities)):
        
        if lat[i] is not None and lon[i] is not None:
            api_req = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat[i]}&lon={lon[i]}&appid={api_key}&units=metric"
            weather = requests.get(api_req)          
            if weather.status_code == 200:
                data = weather.json()  

                for element in data.get("list"):
                    timestamp = element.get("dt")
                    if timerange[0] <= timestamp <= timerange[1]:
                        data_dict = dict.fromkeys(data_keys, None)    
                        data_dict["timestamp"] = timestamp
                        data_dict["city_id"] = cities[i]
                        data_dict["time"] = datetime.fromtimestamp(element.get("dt"))
                        data_dict["temp"] = element.get("main").get("temp")
                        data_dict["felt_temp"] = element.get("main").get("feels_like")
                        data_dict["humidity"] = element.get("main").get("humidity")
                        data_dict["wind_speed"] = element.get("wind").get("speed")
                        data_dict["weather_class"] = element.get("weather")[0].get("main")
                        data_dict["weather_description"] = element.get("weather")[0].get("description")                  
                        rows.append(data_dict)
                    else: pass
            else: pass
        else: pass
    return rows

def get_city_population(city_ids, cities):
    rows = []
    data_keys = ["city_id","last_update","population","log"]
    for i in range(0, len(cities)):
        url = "https://en.wikipedia.org/wiki/" + cities[i]
        page = requests.get(url)
        data_dict = dict.fromkeys(data_keys, None)
        data_dict["last_update"] = datetime.now().date().year
        data_dict["city_id"] = city_ids[i]

        if(page.status_code != 200):
            data_keys["log"] = f"web-page for {cities[i]} not accessed with status-code {page.status_code}"
        else:
            try:
                soup = BeautifulSoup(page.content, "html.parser")
                info_box = soup.select(".infobox")
                info = info_box[0].find_all("tr")
                for i in range(0,len(info)):
                    # Population (look for header)
                    header = info[i].select(".infobox-header")
                    try:
                        tmp = header[0].get_text()
                        if "Population" in tmp:
                            population = info[i+1].select(".infobox-data")[0].get_text()
                            data_dict["population"] = int(population.replace(',', ''))
                    except: pass
            except:
                data_keys["log"] = f"Failed to extract data for {cities[i]}"
        rows.append(data_dict)
    return rows

###datetime conversions
def date_tomorrow():
    date_today = datetime.now(pytz.timezone("CET"))
    return date_today.date() + timedelta(days=1)

def start_end_day(date):
    start = datetime(date.year, date.month, date.day, 0,0,0).astimezone(pytz.timezone("CET"))
    end = datetime(date.year, date.month, date.day, 23,59,59).astimezone(pytz.timezone("CET"))
    return [start.timestamp(), end.timestamp()]

def remove_timezone_offset(dt_value):
    dt = datetime.fromisoformat(dt_value)
    return(dt.strftime('%Y-%m-%d %H:%M:%S'))

### my_sql connection
def open_connection(host, usr, pwd, db):
    conn =  mysql.connector.connect(
            host=host,
            user=usr,
            password=pwd,
            database=db
        )
    return conn

def insert_or_update(rows, table_name, exclude_key, conn):
    cursor = conn.cursor()
    columns = rows[0].keys()
    columns_join = ', '.join(columns)
    values_join = ', '.join(['%s'] * len(columns))
    update_values = ', '.join(f"{col} = %s" for col in columns if col not in exclude_key)
    
    query = f"""
    INSERT INTO {table_name} ({columns_join})
    VALUES ({values_join})
    ON DUPLICATE KEY UPDATE {update_values}
    """

    for row in rows:
        insert_values = [row[col] for col in columns]
        update_values = [row[col] for col in columns if col not in exclude_key]
        params = tuple(insert_values + update_values)
        cursor.execute(query, params)
        
    conn.commit()
    cursor.close()

def get_tabel_column(table_name, col_name, conn):
    cursor = conn.cursor()

    query = f"SELECT {col_name} FROM {table_name}"
    cursor.execute(query)
    out = [i[0] for i in cursor.fetchall()]
    cursor.close()
    return out

### utils
def degree_to_decimal_coords(coords):
    degrees_lat = float(re.search('^[0-9]{1,3}',coords).group())
    minutes_lat = float(re.search('°([0-9]{1,2})′',coords).group(1))/60
    seconds_lat = re.search('′([0-9]{1,2}\.{0,1}[0-9]*)″',coords)
    if seconds_lat is not None:
        seconds_lat = float(seconds_lat.group(1))/3600
    else: seconds_lat = 0
    return degrees_lat+minutes_lat+seconds_lat
