package local.pushesale.callbridge

import okhttp3.Cookie
import okhttp3.CookieJar
import okhttp3.FormBody
import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class FrappeApi {
    private val jar = MemoryCookieJar()
    private val client = OkHttpClient.Builder()
        .cookieJar(jar)
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(20, TimeUnit.SECONDS)
        .build()

    var base: String = ""
        set(value) { field = value.trimEnd('/') }

    fun login(email: String, password: String) {
        val body = FormBody.Builder()
            .add("usr", email)
            .add("pwd", password)
            .build()
        call("POST", "login", body = body)
    }

    fun logout() {
        try {
            val body = FormBody.Builder().build()
            call("POST", "logout", body = body)
        } catch (_: Exception) {
        }
        jar.clear()
    }

    fun registerDevice(deviceName: String): JSONObject {
        val json = JSONObject().put("device_name", deviceName)
        val msg = call("POST", "pushesale.api.call.register_device", json = json)
        return msg as JSONObject
    }

    fun poll(deviceToken: String): JSONObject {
        val msg = call(
            "GET",
            "pushesale.api.call.poll",
            query = mapOf("device_token" to deviceToken),
        )
        return if (msg is JSONObject) msg else JSONObject().put("job", JSONObject.NULL)
    }

    fun disposition(
        deviceToken: String,
        job: String,
        ketQua: String,
        lyDo: String,
        ngayHen: String?,
    ): JSONObject {
        val json = JSONObject()
            .put("device_token", deviceToken)
            .put("job", job)
            .put("ket_qua", ketQua)
            .put("ly_do", lyDo)
        if (ngayHen != null) json.put("ngay_hen", ngayHen)
        else json.put("ngay_hen", JSONObject.NULL)
        val msg = call("POST", "pushesale.api.call.disposition", json = json)
        return msg as JSONObject
    }

    fun skipJob(deviceToken: String, job: String): JSONObject {
        val json = JSONObject()
            .put("device_token", deviceToken)
            .put("job", job)
        val msg = call("POST", "pushesale.api.call.skip_job", json = json)
        return if (msg is JSONObject) msg else JSONObject()
    }

    private fun call(
        method: String,
        apiMethod: String,
        query: Map<String, String> = emptyMap(),
        body: FormBody? = null,
        json: JSONObject? = null,
    ): Any? {
        if (base.isBlank()) throw RuntimeException("Chưa nhập địa chỉ Frappe.")
		val urlBuilder = "$base/api/method/$apiMethod".toHttpUrlOrNull()?.newBuilder()
            ?: throw RuntimeException("URL Frappe không hợp lệ.")
        query.forEach { (k, v) -> urlBuilder.addQueryParameter(k, v) }
        val req = Request.Builder()
            .url(urlBuilder.build())
            .header("Accept", "application/json")
        when {
            json != null -> {
                val media = "application/json; charset=utf-8".toMediaType()
                req.post(json.toString().toRequestBody(media))
            }
            body != null -> req.method(method, body)
            method == "GET" -> req.get()
            else -> req.method(method, FormBody.Builder().build())
        }
        client.newCall(req.build()).execute().use { resp ->
            val text = resp.body?.string() ?: ""
            val parsed = try {
                JSONObject(text)
            } catch (_: Exception) {
                JSONObject()
            }
            if (!resp.isSuccessful) {
                throw RuntimeException(extractError(parsed, resp.code))
            }
            return if (parsed.has("message")) parsed.get("message") else parsed
        }
    }

    private fun extractError(j: JSONObject, code: Int): String {
        var msg = "HTTP $code"
        if (j.has("exc_type")) msg = j.optString("exc_type", msg)
        try {
            val raw = j.optString("_server_messages", "")
            if (raw.isNotBlank()) {
                val arr = JSONArray(raw)
                if (arr.length() > 0) {
                    val first = JSONObject(arr.getString(0))
                    val m = first.optString("message", "")
                    if (m.isNotBlank()) msg = m
                }
            }
        } catch (_: Exception) {
        }
        return msg
    }
}

private class MemoryCookieJar : CookieJar {
    private val store = mutableMapOf<String, MutableList<Cookie>>()

    @Synchronized
    override fun saveFromResponse(url: HttpUrl, cookies: List<Cookie>) {
        val list = store.getOrPut(url.host) { mutableListOf() }
        cookies.forEach { incoming ->
            list.removeAll { it.name == incoming.name }
            list.add(incoming)
        }
    }

    @Synchronized
    override fun loadForRequest(url: HttpUrl): List<Cookie> {
        return store[url.host]?.toList() ?: emptyList()
    }

    @Synchronized
    fun clear() {
        store.clear()
    }
}
