# aws-data-pipeline

Exercise project to create an automated data pipeline on the cloud using Python and MySQL on AWS (RDS, Lambda, and CloudWatch). The project is designed to gather information on the geographic location and population size of pre-specified cities in Germany by web scraping [wikipedia.org](https://www.wikipedia.org/). Furthermore, weather information and information on arriving flights for the next day (CET) can be retrieved. All data is stored in a relational database containing the tables `cities`, `airports`, `population`, `weather`, and `flights`.

## Prerequisites
To run this project, you need an API key for the [Weather API - 5-day forecast](https://openweathermap.org/forecast5) as well as [AeroDataBox](https://rapidapi.com/aedbx-aedbx/api/aerodatabox/). Free options with monthly limited requests are available.

You also need an AWS account to run the project in the cloud.

__WARNING:__ Free tier options are available for AWS, but costs may occur when choosing the wrong payment plan or exceeding limits. __I am not responsible for any costs.__

Alternatively, you can set up the project on your local machine (see "Run Locally" section).

## Setup
Clone the repository to your local machine:

`git clone https://github.com/Ip1oneerI/aws-data-pipeline`

- Set up your AWS credentials and ensure you have the necessary permissions to create and manage AWS resources.

__WARNING:__ Free tier options are available for AWS, but costs may occur when choosing the wrong payment plan or exceeding limits. __I am not responsible for any costs.__

- Create a MySQL database on AWS RDS and execute the `database_script.sql` to set up the schema and necessary tables.
- Create a new layer in AWS Lambda:
  - Upload the `python.zip` file to run with Python 3.10

  OR

  - Create the file on your local machine:
    - Create a virtual environment and install the necessary dependencies by running `pip install -r requirements.txt`.
    - Navigate to `path\to\my\environment\Lib\site-packages`.
    - Copy the contents of the folder into a new folder called `python`.
    - Copy the `aws_lambda.py` and `aws_lambda_helper.py` files to the `python` folder.
    - Compress the `python` folder and upload it to your layer.

## Usage

### Setting up AWS Lambda functions
- I recommend creating separate AWS Lambda functions for different update schedules:
  - Update city and airport information - only needs to run if a new city was added to the database, you can [create a URL](https://docs.aws.amazon.com/lambda/latest/dg/urls-configuration.html) to run this function manually.
  - Update population information - should be updated yearly; older information will be stored with the respective year.
  - Update weather and arrival flights - should be updated every day to retrieve information for the next day.

- Create the respective Lambda functions and copy the appropriate code from below (don't forget to insert your MySQL endpoint and API credentials).
- Add your layer to the function.
- Create an appropriate CloudWatch event schedule. There is a nice short tutorial [here](https://www.youtube.com/watch?v=lSqd6DVWZ9o&t=1s).

Update cities:
```
import aws_lambda as awsl

def lambda_handler(event, context):
    host = "MY_RDS_ENDPOINT"
    user = "admin"
    password = "MY_PASSWORD"
    api_aerodatabox = "MY_AERODATABOX_KEY"
    
    awsl.lambda_city_updater(host, user, password, api_aerodatabox)
    return {}
```

Update population:
```
import aws_lambda as awsl

def lambda_handler(event, context):
    host = "MY_RDS_ENDPOINT"
    user = "admin"
    password = "MY_PASSWORD"
    
    awsl.lambda_population_updater(host, user, password)
    return {}
```

Update flights & weather:
```
import aws_lambda as awsl

def lambda_handler(event, context):
    host = "MY_RDS_ENDPOINT"
    user = "admin"
    password = "MY_PASSWORD"

    api_openweather = "MY_OPENWEATHER_KEY"
    api_aerodatabox = "MY_AERODATABOX_KEY"
    
    awsl.lambda_daily_updater(host, user, password, api_aerodatabox, api_openweather)
    return {}
```

### Inserting data
- To insert some city data, add the city names to the `name` column in the `cities` table, for example, using MySQL:

  `INSERT INTO cities (name) VALUES ("Frankfurt"), ("Hannover"), ("Berlin");`

- Run the update cities and update population Lambda functions, for example, by calling the URLs to complete the information.
- Weather and flights data should be getting updated according to your schedule.

# Run Locally
If you don't want to run on AWS, you can install and set up a local MySQL server on your machine. Refer to the MySQL documentation [here](https://dev.mysql.com/doc/mysql-getting-started/en/).

## Setup
- Clone the repository to your local machine: `git clone https://github.com/Ip1oneerI/aws-data-pipeline`
- Install the necessary dependencies by running `pip install -r requirements.txt` or set up a virtual environment.
- Execute the `database_script.sql` to set up the schema and necessary tables on your local instance.
- To insert some city data, add the city names to the `name` column in the `cities` table:

  `INSERT INTO cities (name) VALUES ("Frankfurt"), ("Hannover"), ("Berlin");`

## Usage
- To update the database, navigate to the project's folder and run the updater functions in `aws_lambda.py` from your console:

  (You need to pass your local instance and API credentials as arguments)
```
C:\path\to\project> python -c "import aws_lambda; aws_lambda.lambda_city_updater('127.0.0.1','root','MY_LOCAL_PASSWORD','MY_AERODATABOX_KEY')"
C:\path\to\project>  python -c "import aws_lambda; aws_lambda.lambda_population_updater('127.0.0.1','root','MY_LOCAL_PASSWORD')"
C:\path\to\project>  python -c "import aws_lambda; aws_lambda.lambda_daily_updater('127.0.0.1','root','MY_LOCAL_PASSWORD','MY_AERODATABOX_KEY','MY_OPENWEATHER_KEY')"
```
