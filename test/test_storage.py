import unittest
from src.storage.redis import init_redis
from src.storage.repository import StorageRepository

events = []


class TestStorage(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        events.append("setUp")
        return super().setUp()

    def tearDown(self) -> None:
        events.append("tearDown")
        return super().tearDown()

    async def asyncSetUp(self) -> None:
        print("Setup Class")
        self.redis = await init_redis()
        self.repo = StorageRepository(self.redis)
        return await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        await self.redis.close()
        return await super().asyncTearDown()

    async def test_init_redis(self):
        self.assertTrue(await self.redis.ping())

    async def test_store_json(self):
        key = "test_key"
        val = {"A": 1}
        await self.repo.store_json(key, val)
        val_get = await self.redis.json().get(key)
        self.assertEqual(val, val_get)
