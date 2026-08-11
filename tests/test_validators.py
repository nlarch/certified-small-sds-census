import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import parse_name, witness_from_record
from sds.validator_independent import validate as validate_independent
from sds.validator_reference import validate as validate_reference


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = json.loads(
            (ROOT / "sources" / "signed-difference-sets" / "sds.json").read_text()
        )

    def repository_vector(self, name):
        instance = parse_name(name)
        positive, negative = self.dataset[name]["sets"][0]
        return instance, witness_from_record(instance, positive, negative)

    def test_known_positive_cyclic(self):
        instance, vector = self.repository_vector("SDS(5,4,-1,[5])")
        self.assertTrue(validate_reference(instance, vector)["valid"])
        self.assertTrue(validate_independent(instance, vector)["valid"])

    def test_known_positive_noncyclic(self):
        instance, vector = self.repository_vector("SDS(9,8,-1,[3,3])")
        self.assertTrue(validate_reference(instance, vector)["valid"])
        self.assertTrue(validate_independent(instance, vector)["valid"])

    def test_invalid_vector_rejected(self):
        instance = parse_name("SDS(9,8,1,[3,3])")
        vector = (0, 1, 1, 1, 1, 1, 1, -1, -1)
        self.assertFalse(validate_reference(instance, vector)["valid"])
        self.assertFalse(validate_independent(instance, vector)["valid"])


if __name__ == "__main__":
    unittest.main()
