import aws_lambda_helper as lh

def lambda_city_updater(host, user, password, api_aerodatabox):
    schema="Gans"
    
    con =  lh.open_connection(host=host, usr=user, pwd=password, db=schema)
    city_names = lh.get_tabel_column("cities", "name", con)
    cities_data = lh.get_city_information(city_names)
    lh.insert_or_update(cities_data, "cities", ["name"], con)

    city_ids = lh.get_tabel_column("cities", "city_id", con)
    lats = lh.get_tabel_column("cities", "lat", con)
    lons = lh.get_tabel_column("cities", "lon", con)

    airports_data = lh.airports(city_ids, lats, lons, api_aerodatabox)
    lh.insert_or_update(airports_data, "airports", ["iata"], con)

    con.close()

def lambda_daily_updater(host, user, password, api_aerodatabox, api_openweather):
    schema="Gans"

    con =  lh.open_connection(host=host, usr=user, pwd=password, db=schema)
    
    city_ids = lh.get_tabel_column("cities", "city_id", con)
    lats = lh.get_tabel_column("cities", "lat", con)
    lons = lh.get_tabel_column("cities", "lon", con)

    weather_data = lh.weather_forecast(city_ids, lats, lons, api_openweather)
    lh.insert_or_update(weather_data, "weather", ["weather_id"], con)

    airports = lh.get_tabel_column("airports", "iata", con)
    flights_data = lh.arrival_flights(airports, api_aerodatabox)
    lh.insert_or_update(flights_data, "flights", ["flight_id"], con)

    con.close()

def lambda_population_updater(host, user, password):
    schema="Gans"
    
    con =  lh.open_connection(host=host, usr=user, pwd=password, db=schema)
    
    city_names = lh.get_tabel_column("cities", "name", con)
    city_ids = lh.get_tabel_column("cities", "city_id", con)

    population_data =  lh.get_city_population(city_ids, city_names)
    lh.insert_or_update(population_data, "population", ["last_update", "city_id"], con)

    con.close()
