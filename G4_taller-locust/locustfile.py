from locust import HttpUser, task, between
import random

class InferenceUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def predict(self):
        payload = {
            "culmen_length_mm": random.uniform(30.0, 60.0),
            "culmen_depth_mm": random.uniform(13.0, 21.0),
            "flipper_length_mm": random.uniform(170.0, 230.0),
            "body_mass_g": random.uniform(2700.0, 6300.0),
            "island": random.choice(["Torgersen", "Biscoe", "Dream"]),
            "sex": random.choice(["MALE", "FEMALE"])
        }
        self.client.post("/predict", json=payload)
