class_name BossData
extends RefCounted
## Boss definitions. phases[] each have hp and attack list. attacks: charge slam rain ring spin summon beam
const DATA := {
	"mogul": {"name": "Mossback Mogul", "kingdom": "forest", "color": Color(0.35, 0.5, 0.25), "color2": Color(0.5, 0.35, 0.2), "scale": 2.4, "shape": "tree",
		"intro": "A walking tree in a tiny crown. He is VERY fond of naps.",
		"phases": [{"hp": 3, "attacks": ["charge", "slam"], "speed": 1.0}, {"hp": 3, "attacks": ["slam", "rain", "summon"], "speed": 1.1}, {"hp": 3, "attacks": ["charge", "rain", "ring"], "speed": 1.3}]},
	"scarabella": {"name": "Madame Scarabella", "kingdom": "desert", "color": Color(0.15, 0.5, 0.65), "color2": Color(1.0, 0.8, 0.2), "scale": 2.2, "shape": "beetle",
		"intro": "Queen of the scarabs. Her hair has its own weather.",
		"phases": [{"hp": 3, "attacks": ["charge", "ring"], "speed": 1.0}, {"hp": 3, "attacks": ["summon", "spin"], "speed": 1.15}, {"hp": 3, "attacks": ["spin", "rain", "charge"], "speed": 1.3}]},
	"gus": {"name": "Gearhead Gus", "kingdom": "city", "color": Color(0.7, 0.72, 0.8), "color2": Color(1.0, 0.7, 0.15), "scale": 2.6, "shape": "mech",
		"intro": "A mech built from every spare part in Tinkertown. It squeaks.",
		"phases": [{"hp": 3, "attacks": ["rain", "slam"], "speed": 1.0}, {"hp": 3, "attacks": ["beam", "summon"], "speed": 1.15}, {"hp": 3, "attacks": ["ring", "beam", "charge"], "speed": 1.3}]},
	"brinebeard": {"name": "Captain Brinebeard", "kingdom": "ocean", "color": Color(0.7, 0.25, 0.55), "color2": Color(1.0, 0.8, 0.8), "scale": 2.4, "shape": "octo",
		"intro": "An octopus with a captain's hat, a parrot, and zero chill.",
		"phases": [{"hp": 3, "attacks": ["spin", "rain"], "speed": 1.0}, {"hp": 3, "attacks": ["slam", "summon", "spin"], "speed": 1.15}, {"hp": 3, "attacks": ["ring", "spin", "rain"], "speed": 1.35}]},
	"frank": {"name": "Frostbite Frank", "kingdom": "snow", "color": Color(0.9, 0.95, 1.0), "color2": Color(0.4, 0.7, 0.95), "scale": 2.7, "shape": "yeti",
		"intro": "A giant robot yeti. He is cold. He wants YOU to be cold too.",
		"phases": [{"hp": 3, "attacks": ["charge", "rain"], "speed": 1.0}, {"hp": 3, "attacks": ["slam", "ring"], "speed": 1.2}, {"hp": 3, "attacks": ["rain", "ring", "charge", "slam"], "speed": 1.35}]},
	"baron": {"name": "Baron Von Grumblebelt", "kingdom": "final", "color": Color(0.35, 0.25, 0.5), "color2": Color(1.0, 0.8, 0.3), "scale": 2.8, "shape": "baron",
		"intro": "He's tall. He's grumpy. He has a giant music box and he is NOT afraid to wind it.",
		"phases": [{"hp": 3, "attacks": ["rain", "charge"], "speed": 1.0}, {"hp": 3, "attacks": ["summon", "beam", "slam"], "speed": 1.15}, {"hp": 3, "attacks": ["ring", "spin", "rain"], "speed": 1.3}, {"hp": 3, "attacks": ["beam", "ring", "charge", "slam", "rain"], "speed": 1.5}]},
}
