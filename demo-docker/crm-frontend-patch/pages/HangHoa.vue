<template>
  <div class="flex h-full min-h-0 flex-col bg-surface-base">
    <div class="flex items-center justify-between border-b px-4 py-3">
      <div>
        <h1 class="text-xl font-semibold text-ink-gray-9">Hàng hóa</h1>
        <p class="text-sm" :class="error ? 'font-medium text-red-600' : 'text-ink-gray-6'">{{ status }}</p>
      </div>
      <div class="flex gap-2">
        <button class="btn" @click="downloadTemplate()">Tải mẫu Excel</button>
        <button class="btn" @click="pickImport()">Import Excel</button>
        <input ref="fileInput" type="file" accept=".xlsx" class="hidden" @change="onImportFile" />
        <button class="btn" @click="openNewCategory()">Thêm danh mục</button>
        <button class="btn primary" @click="openNewProduct()">Thêm sản phẩm</button>
      </div>
    </div>

    <div v-if="catForm.open" class="grid gap-2 border-b p-4 md:grid-cols-4">
      <input v-model="catForm.category_name" class="input" placeholder="Tên danh mục" />
      <select v-model="catForm.parent" class="input">
        <option value="">Không có cha</option>
        <option v-for="c in parentChoices" :key="c.name" :value="c.name">{{ c.category_name }}</option>
      </select>
      <label class="check"><input v-model="catForm.is_group" type="checkbox" /> Là nhóm</label>
      <div class="flex gap-2">
        <button class="btn primary" @click="saveCategory">Lưu danh mục</button>
        <button class="btn" @click="catForm.open = false">Đóng</button>
      </div>
    </div>

    <div v-if="prodForm.open" class="grid gap-2 border-b p-4 md:grid-cols-3">
      <input v-model="prodForm.product_code" class="input" placeholder="Mã SKU" />
      <input v-model="prodForm.product_name" class="input" placeholder="Tên sản phẩm" />
      <select v-model="prodForm.custom_category" class="input">
        <option value="">Chọn danh mục</option>
        <option v-for="c in categories" :key="c.name" :value="c.name">{{ c.category_name }}</option>
      </select>
      <input v-model="prodForm.custom_uom" class="input" placeholder="Đơn vị" />
      <input v-model="prodForm.custom_weight_kg" class="input" placeholder="Kg" />
      <input v-model="prodForm.standard_rate" class="input" placeholder="Giá bán" />
      <input v-model="prodForm.custom_length_cm" class="input" placeholder="Dài cm" />
      <input v-model="prodForm.custom_width_cm" class="input" placeholder="Rộng cm" />
      <input v-model="prodForm.custom_height_cm" class="input" placeholder="Cao cm" />
      <input v-model="prodForm.custom_short_description" class="input md:col-span-2" placeholder="Mô tả ngắn" />
      <label class="check"><input v-model="prodForm.custom_is_combo" type="checkbox" /> Là combo (giá set riêng)</label>
      <div v-if="prodForm.custom_is_combo" class="md:col-span-3">
        <p class="hint">Tổng giá lẻ: {{ retailTotal }} — giá combo không tự cộng.</p>
        <div v-for="(line, i) in prodForm.lines" :key="i" class="mb-2 grid grid-cols-3 gap-2">
          <select v-model="line.item" class="input">
            <option value="">Chọn SP lẻ</option>
            <option v-for="p in singles" :key="p.name" :value="p.name">{{ p.product_code }} — {{ p.product_name }}</option>
          </select>
          <input v-model="line.qty" class="input" placeholder="Số lượng" />
          <button class="btn" @click="prodForm.lines.splice(i, 1)">Bỏ dòng</button>
        </div>
        <button class="btn" @click="prodForm.lines.push({ item: '', qty: 1 })">Thêm SP vào combo</button>
      </div>
      <div class="flex gap-2 md:col-span-3">
        <button class="btn primary" @click="saveProduct">Lưu sản phẩm</button>
        <button v-if="prodForm.old_code" class="btn danger" @click="removeProduct(0)">Xóa</button>
        <button class="btn" @click="prodForm.open = false">Đóng</button>
      </div>
    </div>

    <div class="flex min-h-0 flex-1">
      <aside class="w-72 overflow-auto border-r p-3">
        <button class="tree-btn" :class="{ on: !selected }" @click="selected = ''">Tất cả</button>
        <div v-for="node in flatTree" :key="node.name" class="row" :style="{ paddingLeft: node.depth * 12 + 'px' }">
          <button class="tree-btn" :class="{ on: selected === node.name }" @click="selected = node.name">{{ node.category_name }}</button>
          <button class="mini" @click.stop="editCategory(node)">Sửa</button>
          <button class="mini" @click.stop="removeCategory(node)">Xóa</button>
        </div>
      </aside>
      <div class="flex-1 overflow-auto p-3">
        <div class="mb-2 flex gap-2 text-sm">
          <button class="btn" :class="{ primary: kind === 'all' }" @click="kind = 'all'">Tất cả</button>
          <button class="btn" :class="{ primary: kind === 'single' }" @click="kind = 'single'">Lẻ</button>
          <button class="btn" :class="{ primary: kind === 'combo' }" @click="kind = 'combo'">Combo</button>
        </div>
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-ink-gray-6">
              <th class="py-2">Mã</th>
              <th>Tên</th>
              <th>Loại</th>
              <th>Danh mục</th>
              <th>ĐVT</th>
              <th>Kg</th>
              <th>Giá</th>
              <th>Tồn</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in shown" :key="row.name" class="cursor-pointer border-t hover:bg-gray-50" @click="editProduct(row)">
              <td class="py-2">{{ row.product_code }}</td>
              <td>{{ row.product_name }}</td>
              <td>{{ row.custom_is_combo ? 'Combo' : 'Lẻ' }}</td>
              <td>{{ row.custom_category }}</td>
              <td>{{ row.custom_uom }}</td>
              <td>{{ row.custom_weight_kg }}</td>
              <td>{{ row.standard_rate }}</td>
              <td>{{ stockLabel(row) }}</td>
            </tr>
            <tr v-if="!shown.length">
              <td colspan="8" class="py-6 text-ink-gray-5">Chưa có sản phẩm trong nhóm này.</td>
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
const fileInput = ref(null)
const error = ref(false)
const totals = ref({})
const comboAvailable = ref({})
const categories = ref([])
const products = ref([])
const selected = ref('')
const kind = ref('all')
const catForm = reactive({ open: false, old_name: '', category_name: '', parent: '', is_group: false })
const prodForm = reactive({
  open: false,
  old_code: '',
  product_code: '',
  product_name: '',
  custom_category: '',
  custom_uom: 'cái',
  custom_weight_kg: '0.1',
  custom_length_cm: '',
  custom_width_cm: '',
  custom_height_cm: '',
  standard_rate: '',
  custom_short_description: '',
  custom_is_combo: false,
  lines: [],
})

function descendants(name, acc = []) {
  categories.value
    .filter((c) => c.parent_product_category === name)
    .forEach((c) => {
      acc.push(c.name)
      descendants(c.name, acc)
    })
  return acc
}
const parentChoices = computed(() => {
  const banned = new Set([catForm.old_name, ...descendants(catForm.old_name)])
  return categories.value.filter((c) => c.name && !banned.has(c.name))
})
const flatTree = computed(() => {
  const out = []
  const walk = (parent, depth) => {
    categories.value
      .filter((c) => (c.parent_product_category || '') === parent)
      .forEach((c) => {
        out.push({ ...c, depth })
        walk(c.name, depth + 1)
      })
  }
  walk('', 0)
  return out
})
const singles = computed(() => products.value.filter((p) => !p.custom_is_combo && p.name !== prodForm.old_code))
const selectedNames = computed(() => {
  if (!selected.value) return null
  return [selected.value, ...descendants(selected.value)]
})
const shown = computed(() => {
  let rows = products.value
  if (selectedNames.value) rows = rows.filter((p) => selectedNames.value.includes(p.custom_category))
  if (kind.value === 'combo') rows = rows.filter((p) => p.custom_is_combo)
  if (kind.value === 'single') rows = rows.filter((p) => !p.custom_is_combo)
  return rows
})
const retailTotal = computed(() =>
  prodForm.lines.reduce((sum, line) => {
    const item = products.value.find((p) => p.name === line.item)
    return sum + Number(item?.standard_rate || 0) * Number(line.qty || 0)
  }, 0),
)

function stockLabel(row) {
  if (row.custom_is_combo) return comboAvailable.value[row.name] ?? 0
  return totals.value[row.name] ?? 0
}
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
function fail(prefix, e) {
  const msg = prefix + err(e)
  error.value = true
  status.value = msg
  window.alert(msg)
}
function emptyProduct() {
  Object.assign(prodForm, {
    open: true,
    old_code: '',
    product_code: '',
    product_name: '',
    custom_category: selected.value || '',
    custom_uom: 'cái',
    custom_weight_kg: '0.1',
    custom_length_cm: '',
    custom_width_cm: '',
    custom_height_cm: '',
    standard_rate: '',
    custom_short_description: '',
    custom_is_combo: false,
    lines: [{ item: '', qty: 1 }],
  })
}
function pickImport() {
  fileInput.value?.click()
}
async function downloadTemplate() {
  try {
    const res = await call('pushesale.catalog.download_product_template')
    const bin = atob(res.filedata)
    const bytes = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i += 1) bytes[i] = bin.charCodeAt(i)
    const blob = new Blob([bytes], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = res.filename || 'mau-hang-hoa.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    fail('Không tải mẫu: ', e)
  }
}
function onImportFile(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  const reader = new FileReader()
  reader.onload = async () => {
    const text = String(reader.result || '')
    const filedata = text.includes(',') ? text.split(',')[1] : text
    try {
      const res = await call('pushesale.catalog.import_products', { filedata })
      await load()
      const errs = (res.errors || []).map((x) => `dòng ${x.row}: ${x.message}`).join('; ')
      status.value = `Import: ${res.created} tạo, ${res.updated} cập nhật, ${res.skipped} bỏ${errs ? '. ' + errs : ''}`
      error.value = !!res.skipped
      window.alert(status.value)
    } catch (e) {
      fail('Import lỗi: ', e)
    }
  }
  reader.readAsDataURL(file)
}
function openNewCategory() {
  Object.assign(catForm, { open: true, old_name: '', category_name: '', parent: '', is_group: false })
}
function openNewProduct() {
  emptyProduct()
}
function editCategory(node) {
  Object.assign(catForm, {
    open: true,
    old_name: node.name,
    category_name: node.category_name,
    parent: node.parent_product_category || '',
    is_group: !!node.is_group,
  })
}
async function editProduct(row) {
  let lines = []
  if (row.custom_is_combo) {
    lines = await call('pushesale.catalog.get_combo_lines', { combo: row.name })
  }
  Object.assign(prodForm, {
    open: true,
    old_code: row.name,
    product_code: row.product_code,
    product_name: row.product_name,
    custom_category: row.custom_category || '',
    custom_uom: row.custom_uom || '',
    custom_weight_kg: row.custom_weight_kg ?? '',
    custom_length_cm: row.custom_length_cm ?? '',
    custom_width_cm: row.custom_width_cm ?? '',
    custom_height_cm: row.custom_height_cm ?? '',
    standard_rate: row.standard_rate ?? '',
    custom_short_description: row.custom_short_description || '',
    custom_is_combo: !!row.custom_is_combo,
    lines: lines.length ? lines.map((l) => ({ item: l.item, qty: l.qty })) : [{ item: '', qty: 1 }],
  })
}
async function load() {
  categories.value = await call('frappe.client.get_list', {
    doctype: 'Product Category',
    fields: ['name', 'category_name', 'parent_product_category', 'is_group'],
    limit_page_length: 1000,
    order_by: 'lft asc',
  })
  products.value = await call('frappe.client.get_list', {
    doctype: 'CRM Product',
    fields: [
      'name', 'product_code', 'product_name', 'custom_category', 'custom_uom',
      'custom_weight_kg', 'custom_length_cm', 'custom_width_cm', 'custom_height_cm',
      'standard_rate', 'custom_short_description', 'custom_is_combo',
    ],
    limit_page_length: 1000,
    order_by: 'modified desc',
  })
  const stock = await call('pushesale.stock.balances')
  totals.value = stock?.totals || {}
  comboAvailable.value = stock?.combo_available || {}
  error.value = false
  status.value = `${categories.value.length} danh mục, ${products.value.length} sản phẩm`
}
async function saveCategory() {
  try {
    await call('pushesale.catalog.save_category', {
      old_name: catForm.old_name,
      category_name: catForm.category_name,
      parent: catForm.parent,
      is_group: catForm.is_group ? 1 : 0,
    })
    catForm.open = false
    await load()
    status.value = 'Đã lưu danh mục.'
  } catch (e) {
    fail('Lỗi danh mục: ', e)
  }
}
async function removeCategory(node) {
  if (!window.confirm(`Xóa danh mục ${node.category_name}?`)) return
  try {
    await call('pushesale.catalog.delete_category', { name: node.name })
    if (selected.value === node.name) selected.value = ''
    await load()
    status.value = 'Đã xóa danh mục.'
  } catch (e) {
    fail('Lỗi xóa danh mục: ', e)
  }
}
async function saveProduct() {
  try {
    await call('pushesale.catalog.save_product', {
      old_code: prodForm.old_code,
      product_code: prodForm.product_code,
      product_name: prodForm.product_name,
      custom_category: prodForm.custom_category,
      custom_uom: prodForm.custom_uom,
      custom_weight_kg: prodForm.custom_weight_kg,
      custom_length_cm: prodForm.custom_length_cm,
      custom_width_cm: prodForm.custom_width_cm,
      custom_height_cm: prodForm.custom_height_cm,
      standard_rate: prodForm.standard_rate,
      custom_short_description: prodForm.custom_short_description,
      custom_is_combo: prodForm.custom_is_combo ? 1 : 0,
      lines: JSON.stringify(prodForm.lines),
    })
    prodForm.open = false
    await load()
    status.value = 'Đã lưu sản phẩm.'
  } catch (e) {
    fail('Lỗi sản phẩm: ', e)
  }
}
async function removeProduct(detach = 0, confirmCombo = 0) {
  if (!detach && !confirmCombo && !window.confirm(`Xóa ${prodForm.product_code}?`)) return
  try {
    await call('pushesale.catalog.delete_product', {
      name: prodForm.old_code,
      detach_combo: detach,
      confirm_combo: confirmCombo,
    })
    prodForm.open = false
    await load()
    status.value = 'Đã xóa sản phẩm.'
    error.value = false
  } catch (e) {
    const msg = err(e)
    if (!detach && msg.includes('Đang trong combo')) {
      if (window.confirm(msg + '\nBấm OK để gỡ khỏi combo rồi xóa.')) return removeProduct(1, confirmCombo)
    }
    if (!confirmCombo && msg.includes('Combo này chứa')) {
      if (window.confirm(msg + '\nBấm OK để xóa combo.')) return removeProduct(detach, 1)
    }
    fail('', e)
  }
}
onMounted(() => {
  load().catch((e) => {
    status.value = 'Không tải được hàng hóa: ' + err(e)
  })
})
</script>

<style scoped>
.input { width: 100%; border: 1px solid #ddd; border-radius: 8px; padding: 8px; }
.check { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.btn { border: 0; border-radius: 8px; padding: 8px 12px; background: #e5e7eb; cursor: pointer; }
.btn.primary { background: #1f6feb; color: #fff; }
.btn.danger { background: #fee2e2; }
.hint { margin-bottom: 8px; font-size: 12px; color: #666; }
.row { display: flex; align-items: center; gap: 4px; }
.row.child { padding-left: 12px; }
.mini { border: 0; background: transparent; color: #1f6feb; cursor: pointer; font-size: 12px; }
.tree-btn { flex: 1; text-align: left; border: 0; background: transparent; padding: 6px 8px; border-radius: 6px; cursor: pointer; }
.tree-btn.on { background: #e8f0fe; font-weight: 600; }
</style>
