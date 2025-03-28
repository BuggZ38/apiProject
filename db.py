from influxdb_client import InfluxDBClient, Point, WritePrecision

class DB:

    def __init__(self, url, token, org, bucket):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=WritePrecision.NS)
        self.query_api = self.client.query_api()
        self.bucket = bucket
        self.org = org

    def write_data(self, entity_id, stat, power):
        try:
            point = (
                Point("luminaire")
                .tag("id", entity_id)
                .field("etat", stat)  # 1 = ON, 0 = OFF
                .field("puissance", power)  # En watts
            )
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            return True
        except Exception as e:
            print(f"Erreur lors de l'écriture dans InfluxDB : {e}")
            return False

    def read_data(self, entity_type, entity_id=None):
        try:
            query = f'from(bucket:"{self.bucket}") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "{entity_type}")'

            if entity_id:
                query += f' |> filter(fn: (r) => r.id == "{entity_id}")'

            result = self.query_api.query(org=self.org, query=query)

            donnees = []
            for table in result:
                for record in table.records:
                    data_point = {"time": record.get_time(), "id": record.values.get("id")}
                    for key, value in record.values.items():
                        if key not in ["result", "table", "_measurement", "id", "_time"]:
                            data_point[key] = value
                    donnees.append(data_point)

            return donnees
        except Exception as e:
            print(f"Erreur lors de la lecture depuis InfluxDB : {e}")
            return []