import unittest

from pushesale.phone import display_vn, extract_vn_phones, normalize_vn


class TestVnPhone(unittest.TestCase):
	def test_normalize_dotted(self):
		self.assertEqual(normalize_vn("0912.345.678"), "+84912345678")

	def test_normalize_plus84_spaced(self):
		self.assertEqual(normalize_vn("+84 912 345 678"), "+84912345678")

	def test_normalize_84_prefix(self):
		self.assertEqual(normalize_vn("84912345678"), "+84912345678")

	def test_reject_old_012_prefix(self):
		self.assertIsNone(normalize_vn("0123456789"))

	def test_reject_price(self):
		self.assertIsNone(normalize_vn("150.000"))

	def test_reject_landline(self):
		self.assertIsNone(normalize_vn("0243823456"))

	def test_display(self):
		self.assertEqual(display_vn("+84912345678"), "0912345678")

	def test_extract_sentence(self):
		self.assertEqual(
			extract_vn_phones("goi minh 0912.345.678 nhe"), ["+84912345678"]
		)

	def test_extract_no_number(self):
		self.assertEqual(extract_vn_phones("khong co so o day"), [])

	def test_extract_skips_price(self):
		self.assertEqual(extract_vn_phones("gia chi 150.000 dong"), [])

	def test_extract_multiple_unique(self):
		self.assertEqual(
			extract_vn_phones("lh 0912345678 hoac 0987654321, goi lai 0912345678"),
			["+84912345678", "+84987654321"],
		)
