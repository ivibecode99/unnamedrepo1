class_name ItemData
extends RefCounted
## Shop inventory and cosmetics. Each kingdom's shop takes that kingdom's coins.
const OUTFITS := {
	"leaf": {"name": "Leaf Tunic", "color": Color(0.3, 0.75, 0.3), "kingdom": "forest"},
	"sand": {"name": "Desert Robe", "color": Color(0.95, 0.78, 0.4), "kingdom": "desert"},
	"gear": {"name": "Tinker Overalls", "color": Color(0.8, 0.5, 0.15), "kingdom": "city"},
	"wave": {"name": "Wavy Wetsuit", "color": Color(0.2, 0.75, 0.85), "kingdom": "ocean"},
	"frost": {"name": "Frost Parka", "color": Color(0.85, 0.93, 1.0), "kingdom": "snow"},
	"flame": {"name": "Flame Cape", "color": Color(1.0, 0.4, 0.15), "kingdom": "volcano"},
}
const HAT_SKINS := {
	"classic": {"name": "Classic Capt", "color": Color(0.85, 0.2, 0.35)},
	"forest": {"name": "Forest Capt", "color": Color(0.3, 0.7, 0.3)},
	"desert": {"name": "Sandy Capt", "color": Color(0.95, 0.7, 0.25)},
	"city": {"name": "Chrome Capt", "color": Color(0.7, 0.75, 0.85)},
	"ocean": {"name": "Coral Capt", "color": Color(1.0, 0.5, 0.55)},
	"snow": {"name": "Frosty Capt", "color": Color(0.7, 0.9, 1.0)},
	"volcano": {"name": "Magma Capt", "color": Color(1.0, 0.45, 0.1)},
}

static func outfit_color(id: String):
	if OUTFITS.has(id):
		return OUTFITS[id]["color"]
	return null

static func hat_color(id: String) -> Color:
	if HAT_SKINS.has(id):
		return HAT_SKINS[id]["color"]
	return HAT_SKINS["classic"]["color"]

static func shop_items(kingdom: String) -> Array:
	if not Kingdoms.DATA.has(kingdom):
		return []
	var kd: Dictionary = Kingdoms.DATA[kingdom]
	var items: Array = []
	if kd.has("shop_price"):
		items.append({"id": "star_" + kingdom, "name": "A Shiny Star", "desc": "Yes, they sell Stars here. Don't ask.", "price": int(kd["shop_price"]), "kind": "star", "value": kingdom + "_shop"})
	items.append({"id": "heal_" + kingdom, "name": "Snack", "desc": "Restores all health.", "price": 8, "kind": "heal", "value": ""})
	if kingdom in ["forest", "desert", "city"]:
		items.append({"id": "heart_" + kingdom, "name": "Heart Snack", "desc": "+1 max health. Permanent.", "price": 25, "kind": "heart", "value": ""})
	items.append({"id": "outfit_" + kingdom, "name": OUTFITS.get(_outfit_id(kingdom), {"name": "Outfit"})["name"], "desc": "Cosmetic outfit for Pip.", "price": 20, "kind": "outfit", "value": _outfit_id(kingdom)})
	items.append({"id": "hat_" + kingdom, "name": HAT_SKINS[kingdom]["name"], "desc": "Cosmetic skin for Capt.", "price": 15, "kind": "hat", "value": kingdom})
	return items

static func _outfit_id(kingdom: String) -> String:
	for k in OUTFITS:
		if OUTFITS[k]["kingdom"] == kingdom:
			return k
	return "leaf"
