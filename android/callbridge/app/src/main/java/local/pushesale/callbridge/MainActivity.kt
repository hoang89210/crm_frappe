package local.pushesale.callbridge

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.GridLayout
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {
    private val api = FrappeApi()
    private val io = Executors.newSingleThreadExecutor()
    private val ui = Handler(Looper.getMainLooper())
    private lateinit var prefs: Prefs

    private var polling = false
    private var currentJob: JSONObject? = null
    private var pollRunnable: Runnable? = null

    private val results = listOf(
        "Khong nghe", "Thue bao", "Ban goi lai", "Can cham tiep",
        "Hen goi lai", "Chot", "Churn",
    )
    private val labels = mapOf(
        "Khong nghe" to "Không nghe",
        "Thue bao" to "Thuê bao",
        "Ban goi lai" to "Bận gọi lại",
        "Can cham tiep" to "Cần chăm tiếp",
        "Hen goi lai" to "Hẹn gọi lại",
        "Chot" to "Chốt",
        "Churn" to "Churn",
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        prefs = Prefs(this)

        findViewById<EditText>(R.id.baseUrl).setText(prefs.baseUrl)
        findViewById<EditText>(R.id.email).setText(prefs.email)
        if (prefs.deviceName.isNotBlank()) {
            findViewById<EditText>(R.id.deviceName).setText(prefs.deviceName)
        }
        api.base = prefs.baseUrl
        if (prefs.email.isNotBlank() && prefs.token.isNotBlank()) {
            showBound()
        }

        findViewById<Button>(R.id.loginBtn).setOnClickListener { login() }
        findViewById<Button>(R.id.startBtn).setOnClickListener { startPoll() }
        findViewById<Button>(R.id.stopBtn).setOnClickListener { stopPoll("Đã dừng.") }
        findViewById<Button>(R.id.logoutBtn).setOnClickListener { logout() }
        findViewById<Button>(R.id.dialBtn).setOnClickListener { dial() }
        findViewById<Button>(R.id.skipBtn).setOnClickListener { skip() }

        val grid = findViewById<GridLayout>(R.id.resultGrid)
        results.forEach { code ->
            val b = Button(this)
            b.text = labels[code] ?: code
            b.isAllCaps = false
            val lp = GridLayout.LayoutParams()
            lp.width = 0
            lp.columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f)
            lp.setMargins(4, 4, 4, 4)
            b.layoutParams = lp
            b.setOnClickListener { submitResult(code) }
            grid.addView(b)
        }
    }

    private fun setStatus(msg: String) {
        findViewById<TextView>(R.id.status).text = msg
    }

    private fun showBound() {
        findViewById<View>(R.id.loginForm).visibility = View.GONE
        findViewById<View>(R.id.whoBox).visibility = View.VISIBLE
        findViewById<TextView>(R.id.whoText).text = "Đã gắn máy: ${prefs.email}"
        findViewById<EditText>(R.id.tokenView).setText(prefs.token)
    }

    private fun showLogin(msg: String) {
        findViewById<View>(R.id.loginForm).visibility = View.VISIBLE
        findViewById<View>(R.id.whoBox).visibility = View.GONE
        findViewById<View>(R.id.jobCard).visibility = View.GONE
        findViewById<Button>(R.id.startBtn).visibility = View.VISIBLE
        findViewById<Button>(R.id.stopBtn).visibility = View.GONE
        setStatus(msg)
    }

    private fun login() {
        val base = findViewById<EditText>(R.id.baseUrl).text.toString().trim().trimEnd('/')
        val email = findViewById<EditText>(R.id.email).text.toString().trim()
        val pw = findViewById<EditText>(R.id.password).text.toString()
        val dname = findViewById<EditText>(R.id.deviceName).text.toString().trim()
            .ifBlank { "Dien thoai" }
        if (email.isBlank() || pw.isBlank()) {
            setStatus("Nhập email + mật khẩu.")
            return
        }
        setStatus("Đang đăng nhập...")
        io.execute {
            try {
                api.base = base
                api.login(email, pw)
                ui.post { setStatus("Đăng nhập OK. Đang gắn máy...") }
                val res = api.registerDevice(dname)
                val token = res.optString("device_token")
                prefs.baseUrl = base
                prefs.email = email
                prefs.token = token
                prefs.deviceName = dname
                ui.post {
                    findViewById<EditText>(R.id.password).setText("")
                    showBound()
                    setStatus("Gắn máy xong. Bấm \"Bắt đầu nghe lệnh gọi\".")
                }
            } catch (e: Exception) {
                ui.post {
                    setStatus("Lỗi: ${e.message} (kiểm tra email/mật khẩu, đúng role Sales).")
                }
            }
        }
    }

    private fun startPoll() {
        if (prefs.token.isBlank()) {
            setStatus("Chưa có device token. Đăng nhập lại.")
            return
        }
        polling = true
        findViewById<Button>(R.id.startBtn).visibility = View.GONE
        findViewById<Button>(R.id.stopBtn).visibility = View.VISIBLE
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setStatus("Đang nghe lệnh gọi...")
        pollOnce()
    }

    private fun stopPoll(msg: String) {
        polling = false
        pollRunnable?.let { ui.removeCallbacks(it) }
        findViewById<Button>(R.id.startBtn).visibility = View.VISIBLE
        findViewById<Button>(R.id.stopBtn).visibility = View.GONE
        window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setStatus(msg)
    }

    private fun logout() {
        stopPoll("Đã đăng xuất, xóa gắn máy trên điện thoại này.")
        io.execute { api.logout() }
        prefs.clearSession()
        showLogin("Đã đăng xuất, xóa gắn máy trên điện thoại này.")
    }

    private fun pollOnce() {
        if (!polling) return
        val token = prefs.token
        io.execute {
            try {
                val res = api.poll(token)
                val job = res.opt("job")
                ui.post {
                    if (!polling) return@post
                    if (job != null && job != JSONObject.NULL && job.toString().isNotBlank()) {
                        onJob(res)
                    } else {
                        setStatus("Đang nghe... (${java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault()).format(java.util.Date())})")
                        schedule()
                    }
                }
            } catch (e: Exception) {
                ui.post {
                    if (!polling) return@post
                    setStatus("Lỗi poll: ${e.message}")
                    schedule()
                }
            }
        }
    }

    private fun schedule() {
        if (!polling) return
        val r = Runnable { pollOnce() }
        pollRunnable = r
        ui.postDelayed(r, 3000)
    }

    private fun onJob(job: JSONObject) {
        polling = false
        pollRunnable?.let { ui.removeCallbacks(it) }
        currentJob = job
        findViewById<TextView>(R.id.leadName).text =
            job.optString("lead_name").ifBlank { job.optString("lead") }
        findViewById<TextView>(R.id.leadPhone).text = job.optString("phone")
        findViewById<View>(R.id.jobCard).visibility = View.VISIBLE
        findViewById<View>(R.id.henBox).visibility = View.GONE
        findViewById<EditText>(R.id.lyDo).setText("")
        findViewById<EditText>(R.id.ngayHen).setText("")
        setStatus("Có lệnh gọi mới: ${job.optString("job")}")
    }

    private fun dial() {
        val phone = findViewById<TextView>(R.id.leadPhone).text.toString()
            .replace(Regex("[^\\d+]"), "")
        if (phone.isBlank()) return
        startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$phone")))
    }

    private fun submitResult(ketQua: String) {
        val job = currentJob ?: return
        val henBox = findViewById<View>(R.id.henBox)
        val ngayRaw = findViewById<EditText>(R.id.ngayHen).text.toString().trim()
        if (ketQua == "Hen goi lai" && ngayRaw.isBlank()) {
            henBox.visibility = View.VISIBLE
            setStatus("Chọn giờ hẹn trước khi gửi.")
            return
        }
        if (ketQua == "Hen goi lai") henBox.visibility = View.VISIBLE
        var ngayHen: String? = null
        if (ngayRaw.isNotBlank()) {
            ngayHen = if (ngayRaw.contains("T")) {
                ngayRaw.replace("T", " ") + if (ngayRaw.length <= 16) ":00" else ""
            } else if (ngayRaw.length == 16) {
                "$ngayRaw:00"
            } else {
                ngayRaw
            }
        }
        setStatus("Đang gửi kết quả...")
        val token = prefs.token
        val jobName = job.optString("job")
        val lyDo = findViewById<EditText>(R.id.lyDo).text.toString()
        io.execute {
            try {
                val res = api.disposition(token, jobName, ketQua, lyDo, ngayHen)
                ui.post {
                    resetToPolling(
                        "Đã ghi: $ketQua → lead ${res.optString("care_status")}. Nghe tiếp...",
                    )
                }
            } catch (e: Exception) {
                ui.post { setStatus("Lỗi gửi: ${e.message}") }
            }
        }
    }

    private fun skip() {
        val job = currentJob ?: return
        val token = prefs.token
        val jobName = job.optString("job")
        io.execute {
            try {
                api.skipJob(token, jobName)
                ui.post { resetToPolling("Đã bỏ qua job. Nghe tiếp...") }
            } catch (e: Exception) {
                ui.post { setStatus("Lỗi bỏ qua: ${e.message}") }
            }
        }
    }

    private fun resetToPolling(msg: String) {
        currentJob = null
        findViewById<View>(R.id.jobCard).visibility = View.GONE
        findViewById<EditText>(R.id.lyDo).setText("")
        findViewById<EditText>(R.id.ngayHen).setText("")
        findViewById<View>(R.id.henBox).visibility = View.GONE
        polling = true
        findViewById<Button>(R.id.startBtn).visibility = View.GONE
        findViewById<Button>(R.id.stopBtn).visibility = View.VISIBLE
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setStatus(msg)
        schedule()
    }

    override fun onDestroy() {
        polling = false
        pollRunnable?.let { ui.removeCallbacks(it) }
        io.shutdownNow()
        super.onDestroy()
    }
}
