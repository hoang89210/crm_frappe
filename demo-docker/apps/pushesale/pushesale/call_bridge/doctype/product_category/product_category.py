from frappe.utils.nestedset import NestedSet


class ProductCategory(NestedSet):
	nsm_parent_field = "parent_product_category"
