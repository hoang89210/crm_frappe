"""Vietnamese phone normalize + extract for pushesale.

Rules (from plan):
- Strip spaces, dots, dashes.
- `84...` (11 digits) -> `+84...`
- `0...` (10 digits) -> `+84` + last 9 digits
- Valid mobile: ^(?:\\+84|84|0)(3|5|7|8|9)\\d{8}$
- Display form `mobile_no`: `0xxxxxxxxx`, key form `custom_phone_e164`: `+84xxxxxxxxx`
"""

import re

_VALID_RE = re.compile(r"^(?:\+84|84|0)(3|5|7|8|9)\d{8}$")
# Candidate chunks: digit runs possibly separated by space/dot/dash, min 9 chars
_CANDIDATE_RE = re.compile(r"\+?\d[\d.\s\-]{7,}\d")


def normalize_vn(raw):
	"""Return E.164 `+84...` or None if not a valid VN mobile."""
	if not raw:
		return None
	cleaned = re.sub(r"[\s.\-]", "", str(raw).strip())
	if not _VALID_RE.match(cleaned):
		return None
	if cleaned.startswith("+84"):
		return cleaned
	if cleaned.startswith("84"):
		return "+" + cleaned
	# starts with 0
	return "+84" + cleaned[1:]


def display_vn(e164):
	"""`+84912345678` -> `0912345678`. Returns input if not E.164."""
	if e164 and e164.startswith("+84"):
		return "0" + e164[3:]
	return e164


def extract_vn_phones(text):
	"""Extract unique valid VN mobiles from free text, in order of appearance."""
	if not text:
		return []
	found = []
	for m in _CANDIDATE_RE.finditer(str(text)):
		e164 = normalize_vn(m.group(0))
		if e164 and e164 not in found:
			found.append(e164)
	return found
