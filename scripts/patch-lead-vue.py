#!/usr/bin/env python3
"""Surgical SIM-call button for CRM Lead.vue (pushesale Phase 4A).

Inserts:
1. usersStore import
2. simCall logic after `const doc = computed(...)`
3. "Goi SIM" button after the native Call button
Keeps a backup at /tmp/Lead.vue.bak. Fails loudly if anchors change.
"""

PATH = "/home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue"

ANCHOR_IMPORT = "import { callEnabled } from '@/composables/telephony'"
ADD_IMPORT = "import { usersStore } from '@/stores/users'"

ANCHOR_DOC = "const doc = computed(() => document.doc || {})"
ADD_LOGIC = """const doc = computed(() => document.doc || {})

const { isAdmin, isManager, isSalesUser } = usersStore()
const simCalling = ref(false)

// Pushsale SIM call: push a Call Job to the sale's Android device/PWA.
// Backend (pushesale.api.call.create_job) enforces Sales-only roles.
async function simCall() {
  if (!doc.value.mobile_no) {
    toast.error(__('Vui lòng nhập số điện thoại trước khi gọi'))
    return
  }
  if (simCalling.value) return
  simCalling.value = true
  try {
    const res = await call('pushesale.api.call.create_job', {
      lead: props.leadId,
    })
    toast.success(__('Đã gửi lệnh gọi tới máy của bạn ({phone})', { phone: res.phone }))
  } catch (e) {
    toast.error(e.messages?.[0] || __('Không tạo được lệnh gọi'))
  } finally {
    simCalling.value = false
  }
}"""

ANCHOR_BUTTON = """                <Button
                  v-if="callEnabled"
                  :tooltip="__('Make a Call')"
                  :icon="PhoneIcon"
                  @click="
                    () =>
                      doc.mobile_no
                        ? makeCall(doc.mobile_no)
                        : toast.error(
                            __('Please set a mobile number to make calls'),
                          )
                  "
                />"""
ADD_BUTTON = ANCHOR_BUTTON + """
                <Button
                  v-if="doc.mobile_no && (isAdmin() || isManager() || isSalesUser())"
                  :tooltip="__('Gọi bằng SIM')"
                  :icon="PhoneIcon"
                  :label="__('Gọi SIM')"
                  :loading="simCalling"
                  @click="() => simCall()"
                />"""


def main():
    with open(PATH, encoding="utf-8") as f:
        src = f.read()
    with open("/tmp/Lead.vue.bak", "w", encoding="utf-8") as f:
        f.write(src)

    for name, anchor in (
        ("import", ANCHOR_IMPORT),
        ("doc", ANCHOR_DOC),
        ("button", ANCHOR_BUTTON),
    ):
        if src.count(anchor) != 1:
            raise SystemExit(f"anchor {name!r} found {src.count(anchor)}x, aborting")

    if "usersStore } from '@/stores/users'" in src:
        print("usersStore import already present, skipping import insert")
    else:
        src = src.replace(ANCHOR_IMPORT, ANCHOR_IMPORT + "\n" + ADD_IMPORT)
    if "async function simCall()" in src:
        print("simCall already present, skipping logic insert")
    else:
        src = src.replace(ANCHOR_DOC, ADD_LOGIC)
    if "Gọi bằng SIM" in src:
        print("SIM button already present, skipping button insert")
    else:
        src = src.replace(ANCHOR_BUTTON, ADD_BUTTON)

    with open(PATH, "w", encoding="utf-8") as f:
        f.write(src)
    print("Lead.vue patched OK")


if __name__ == "__main__":
    main()
