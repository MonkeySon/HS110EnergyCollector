class HS110EnergyPoint:
    def __init__(self, json_response):
        data = json_response['emeter']['get_realtime']
        self.voltage = data['voltage_mv'] / 1000.0
        self.current = data['current_ma'] / 1000.0
        self.power = data['power_mw'] / 1000.0

    def __str__(self):
        return f'{self.voltage} V, {self.current} A, {self.power} W'
