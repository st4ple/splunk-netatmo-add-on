# :thermometer::electric_plug: Netatmo TA for Splunk
> **WARNING**: This TA is still under construction. Future updates might break existing setups so proceed with care! 

## Installation
#### via GIT:
Clone this repository to $SPLUNK_HOME/etc/apps/ on an Indexer or Heavy Forwarder and restart Splunk.

````
$ git clone https://github.com/st4ple/splunk-netatmo-add-on.git
$ splunk restart
````

#### via Splunk UI:

Download the [.zip directory of this repository](https://github.com/st4ple/splunk-netatmo-add-on/archive/master.zip) and upload it to your Splunk instance via 

`Apps -> Manage Apps -> Install App from File`.


## Configuration 

Prerequisites: Client API id & secret for an App from the [Netatmo Connect Developer Portal](https://dev.netatmo.com/) with the following scopes enabled:

* read_station
* read_thermostat

Add the API key and secret to a (new) file named app_config.py in the apps `bin/` directory (`$SPLUNK_HOME/etc/apps/splunk-netatmo-add-on/bin/app_config.py`) like this:

```
client_id = "<client_id>"
client_secret = "<client_secret>"
````
Note: Make sure to include \" before and after the `client_id` and `client_secret` to comply to Python's syntax.
#### via Splunk UI:

Navigate to 

`Settings -> Data inputs -> Local Inputs -> Netatmo -> New` 

and fill out the required parameters.

#### via .conf files:

Add a stanza like this to an inputs.conf file (replace parts in <> brackets):

```YAML
[netatmo://<unique stanza title>]
host = Netatmo
index = <index>
interval = 300               
password = <netatmo_account_password>
sourcetype = _json
username = <netatmo_account_username>
```
Note: It makes no sense to set a smaller interval than 300\[s\] as the refresh-rate of the station data seems to be exactly 5 mins. 
 
## Example event:
```json
{
  "_id": "xx:xx:xx:xx:xx:xx", 
  "co2_calibrating": false, 
  "dashboard_data": 
  {
    "AbsolutePressure": 953.2, 
    "CO2": 492, 
    "Humidity": 42, 
    "Noise": 45,
    "Pressure": 1020.9, 
    "Temperature": 21, 
    "date_max_temp": 1570786498, 
    "date_min_temp": 1570774914, 
    "max_temp": 21.5, "min_temp": 20, 
    "pressure_trend": "stable", 
    "temp_trend": "stable", 
    "time_utc": 1570797206
  }, 
  "data_type": ["Temperature", "CO2", "Humidity", "Noise", "Pressure"], 
  "date_setup": 1526465125, 
  "firmware": 134, 
  "last_setup": 1526465125, 
  "last_status_store": 1570797232, 
  "last_upgrade": 1565246446, 
  "module_name": "Indoor", 
  "modules": [
    {
      "_id": "xx:xx:xx:xx:xx:xx", 
      "battery_percent": 67, 
      "battery_vp": 5216, 
      "dashboard_data": 
      {
        "Humidity": 71, 
        "Temperature": 17.4, 
        "date_max_temp": 1570797167, 
        "date_min_temp": 1570773099, 
        "max_temp": 17.4, 
        "min_temp": 3.1, 
        "temp_trend": "up", 
        "time_utc": 1570797167
       }, 
       "data_type": ["Temperature", "Humidity"], 
       "firmware": 46, 
       "last_message": 1570797225, 
       "last_seen": 1570797218, 
       "last_setup": 1526465183, 
       "module_name": "Terrasse", 
       "reachable": true, 
       "rf_status": 48, "type": 
       "NAModule1"
     }, 
     {
       "_id": "xx:xx:xx:xx:xx:xx",        
       "battery_percent": 83, 
       "battery_vp": 5700, 
       "dashboard_data": 
       {
        "CO2": 463, 
        "Humidity": 38, 
        "Temperature": 23.1, 
        "date_max_temp": 1570797167, 
        "date_min_temp": 1570770946, 
        "max_temp": 23.1, 
        "min_temp": 20.7, 
        "temp_trend": "up", 
        "time_utc": 1570797167
      }, 
     "data_type": ["Temperature", "CO2", "Humidity"], 
     "firmware": 44, 
     "last_message": 1570797225, 
     "last_seen": 1570797218, 
     "last_setup": 1526465761, 
     "module_name": "Sitzungszimmer", 
     "reachable": true, 
     "rf_status": 54, 
     "type": "NAModule4"
     },
     {
       "_id": "xx:xx:xx:xx:xx:xx", 
       "battery_percent": 53, 
       "battery_vp": 5151, 
       "dashboard_data": 
         {
           "CO2": 460, 
           "Humidity": 39, 
           "Temperature": 22.7, 
           "date_max_temp": 1570797167, 
           "date_min_temp": 1570771253, 
           "max_temp": 22.7, 
           "min_temp": 21.3, 
           "temp_trend": "up", 
           "time_utc": 1570797167
         }, 
       "data_type": ["Temperature", "CO2", "Humidity"], 
       "firmware": 44, 
       "last_message": 1570797225, 
       "last_seen": 1570797219, 
       "last_setup": 1526465894, 
       "module_name": "Attika", 
       "reachable": true, 
       "rf_status": 75, 
       "type": "NAModule4"
     }
   ], 
   "place":
     {
       "altitude": 500, 
       "city": "Zurich", 
       "country": "CH", 
       "location": [1.111, 2.222], 
       "timezone": "Europe/Zurich"
     }, 
   "reachable": true, 
   "read_only": true, 
   "station_name": "Headquarter", 
   "type": "NAMain", 
   "wifi_status": 72
 }
```
