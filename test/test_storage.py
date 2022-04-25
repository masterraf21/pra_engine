import unittest
from src.storage.redis import init_redis
from src.storage.repository import StorageRepository
from src.critical_path.models import CriticalPath, PathDuration

events = []


class TestStorage(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
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

    async def test_retrieve_duration(self):
        key = "test_duration"
        val = [0.9 for i in range(10)]
        await self.repo.store_json(key, val)
        durations = await self.repo.retrieve_durations(key)
        self.assertEqual(len(durations), 10)
        self.assertEqual(val, durations)

    async def test_retrieve_critical_path(self):
        key = "test_critical_path"
        cp = CriticalPath(
            durations=[
                PathDuration(
                    counter=100,
                    duration=100.2,
                    operation="Hehe"
                )
                for i in range(5)
            ],
            root="hihi"
        )
        cp_dict = cp.dict()
        val = [cp_dict for i in range(3)]
        await self.repo.store_json(key, val)
        cp_real = await self.repo.retrieve_critical_path(key)
        self.assertEqual(len(cp_real), 3)
        self.assertEqual(cp, cp_real[0])
