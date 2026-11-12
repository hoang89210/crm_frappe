"""Tiny HTTP helper so tests can patch one function."""


def http_json(method, url, headers=None, params=None, json_body=None, timeout=15):
	import requests

	resp = requests.request(
		method,
		url,
		headers=headers or {},
		params=params,
		json=json_body,
		timeout=timeout,
	)
	try:
		data = resp.json()
	except Exception:
		data = {"text": (resp.text or "")[:500]}
	return resp.status_code, data
