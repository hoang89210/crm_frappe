<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-base p-4">
    <h1 class="mb-3 text-xl font-semibold text-ink-gray-9">Kênh</h1>
    <p class="mb-4 text-sm text-ink-gray-6">{{ status }}</p>

    <section class="mb-4 rounded-lg border bg-surface-white p-4">
      <h2 class="mb-2 text-base font-medium">Chatwoot inbox</h2>
      <label class="field">Chatwoot URL</label>
      <input v-model="form.chatwoot_url" class="input" placeholder="http://127.0.0.1:3000" />
      <label class="field">Account ID</label>
      <input v-model="form.chatwoot_account_id" class="input" />
      <label class="field">API token</label>
      <input v-model="form.chatwoot_api_token" class="input" type="password" placeholder="để trống nếu giữ nguyên" />
      <label class="field">Webhook secret</label>
      <input v-model="form.chatwoot_webhook_secret" class="input" type="password" />
      <label class="field">URL webhook</label>
      <textarea v-model="form.chatwoot_webhook_url" class="input" rows="2" readonly />
      <label class="check"><input v-model="form.chatwoot_sync_enabled" type="checkbox" /> Tự đồng bộ inbox mỗi 10 phút</label>
      <div class="row">
        <button class="btn" @click="testChatwoot">Kiểm tra kết nối</button>
        <button class="btn primary" @click="syncInbox">Đồng bộ inbox</button>
      </div>
      <button class="btn" @click="save">Lưu Chatwoot</button>
      <p class="hint">{{ form.chatwoot_last_result }}</p>
    </section>

    <section class="mb-4 rounded-lg border bg-surface-white p-4">
      <h2 class="mb-2 text-base font-medium">Facebook Page (nhiều Page)</h2>
      <p class="hint">Mỗi Page cần 1 Page Access Token. Cần Admin Page + Meta App (Development).</p>
      <div v-for="p in fbPages" :key="p.name" class="page-row">
        <div class="flex-1">
          <div class="font-medium">{{ p.page_name }} <span class="muted">({{ p.page_id }})</span></div>
          <div class="muted">{{ p.last_result || 'Chưa đồng bộ' }}</div>
        </div>
        <label class="check"><input type="checkbox" :checked="!!p.sync_enabled" @change="togglePage(p)" /> Tự đồng bộ</label>
        <button class="btn" @click="syncOnePage(p)">Đồng bộ</button>
        <button class="btn danger" @click="removePage(p)">Xóa</button>
      </div>
      <p v-if="!fbPages.length" class="hint">Chưa có Page nào.</p>
      <div class="grid gap-2 md:grid-cols-4">
        <input v-model="fbForm.page_url" class="input" placeholder="Link Page" />
        <input v-model="fbForm.page_name" class="input" placeholder="Tên Page (tùy chọn)" />
        <input v-model="fbForm.access_token" class="input" type="password" placeholder="Page Access Token" />
        <div class="row">
          <button class="btn" @click="testPage">Kiểm tra token</button>
          <button class="btn primary" @click="savePage">Lưu Page</button>
        </div>
      </div>
      <button class="btn" @click="syncAllPages">Đồng bộ tất cả Page</button>
      <p class="hint">{{ fbHint }}</p>
    </section>

    <section class="rounded-lg border bg-surface-white p-4">
      <h2 class="mb-2 text-base font-medium">Facebook comment</h2>
      <label class="field">Link Facebook page</label>
      <input v-model="form.facebook_page_url" class="input" />
      <label class="field">Page Access Token</label>
      <input v-model="form.facebook_access_token" class="input" type="password" />
      <label class="field">Page đã nhận diện</label>
      <input class="input" readonly :value="pageLabel" />
      <label class="check"><input v-model="form.facebook_sync_enabled" type="checkbox" /> Tự đồng bộ comment mỗi 10 phút</label>
      <div class="row">
        <button class="btn" @click="testFacebook">Kiểm tra token</button>
        <button class="btn primary" @click="syncFacebook">Đồng bộ comment</button>
      </div>
      <button class="btn" @click="save">Lưu Facebook</button>
      <p class="hint">{{ form.facebook_last_result }}</p>
    </section>
  </div>
</template>

<script setup>
import { call } from 'frappe-ui'
import { computed, onMounted, reactive, ref } from 'vue'

const status = ref('Đang tải cấu hình...')
const form = reactive({
  chatwoot_url: '',
  chatwoot_account_id: '',
  chatwoot_api_token: '',
  chatwoot_webhook_secret: '',
  chatwoot_webhook_url: '',
  chatwoot_sync_enabled: false,
  chatwoot_last_result: '',
  facebook_page_url: '',
  facebook_access_token: '',
  facebook_page_id: '',
  facebook_page_name: '',
  facebook_sync_enabled: true,
  facebook_last_result: '',
})

const fbPages = ref([])
const fbHint = ref('')
const fbForm = reactive({ page_url: '', page_name: '', access_token: '' })

const pageLabel = computed(() => {
  const name = form.facebook_page_name || ''
  const id = form.facebook_page_id ? ` (${form.facebook_page_id})` : ''
  return (name + id).trim()
})

function fill(s) {
  if (!s) return
  Object.assign(form, {
    chatwoot_url: s.chatwoot_url || '',
    chatwoot_account_id: s.chatwoot_account_id || '',
    chatwoot_api_token: s.chatwoot_api_token || '',
    chatwoot_webhook_secret: s.chatwoot_webhook_secret || '',
    chatwoot_webhook_url: s.chatwoot_webhook_url || '',
    chatwoot_sync_enabled: !!s.chatwoot_sync_enabled,
    chatwoot_last_result: s.chatwoot_last_result || '',
    facebook_page_url: s.facebook_page_url || '',
    facebook_access_token: s.facebook_access_token || '',
    facebook_page_id: s.facebook_page_id || '',
    facebook_page_name: s.facebook_page_name || '',
    facebook_sync_enabled: s.facebook_sync_enabled !== 0,
    facebook_last_result: s.facebook_last_result || '',
  })
}

function payload() {
  return {
    chatwoot_url: form.chatwoot_url.trim(),
    chatwoot_account_id: String(form.chatwoot_account_id || '').trim(),
    chatwoot_api_token: form.chatwoot_api_token,
    chatwoot_webhook_secret: form.chatwoot_webhook_secret,
    chatwoot_sync_enabled: form.chatwoot_sync_enabled ? 1 : 0,
    facebook_page_url: form.facebook_page_url.trim(),
    facebook_access_token: form.facebook_access_token,
    facebook_sync_enabled: form.facebook_sync_enabled ? 1 : 0,
  }
}

function err(e) {
  return e?.messages?.[0] || e?.message || String(e)
}

async function load() {
  const s = await call('pushesale.api.settings.get_settings')
  fill(s)
  await loadPages()
  status.value = 'Đã tải cấu hình.'
}

async function loadPages() {
  try {
    fbPages.value = await call('pushesale.api.fb_pages.list_pages')
  } catch (e) {
    fbHint.value = 'Lỗi tải Page: ' + err(e)
  }
}

async function testPage() {
  fbHint.value = 'Đang kiểm tra token...'
  try {
    const r = await call('pushesale.api.fb_pages.test_page', {
      page_url: fbForm.page_url,
      access_token: fbForm.access_token,
    })
    fbHint.value = `OK: ${r.page_name} (${r.page_id})`
  } catch (e) {
    fbHint.value = 'Lỗi token: ' + err(e)
  }
}

async function savePage() {
  fbHint.value = 'Đang lưu Page...'
  try {
    const r = await call('pushesale.api.fb_pages.save_page', {
      page_url: fbForm.page_url,
      page_name: fbForm.page_name,
      access_token: fbForm.access_token,
      sync_enabled: 1,
    })
    fbForm.page_url = ''
    fbForm.page_name = ''
    fbForm.access_token = ''
    fbHint.value = `Đã lưu ${r.page_name}.`
    await loadPages()
  } catch (e) {
    fbHint.value = 'Lỗi lưu Page: ' + err(e)
  }
}

async function syncOnePage(p) {
  fbHint.value = `Đang đồng bộ ${p.page_name}...`
  try {
    const r = await call('pushesale.api.fb_pages.sync_page', { name: p.name })
    fbHint.value = r.result || r.error || ''
    await loadPages()
  } catch (e) {
    fbHint.value = 'Lỗi đồng bộ: ' + err(e)
  }
}

async function syncAllPages() {
  fbHint.value = 'Đang đồng bộ tất cả Page...'
  try {
    const r = await call('pushesale.api.fb_pages.sync_all')
    fbHint.value = r.result || JSON.stringify(r)
    await loadPages()
  } catch (e) {
    fbHint.value = 'Lỗi đồng bộ: ' + err(e)
  }
}

async function togglePage(p) {
  try {
    await call('pushesale.api.fb_pages.save_page', {
      name: p.name,
      page_name: p.page_name,
      page_url: p.page_url,
      sync_enabled: p.sync_enabled ? 0 : 1,
    })
    await loadPages()
  } catch (e) {
    fbHint.value = 'Lỗi đổi chế độ: ' + err(e)
  }
}

async function removePage(p) {
  if (!window.confirm(`Xóa Page ${p.page_name}?`)) return
  try {
    await call('pushesale.api.fb_pages.delete_page', { name: p.name })
    await loadPages()
  } catch (e) {
    fbHint.value = 'Lỗi xóa Page: ' + err(e)
  }
}

async function save() {
  status.value = 'Đang lưu...'
  try {
    fill(await call('pushesale.api.settings.save_settings', payload()))
    status.value = 'Đã lưu.'
  } catch (e) {
    status.value = 'Lỗi lưu: ' + err(e)
  }
}

async function testChatwoot() {
  status.value = 'Đang kiểm tra Chatwoot...'
  try {
    const p = payload()
    const r = await call('pushesale.api.chatwoot.test_connection', {
      chatwoot_url: p.chatwoot_url,
      chatwoot_api_token: p.chatwoot_api_token,
      chatwoot_account_id: p.chatwoot_account_id,
    })
    status.value = 'Chatwoot OK: ' + (r?.name || '') 
    await load()
  } catch (e) {
    status.value = 'Lỗi Chatwoot: ' + err(e)
  }
}

async function syncInbox() {
  status.value = 'Đang đồng bộ inbox...'
  try {
    await call('pushesale.api.settings.save_settings', payload())
    const r = await call('pushesale.api.chatwoot.sync_inbox')
    status.value = r?.result || JSON.stringify(r)
    await load()
  } catch (e) {
    status.value = 'Lỗi đồng bộ inbox: ' + err(e)
  }
}

async function testFacebook() {
  status.value = 'Đang kiểm tra Facebook...'
  try {
    const p = payload()
    const r = await call('pushesale.api.meta.test_connection', {
      facebook_page_url: p.facebook_page_url,
      facebook_access_token: p.facebook_access_token,
    })
    status.value = 'Facebook OK: ' + (r?.page_name || '') + ' (' + (r?.page_id || '') + ')'
    await load()
  } catch (e) {
    status.value = 'Lỗi Facebook: ' + err(e)
  }
}

async function syncFacebook() {
  status.value = 'Đang đồng bộ comment...'
  try {
    await call('pushesale.api.settings.save_settings', payload())
    const r = await call('pushesale.api.meta.sync_recent')
    status.value = r?.result || JSON.stringify(r)
    await load()
  } catch (e) {
    status.value = 'Lỗi đồng bộ comment: ' + err(e)
  }
}

onMounted(() => {
  load().catch((e) => {
    status.value = 'Không tải được cấu hình: ' + err(e)
  })
})
</script>

<style scoped>
.field { display: block; margin-top: 8px; font-size: 13px; color: #555; }
.input { width: 100%; margin-top: 4px; border: 1px solid #ddd; border-radius: 8px; padding: 8px; font-size: 14px; }
.check { display: flex; gap: 8px; align-items: center; margin-top: 10px; font-size: 14px; }
.check input { width: auto; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.btn { width: 100%; margin-top: 8px; border: 0; border-radius: 8px; padding: 10px; background: #e5e7eb; cursor: pointer; }
.btn.primary { background: #1f6feb; color: #fff; }
.hint { margin-top: 8px; font-size: 12px; color: #666; white-space: pre-wrap; }
.page-row { display: flex; align-items: center; gap: 8px; border-top: 1px solid #eee; padding: 8px 0; }
.page-row .btn { width: auto; margin-top: 0; }
.btn.danger { background: #fee2e2; }
.muted { font-size: 12px; color: #888; }
</style>
