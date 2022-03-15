from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient


class TestAPI(TestCase):
    def test_consumingAPI(self):
        client = APIClient()
        response = client.get(
            '/consumeapi/52.923454/-1.474217',
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"][0]["longitude"],-1.474217)

