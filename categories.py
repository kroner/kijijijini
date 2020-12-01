import itertools

	#('buy-sell', 10),
categories = {
	#('clothing', 274),
'clothing' : [
	('clothing-men', 278),
	('mens-shoes', 15117001),
	('women-shoes', 286),
	('women-tops-outerwear', 284),
	('women-bags-wallets', 281),
	('clothing-kid-youth', 279),
	('women-dresses-skirts', 283),
	('women-other-clothing', 287),
	('women-pants-shorts', 285),
	('other-clothing', 275),
	('clothing-costumes', 277),
	('wedding-dresses-suits', 280),
	#('clothing-lot', 276),
	('women-maternity', 282),
	],

'art-collectables' : [
	('art-collectables', 12),
	],

	#('furniture', 235),
'furniture' : [
	('chair-recliner', 245),
	('bed-mattress', 246),
	('couch-futon', 238),
	('dining-table-set', 243),
	('coffee-table-ottoman', 241),
	('hutch-display-cabinet', 250),
	('dresser-wardrobe', 247),
	('furniture-other-table', 244),
	('bookcase-shelves', 249),
	('other-furniture', 236),
	('buy-sell-desks', 239),
	('tv-table-entertainment-unit', 242),
	#('furniture-lot', 237),
	],

	#('home-indoor', 717),
'home-indoor' : [
	('indoor-decor-accent', 720),
	('kitchen-dining', 722),
	('indoor-lighting-fan', 721),
	('rug-carpet-runner', 723),
	('home-indoor-other', 725),
	('storage-organization', 15058003),
	('bathware-bathroom', 718),
	('bedding', 719),
	('window-treatment', 724),
	('holiday-event-seasonal', 15058002),
	('fireplace-firewood', 15058001),
	],

	#('books', 109),
'books' : [
	('textbooks', 14970001),
	('comics-graphic-novels', 14970004),
	('non-fiction', 14970006),
	('children-young-adult', 14970003),
	('other', 14970007),
	('fiction', 14970005),
	('magazines', 14970002),
	],

'buy-sell-other' : [
	('buy-sell-other', 26),
	],

'toys-games' : [
	('toys-games', 108),
	],

	#('baby-items', 253),
'baby-items' : [
	('baby-stroller-carrier-car-seat', 270),
	('baby-feeding-high-chair', 271),
	('baby-toy', 256),
	('other-baby-items', 254),
	('baby-playpen-swing-saucer', 268),
	('baby-crib-bassinet', 269),
	('baby-bathing-changing-diapers', 272),
	('baby-safety-gate-monitor', 273),
	('baby-clothes-12-18-months', 262),
	('baby-lot', 255),
	('baby-clothes-2t', 264),
	('baby-clothes-18-24-months', 263),
	('baby-clothes-3t', 265),
	('baby-clothes-0-3-months', 258),
	('baby-clothes-3-6-months', 259),
	('baby-clothes-4t', 266),
	('baby-clothes-6-9-months', 260),
	('baby-clothes-9-12-months', 261),
	('baby-clothes-5t', 267),
	('baby-clothes-preemie', 257),
	],

	#('sporting-goods-exercise', 111),
'sporting-goods-exercise' : [
	('exercise-equipment', 655),
	('hockey', 659),
	('golf', 658),
	('sport-other', 669),
	('fishing-camping-outdoor', 656),
	('skates-blades', 662),
	('soccer', 666),
	('water-sport', 668),
	('ski', 664),
	('tennis-and-racket', 667),
	('baseball-softball', 652),
	('snowboard', 665),
	('basketball', 653),
	('skateboard', 663),
	('football', 657),
	('paintball', 661),
	('lacrosse', 660),
	('curling', 654),
	],

	#('value', 29659001),
'value' : [
	('general-electronics', 15),
	('security-systems', 29659002),
	],

	#('computer-accessories', 128),
'computer-accessories' : [
	('computer-components', 788),
	('printers-scanners-fax', 784),
	('computer-networking', 783),
	('mice-keyboards-webcam', 781),
	('laptop-accessories', 780),
	('monitors', 782),
	('networking-cables-and-connectors', 777),
	('other-computer-products', 790),
	('speakers-headsets-mics', 787),
	('ipad-tablet-accessories', 789),
	('flash-memory-usb-sticks', 778),
	 #('service-training-repair', 785),
	('software', 786),
	],

	#('home-appliances', 107),
'home-appliances' : [
	('other-home-appliance', 701),
	('microwave-cooker', 694),
	('coffee-maker-espresso-machine', 689),
	('heater-humidifier-dehumidifier', 692),
	('stove-oven-range', 697),
	('washer-dryer', 700),
	('vacuum', 699),
	('processor-blender-juicer', 695),
	('refrigerator-fridge', 696),
	('toasters-toaster-oven', 698),
	('iron-garment-steamer', 693),
	('appliance-dishwasher', 690),
	('freezer', 691),
	],

	#('phone-tablet', 132),
'phone-tablet' : [
	('cell-phone', 760),
	('cell-phone-accessories', 761),
	##('cell-phone-services', 762),
	('home-phone-answering-machine', 765),
	('phone-tablet-other', 766),
	],

'jewelry-watch' : [
	('jewelry-watch', 133),
	],

	#('video-games-consoles', 141),
'video-games-consoles' : [
	('sony-playstation-4', 792),
	('old-video-games', 623),
	('xbox-one', 793),
	('nintendo-switch', 33035001),
	('sony-playstation-3', 627),
	('xbox-360', 622),
	('video-games-consoles-other', 625),
	('nintendo-ds', 619),
	('nintendo-wii', 626),
	('pc-games', 624),
	('nintendo-wii-u', 14654002),
	('sony-psp', 621),
	],

'health-special-needs' : [
	('health-special-needs', 140)],

	#('bikes', 644),

'bikes' : [
	('kids-bike', 646),
	('road-bike', 644),
	('mountain-bike', 647),
	('bike-frames-parts', 649),
	('bike-clothes-shoes-accessories', 650),
	('cruiser-commuter-hybrid', 15096001),
	('ebike', 14654001),
	('other-bike', 651),
	('bmx-bike', 645),
	('fixie-single-speed', 15096002),
	],

	#('business-industrial', 29659003),
'business-industrial' : [
	('other-business-industrial', 145),
	('industrial-kitchen-supplies', 29659004),
	('storage-containers', 29659006),
	('industrial-shelving-racking', 29659005),
	],

'cd-dvd-blu-ray' : [
	('cd-dvd-blu-ray', 104),
	],

	#('home-renovation', 727),
'home-renovation' : [
	('plumbing-sink-toilet-shower', 734),
	('renovation-window-door-trim', 736),
	('renovation-cabinet-counter', 728),
	('renovation-flooring-wall', 730),
	('renovation-other', 737),
	('renovation-electrical', 729),
	('heating-cooling-air', 732),
	('renovation-hardware-nail-screw', 731),
	('paint-and-painting-supplies', 733),
	('roofing', 735),
	],

'hobbies-crafts' : [
	('hobbies-craft', 139),
	],

	#('home-outdoor', 19),
'home-outdoor' : [
	('gardening-plant-fertilizer-soil', 687),
	('home-outdoor-other', 726),
	('patio-garden-furniture', 19),
	('lawnmower-leaf-blower', 682),
	('outdoor-decor', 683),
	('bbq-outdoor-cooking', 678),
	('outdoor-tools-storage', 685),
	('outdoor-lighting', 684),
	('hot-tub-pool', 681),
	('snowblower', 688),
	('deck-fence', 679),
	('garage-door-opener', 680),
	],

'camera-camcorder-lens' : [
	('camera-camcorder-lens', 103),
	],

	#('audio', 767),
'audio' : [
	('speakers', 14922002),
	('headphones', 770),
	('stereo-systems-home-theatre', 14922001),
	('ipod-mp3-player-other', 771),
	('ipod-mp3-player', 768),
	('ipod-mp3-player-accessories', 769),
	],

	#('computer', 16),
'computer' : [
	('laptops', 773),
	('desktop-computers', 772),
	('ipads-tablets', 776),
	('other', 29324001),
	('servers', 774),
	],

	#('tool', 110),
'tool' : [
	('power-tool', 703),
	('hand-tool', 702),
	('tool-other', 715),
	('tool-storage-bench', 704),
	('ladder-scaffolding', 705),
	],

	#('musical-instrument', 17),

'musical-instrument' : [
	('guitar', 613),
	('amp-pedal', 610),
	('piano-keyboard', 614),
	('pro-audio-recording', 615),
	('drum-percussion', 612),
	('performance-dj-equipment', 14922003),
	('other-musical-instrument', 618),
	('string-instrument', 616),
	('woodwind', 617),
	('brass-instrument-horn', 611),
	],

	#('tvs-video', 15093001),
'tvs-video' : [
	('tvs', 15093002),
	('video-tv-accessories', 15093003),
	],
	}

	##('free-stuff', 17220001),

	##('garage-sale-yard-sale', 638),

item_list = []
for li in categories.values():
	item_list.extend(li)
#categories['buy-sell'] = item_list
item_category = dict()
for cat in categories:
	for item in categories[cat]:
		item_category[item[0]] = cat

item_dict = dict(item_list)
item_dict_reverse = dict([(v,k) for (k,v) in item_list])

def item_code(s):
	return item_dict[s]

def item_name(n):
	return reverse_dict[n]
