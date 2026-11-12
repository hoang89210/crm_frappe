PATH = "/home/frappe/frappe-bench/apps/crm/frontend/src/pages/Lead.vue"
src = open(PATH, encoding="utf-8").read()
if "openChat" in src:
    print("button already present")
else:
    old_fn = """  } finally {
    simCalling.value = false
  }
}"""
    new_fn = """  } finally {
    simCalling.value = false
  }
}

async function openChat() {
  try {
    const res = await call('pushesale.api.chatwoot.open_conversation', {
      lead: props.leadId,
    })
    if (!res?.url) {
      toast.error(__('Chưa kết nối Chatwoot'))
      return
    }
    window.open(res.url, '_blank', 'noopener')
  } catch (e) {
    toast.error(e.messages?.[0] || __('Chưa kết nối Chatwoot'))
  }
}"""
    if src.count(old_fn) != 1:
        raise SystemExit(f"fn anchor {src.count(old_fn)}")
    src = src.replace(old_fn, new_fn, 1)
    old_btn = """                  @click="() => simCall()"
                />"""
    new_btn = """                  @click="() => simCall()"
                />
                <Button
                  v-if="isAdmin() || isManager() || isSalesUser()"
                  :tooltip="__('Mở hội thoại Chatwoot')"
                  :label="__('Chat')"
                  @click="() => openChat()"
                />"""
    if src.count(old_btn) != 1:
        raise SystemExit(f"btn anchor {src.count(old_btn)}")
    src = src.replace(old_btn, new_btn, 1)
    open(PATH, "w", encoding="utf-8").write(src)
    print("lead patched")
