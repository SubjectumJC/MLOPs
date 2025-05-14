from locust import HttpUser, task, between
import random, requests, json

FEATURES = [
    'time_in_hospital','num_lab_procedures','num_procedures',
    'num_medications','number_outpatient','number_emergency',
    'number_inpatient','number_diagnoses'
]

class InferenceUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def predict(self):
        attrs = [random.random() for _ in FEATURES]
        self.client.post("/predict", json={"attributes": attrs})

