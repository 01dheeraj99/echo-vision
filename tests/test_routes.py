import unittest
from io import BytesIO
from app import app

class TestEchoVisionRoutes(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"EchoVision", response.data)
        self.assertIn(b"Spoken Narration", response.data)
        self.assertIn(b"contrast-toggle", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "healthy")
        self.assertEqual(json_data["app"], "EchoVision")

    def test_analyze_no_data(self):
        response = self.client.post("/analyze", data={})
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])

    def test_analyze_disallowed_extension(self):
        data = {
            "image": (BytesIO(b"fake data"), "malicious.exe")
        }
        response = self.client.post("/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertFalse(json_data["success"])
        self.assertIn("Invalid image format", json_data["error"])

    def test_404_error_handler(self):
        response = self.client.get("/nonexistent-page-url")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()

