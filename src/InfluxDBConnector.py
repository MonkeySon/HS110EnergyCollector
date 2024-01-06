from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

def write_point(config, energy_point):
    point = Point(config['measurement']).field('Voltage', energy_point.voltage).field('Current', energy_point.current).field('Watt', energy_point.power)
    client = InfluxDBClient(url=config['url'], token=config['token'], org=config['org'])
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=config['bucket'], record=point)