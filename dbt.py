import os, json, datetime

class Db:


    def __init__(self, file_name='db.json'):
        self.db_file = file_name

        self.data = {
            "sensor": [],
            "data": [],
            "history": []
        }

        self.__load_file()

    def __load_file(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.__save_file()

    def __save_file(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def __close_file(self):
        self.__save_file()

    def __add_history(self, type, hist):
        self.data['history'].append(f"{datetime.datetime.now()} --- Add {type} ({hist})")
        self.__save_file()

    def __add_history_error(self, type, hist):
        self.data['history'].append(f"{datetime.datetime.now()} --- Error {type} ({hist})")
        self.__save_file()

    def clear_db_file(self):
        self.data = {
            "sensor": self.get_sensor(),
            "data": [],
            "history": [],
            "alerts": [],
            "stats": {
                "AI_sender_id": self.data.get("stats", {}).get("AI_sender_id", 0)
            }
        }
        self.__save_file()

    def add_data(self, data):
        if self.__check_data(data):
            self.data['data'].append(data)
            self.__add_history("data", data)
        else:
            self.__add_history_error("data", data)

    def add_sensor(self, sensor):
        data = {"id": self.data['stats']['AI_sender_id'], "sender_ip": sensor}
        if self.__check_sensor(data):
            self.data['sensor'].append(data)
            self.__add_history("sensor", data)
        else:
            self.__add_history_error("sensor", data)

        self.__Incr_id()

    def get_data(self):
        return self.data['data']

    def get_alerts(self):
        return self.data['alerts']

    def get_sensor(self):
        return self.data['sensor']

    def get_history(self):
        return self.data['history']

    def __Incr_id(self):
        current_id = int(self.data.get("stats", {}).get("AI_sender_id", 0))
        new_id = current_id + 1
        self.data["stats"]["AI_sender_id"] = str(new_id)
        self.__save_file()
        return new_id

    @staticmethod
    def __check_data(data):
        if not isinstance(data, dict):
            return False
        if 'sender_id' not in data or not isinstance(data['sender_id'], int):
            return False
        if 'data' not in data:
            return False
        if 'timestamp' not in data:
            return False
        return True

    @staticmethod
    def __check_sensor(sensor):
        if not isinstance(sensor, dict):
            return False
        if 'id' not in sensor:
            return False
        if 'sender_ip' not in sensor or not isinstance(sensor['sender_ip'], str):
            return False
        return True
