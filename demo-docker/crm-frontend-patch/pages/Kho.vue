<template>
  <div class="flex h-full min-h-0 flex-col bg-surface-base">
    <div class="flex items-center justify-between border-b px-4 py-3">
      <div>
        <h1 class="text-xl font-semibold">Kho</h1>
        <p class="text-sm" :class="error ? 'font-medium text-red-600' : 'text-ink-gray-6'">{{ status }}</p>
      </div>
      <button class="btn" @click="openWh()">Thêm kho</button>
    </div>

    <div v-if="wh.open" class="grid gap-2 border-b p-4 md:grid-cols-4">
      <input v-model="wh.warehouse_name" class="input" placeholder="Tên kho" />
      <select v-model="wh.parent" class="input">
        <option value="">Không có cha</option>
        <option v-for="w in parentChoices" :key="w.name" :value="w.name">{{ w.warehouse_name }}</option>
      </select>
      <label class="check"><input v-model="wh.is_group" type="checkbox" /> Là nhóm</label>
      <div class="flex gap-2">
        <button class="btn primary" @click="saveWh">Lưu kho</button>
        <button class="btn" @click="wh.open = false">Đóng</button>
      </div>
    </div>

    <div class="grid gap-2 border-b p-4 md:grid-cols-4">
      <select v-model="entry.entry_type" class="input">
        <option>Nhập</option>
        <option>Xuất</option>
        <option>Điều chuyển</option>
      </select>
      <select v-if="entry.entry_type !== 'Nhập'" v-model="entry.from_warehouse" class="input">
        <option value="">Kho xuất</option>
        <option v-for="w in leaves" :key="w.name" :value="w.name">{{ w.warehouse_name }}</option>
      </select>
      <select v-if="entry.entry_type !== 'Xuất'" v-model="entry.to_warehouse" class="input">
        <option value="">Kho nhập</option>
        <option v-for="w in leaves" :key="'t'+w.name" :value="w.name">{{ w.warehouse_name }}</option>
      </select>
      <button class="btn primary" @click="submit">Ghi sổ</button>
      <div v-for="(line, i) in entry.lines" :key="i" class="grid grid-cols-3 gap-2 md:col-span-4">
        <select v-model="line.item" class="input">
          <option value="">Sản phẩm</option>
          <option v-for="p in products" :key="p.name" :value="p.name">{{ p.product_code }} — {{ p.product_name }}</option>
        </select>
        <input v-model="line.qty" class="input" placeholder="Số lượng" />
        <button class="btn" @click="entry.lines.splice(i, 1)">Bỏ</button>
      </div>
      <button class="btn md:col-span-4" @click="entry.lines.push({ item: '', qty: 1 })">Thêm dòng</button>
    </div>

    <div class="flex min-h-0 flex-1">
      <aside class="w-64 overflow-auto border-r p-3">
        <div v-for="w in flatTree" :key="w.name" class="row" :style="{ paddingLeft: w.depth * 12 + 'px' }">
          <button class="tree-btn" :class="{ on: selected === w.name }" @click="selected = w.name">{{ w.warehouse_name }}</button>
          <button class="mini" @click.stop="openWh(w)">Sửa</button>
          <button class="mini" @click.stop="removeWh(w)">Xóa</button>
        </div>
      </aside>
      <div class="flex-1 overflow-auto p-3">
        <h2 class="mb-2 text-sm font-medium">Tồn {{ selected || 'mọi kho' }}</h2>
        <table class="mb-4 w-full text-sm">
          <thead><tr class="text-left text-ink-gray-6"><th>Mã</th><th>Kho</th><th>Tồn</th></tr></thead>
          <tbody>
            <tr v-for="row in shownBins" :key="row.item + row.warehouse" class="border-t">
              <td class="py-1">{{ row.item }}</td>
              <td>{{ row.warehouse }}</td>
              <td>{{ row.qty }}</td>
            </tr>
          </tbody>
        </table>
        <h2 class="mb-2 text-sm font-medium">Phiếu gần đây</h2>
        <table class="w-full text-sm">
          <thead><tr class="text-left text-ink-gray-6"><th>Mã</th><th>Loại</th><th>Từ</th><th>Đến</th><th></th></tr></thead>
          <tbody>
            <tr v-for="e in entries" :key="e.name" class="border-t">
              <td class="py-1">{{ e.name }}</td>
              <td>{{ e.entry_type }}</td>
              <td>{{ e.from_warehouse }}</td>
              <td>{{ e.to_warehouse }}</td>
              <td><button v-if="e.docstatus === 1" class="mini" @click="cancel(e.name)">Hủy</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { call } from 'frappe-ui'
import { computed, onMounted, reactive, ref } from 'vue'

const status = ref('Đang tải...')
const error = ref(false)
const warehouses = ref([])
const products = ref([])
const bins = ref([])
const entries = ref([])
const selected = ref('Kho chính')
const wh = reactive({ open: false, old_name: '', warehouse_name: '', parent: '', is_group: false })
const entry = reactive({
  entry_type: 'Nhập',
  from_warehouse: '',
  to_warehouse: 'Kho chính',
  lines: [{ item: '', qty: 1 }],
})
const leaves = computed(() => warehouses.value.filter((w) => !w.is_group))
const shownBins = computed(() => (selected.value ? bins.value.filter((b) => b.warehouse === selected.value) : bins.value))
function descendants(name, acc = []) {
  warehouses.value
    .filter((w) => (w.parent_warehouse || '') === name)
    .forEach((w) => {
      acc.push(w.name)
      descendants(w.name, acc)
    })
  return acc
}
const parentChoices = computed(() => {
  const banned = new Set([wh.old_name, ...(wh.old_name ? descendants(wh.old_name) : [])])
  return warehouses.value.filter((w) => !banned.has(w.name))
})
const flatTree = computed(() => {
  const out = []
  const walk = (parent, depth) => {
    warehouses.value
      .filter((w) => (w.parent_warehouse || '') === parent)
      .forEach((w) => {
        out.push({ ...w, depth })
        walk(w.name, depth + 1)
      })
  }
  walk('', 0)
  return out
})
function err(e) {
  let msg = e?.messages?.[0] || e?.exc || e?.message || ''
  if (!msg && e?._server_messages) {
    try {
      const raw = JSON.parse(e._server_messages)
      msg = JSON.parse(raw[0]).message || ''
    } catch {
      msg = String(e._server_messages)
    }
  }
  msg = String(msg || e || '').replace(/<[^>]+>/g, '')
  if (!msg || msg === 'Internal Server Error') msg = 'Lỗi máy chủ. Thử lại hoặc xem log.'
  return msg
}
function fail(e) {
  error.value = true
  status.value = err(e)
  window.alert(status.value)
}
function openWh(row) {
  Object.assign(wh, {
    open: true,
    old_name: row?.name || '',
    warehouse_name: row?.warehouse_name || '',
    parent: row?.parent_warehouse || '',
    is_group: !!row?.is_group,
  })
}
async function load() {
  warehouses.value = await call('frappe.client.get_list', {
    doctype: 'Warehouse',
    fields: ['name', 'warehouse_name', 'parent_warehouse', 'is_group'],
    limit_page_length: 1000,
    order_by: 'lft asc',
  })
  products.value = await call('frappe.client.get_list', {
    doctype: 'CRM Product',
    fields: ['name', 'product_code', 'product_name', 'custom_is_combo'],
    limit_page_length: 1000,
  })
  const stock = await call('pushesale.stock.balances')
  bins.value = stock?.bins || []
  entries.value = await call('pushesale.stock.recent_entries')
  error.value = false
  status.value = `${warehouses.value.length} kho`
}
async function saveWh() {
  try {
    await call('pushesale.stock.save_warehouse', {
      old_name: wh.old_name,
      warehouse_name: wh.warehouse_name,
      parent: wh.parent,
      is_group: wh.is_group ? 1 : 0,
    })
    wh.open = false
    await load()
  } catch (e) {
    fail(e)
  }
}
async function removeWh(row) {
  if (!window.confirm(`Xóa kho ${row.warehouse_name}?`)) return
  try {
    await call('pushesale.stock.delete_warehouse', { name: row.name })
    await load()
  } catch (e) {
    fail(e)
  }
}
async function submit() {
  try {
    await call('pushesale.stock.submit_entry', {
      entry_type: entry.entry_type,
      from_warehouse: entry.from_warehouse,
      to_warehouse: entry.to_warehouse,
      lines: JSON.stringify(entry.lines),
    })
    entry.lines = [{ item: '', qty: 1 }]
    await load()
    status.value = 'Đã ghi sổ.'
  } catch (e) {
    fail(e)
  }
}
async function cancel(name) {
  if (!window.confirm(`Hủy phiếu ${name}?`)) return
  try {
    await call('pushesale.stock.cancel_entry', { name })
    await load()
  } catch (e) {
    fail(e)
  }
}
onMounted(() => load().catch(fail))
</script>

<style scoped>
.input { width: 100%; border: 1px solid #ddd; border-radius: 8px; padding: 8px; }
.check { display: flex; align-items: center; gap: 8px; }
.btn { border: 0; border-radius: 8px; padding: 8px 12px; background: #e5e7eb; cursor: pointer; }
.btn.primary { background: #1f6feb; color: #fff; }
.row { display: flex; align-items: center; gap: 4px; }
.mini { border: 0; background: transparent; color: #1f6feb; cursor: pointer; font-size: 12px; }
.tree-btn { flex: 1; text-align: left; border: 0; background: transparent; padding: 6px 8px; border-radius: 6px; cursor: pointer; }
.tree-btn.on { background: #e8f0fe; font-weight: 600; }
</style>
