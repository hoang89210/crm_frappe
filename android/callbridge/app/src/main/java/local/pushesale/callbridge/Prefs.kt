package local.pushesale.callbridge

import android.content.Context

class Prefs(ctx: Context) {
    private val sp = ctx.getSharedPreferences("callbridge", Context.MODE_PRIVATE)

    var baseUrl: String
        get() = sp.getString("base", "") ?: ""
        set(v) { sp.edit().putString("base", v).apply() }

    var email: String
        get() = sp.getString("email", "") ?: ""
        set(v) { sp.edit().putString("email", v).apply() }

    var token: String
        get() = sp.getString("token", "") ?: ""
        set(v) { sp.edit().putString("token", v).apply() }

    var deviceName: String
        get() = sp.getString("device", "") ?: ""
        set(v) { sp.edit().putString("device", v).apply() }

    fun clearSession() {
        sp.edit().remove("email").remove("token").remove("device").apply()
    }
}
