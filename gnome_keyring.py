from gi.repository import GnomeKeyring

password_type = GnomeKeyring.ItemType.GENERIC_SECRET

def set(description, secret, attributes={}):
	attributes = build_attributes(attributes)
	result, id = GnomeKeyring.item_create_sync(None, password_type, description, attributes, secret, True)

	return result == GnomeKeyring.Result.OK

def get(attributes):
	attributes = build_attributes(attributes)
	result, values = GnomeKeyring.find_items_sync(password_type, attributes)

	if result == GnomeKeyring.Result.OK:
		return values[0].secret
	else:
		return None

def build_attributes(attributes):
	attrs = GnomeKeyring.Attribute.list_new()
	for key in attributes:
		GnomeKeyring.Attribute.list_append_string(attrs, key, attributes[key])
	return attrs
