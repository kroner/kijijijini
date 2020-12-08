#############################################

ids = dict()
names = dict()
# A class for item types and categories
class Category():
	def __init__(self, name, id, string, parent=None, disabled=False):
		self.name = name
		self.id = id
		self.string = string
		self.parent = parent
		self.disabled = disabled
		if parent is not None:
			parent._children.append(self)
		self._children = []
		ids[id] = self
		names[name] = self

	# return all children or the category itself
	# if disabled is False, ignore categories with disabled flag set to True
	def children(self, disabled=False):
		if self._children:
			return [c for c in self._children if (not c.disabled) or disabled]
		return [self]

	def category(self):
		if self.parent is None or self.parent == buy_sell:
			return self
		return self.parent

	def __repr__(self):
		return f'Category: {self.name} ({self.id})'

# Retreive item by its id
def by_id(id):
	return ids[id]

# Retreive item by its name
def by_name(name):
	return names[name]

# List all non-disabled cateogries
def categories(disabled=False):
	return buy_sell.children(disabled=disabled)

# List all non-disabled items
def items(disabled=False):
	items = []
	for cat in categories(disabled=disabled):
		if cat._children:
			items.extend(cat.children(disabled=disabled))
		else:
			items.append(cat)
	return items


#############################################

disabled_list = ['free-stuff', 'garage-sale-yard-sale', 'clothing-lot', 'furniture-lot', 'baby-lot']

buy_sell = Category('buy-sell', 10, "All")

category_list = [
	('furniture', 235, "Furniture"),
	('clothing', 274, "Clothing"),
	('art-collectibles', 12, "Arts & Collectibles"),
	('home-indoor', 717, "Home - Indoor"),
	('books', 109, "Books"),
	('buy-sell-other', 26, "Other"),
	('toys-games', 108, "Toys & Games"),
	('baby-items', 253, "Baby Items"),
	('sporting-goods-exercise', 111, "Sporting Goods & Exercise"),
	('value', 29659001, "Electronics"),
	('computer-accessories', 128, "Computer Accessories"),
	('home-appliances', 107, "Home Appliances"),
	('phone-tablet', 132, "Phones"),
	('jewelry-watch', 133, "Jewellery & Watches"),
	('video-games-consoles', 141, "Video Games & Consoles"),
	('health-special-needs', 140, "Health & Special Needs"),
	('bikes', 644, "Bikes"),
	('business-industrial', 29659003, "Business & Industrial"),
	('cd-dvd-blu-ray', 104, "CDs, DVDs & Blu-ray"),
	('home-renovation', 727, "Home Renovation Materials"),
	('hobbies-craft', 139, "Hobbies & Crafts"),
	('home-outdoor', 19, "Home - Outdoors & Garden"),
	('camera-camcorder-lens', 103, "Cameras & Camcorders"),
	('audio', 767, "Audio"),
	('computer', 16, "Computers"),
	('tool', 110, "Tools"),
	('musical-instrument', 17, "Musical Instruments"),
	('tvs-video', 15093001, "TVs & Video"),
	('free-stuff', 17220001, "Free Stuff"),
	('garage-sale-yard-sale', 638, "Garage Sales"),
	]


	#('buy-sell', 10, "Buy & Sell"),
category_dict = {
	#('clothing', 274, "Clothing"),
'clothing' : [
	('clothing-men', 278, "Men's"),
	('mens-shoes', 15117001, "Men's - Shoes"),
	('women-shoes', 286, "Women's - Shoes"),
	('women-tops-outerwear', 284, "Women's - Tops & Outerwear"),
	('women-bags-wallets', 281, "Women's - Bags & Wallets"),
	('clothing-kid-youth', 279, "Kids & Youth"),
	('women-dresses-skirts', 283, "Women's - Dresses & Skirts"),
	('women-other-clothing', 287, "Women's - Other"),
	('women-pants-shorts', 285, "Women's - Bottoms"),
	('other-clothing', 275, "Other"),
	('clothing-costumes', 277, "Costumes"),
	('wedding-dresses-suits', 280, "Wedding"),
	('clothing-lot', 276, "Multi-item"),
	('women-maternity', 282, "Women's - Maternity"),
	],

'art-collectibles' : [
	('art-collectibles', 12, "Arts & Collectibles"),
	],

	#('furniture', 235, "Furniture"),
'furniture' : [
	('chair-recliner', 245, "Chairs & Recliners"),
	('bed-mattress', 246, "Bed & Mattresses"),
	('couch-futon', 238, "Couches & Futons"),
	('dining-table-set', 243, "Dining Tables & Sets"),
	('coffee-table-ottoman', 241, "Coffee Tables"),
	('hutch-display-cabinet', 250, "Hutches & Display Cabinets"),
	('dresser-wardrobe', 247, "Dressers & Wardrobes"),
	('furniture-other-table', 244, "Other Tables"),
	('bookcase-shelves', 249, "Bookcases & Shelving Units"),
	('other-furniture', 236, "Other"),
	('buy-sell-desks', 239, "Desks"),
	('tv-table-entertainment-unit', 242, "TV Tables & Entertainment Units"),
	('furniture-lot', 237, "Multi-item"),
	],

	#('home-indoor', 717, "Home - Indoor"),
'home-indoor' : [
	('indoor-decor-accent', 720, "Home Decor & Accents"),
	('kitchen-dining', 722, "Kitchen & Dining Wares"),
	('indoor-lighting-fan', 721, "Indoor Lighting & Fans"),
	('rug-carpet-runner', 723, "Rugs, Carpets & Runners"),
	('home-indoor-other', 725, "Other"),
	('storage-organization', 15058003, "Storage & Organization"),
	('bathware-bathroom', 718, "Bathwares"),
	('bedding', 719, "Bedding"),
	('window-treatment', 724, "Window Treatments"),
	('holiday-event-seasonal', 15058002, "Holiday, Event & Seasonal"),
	('fireplace-firewood', 15058001, "Fireplace & Firewood"),
	],

	#('books', 109, "Books"),
'books' : [
	('textbooks', 14970001, "Textbooks"),
	('comics-graphic-novels', 14970004, "Comics & Graphic Novels"),
	('non-fiction', 14970006, "Non-fiction"),
	('children-young-adult', 14970003, "Children & Young Adult"),
	('other', 14970007, "Other"),
	('fiction', 14970005, "Fiction"),
	('magazines', 14970002, "Magazines"),
	],

'buy-sell-other' : [
	('buy-sell-other', 26, "Other"),
	],

'toys-games' : [
	('toys-games', 108, "Toys & Games"),
	],

	#('baby-items', 253, "Baby Items"),
'baby-items' : [
	('baby-stroller-carrier-car-seat', 270, "Strollers, Carriers & Car Seats"),
	('baby-feeding-high-chair', 271, "Feeding & High Chairs"),
	('baby-toy', 256, "Toys"),
	('other-baby-items', 254, "Other"),
	('baby-playpen-swing-saucer', 268, "Playpens, Swings & Saucers"),
	('baby-crib-bassinet', 269, "Cribs"),
	('baby-bathing-changing-diapers', 272, "Bathing & Changing"),
	('baby-safety-gate-monitor', 273, "Gates, Monitors & Safety"),
	('baby-clothes-12-18-months', 262, "Clothing - 12-18 Months"),
	('baby-lot', 255, "Multi-item"),
	('baby-clothes-2t', 264, "Clothing - 2T"),
	('baby-clothes-18-24-months', 263, "Clothing - 18-24 Months"),
	('baby-clothes-3t', 265, "Clothing - 3T"),
	('baby-clothes-0-3-months', 258, "Clothing - 0-3 Months"),
	('baby-clothes-3-6-months', 259, "Clothing - 3-6 Months"),
	('baby-clothes-4t', 266, "Clothing - 4T"),
	('baby-clothes-6-9-months', 260, "Clothing - 6-9 Months"),
	('baby-clothes-9-12-months', 261, "Clothing - 9-12 Months"),
	('baby-clothes-5t', 267, "Clothing - 5T"),
	('baby-clothes-preemie', 257, "Clothing - Preemie"),
	],

	#('sporting-goods-exercise', 111, "Sporting Goods & Exercise"),
'sporting-goods-exercise' : [
	('exercise-equipment', 655, "Excercise Equipment"),
	('hockey', 659, "Hockey"),
	('golf', 658, "Golf"),
	('sport-other', 669, "Other"),
	('fishing-camping-outdoor', 656, "Fishing, Camping & Outdoors"),
	('skates-blades', 662, "Skates & Blades"),
	('soccer', 666, "Soccer"),
	('water-sport', 668, "Water Sports"),
	('ski', 664, "Ski"),
	('tennis-and-racket', 667, "Tennis & Racquet"),
	('baseball-softball', 652, "Baseballs & Softballs"),
	('snowboard', 665, "Snowboard"),
	('basketball', 653, "Basketball"),
	('skateboard', 663, "Skateboard"),
	('football', 657, "Football"),
	('paintball', 661, "Paintball"),
	('lacrosse', 660, "Lacrosse"),
	('curling', 654, "Curling"),
	],

	#('value', 29659001, "Electronics"),
'value' : [
	('general-electronics', 15, "General Electronics"),
	('security-systems', 29659002, "Security Systems"),
	],

	#('computer-accessories', 128, "Computer Accessories"),
'computer-accessories' : [
	('computer-components', 788, "System Components"),
	('printers-scanners-fax', 784, "Printers, Scanners & Fax"),
	('computer-networking', 783, "Networking"),
	('mice-keyboards-webcam', 781, "Mice, Keyboards & Webcams"),
	('laptop-accessories', 780, "Laptop Accessories"),
	('monitors', 782, "Monitors"),
	('networking-cables-and-connectors', 777, "Cables & Connectors"),
	('other-computer-products', 790, "Other"),
	('speakers-headsets-mics', 787, "Speakers, Headsets & Mics"),
	('ipad-tablet-accessories', 789, "iPad & Tablet Accessories"),
	('flash-memory-usb-sticks', 778, "Flash Memory & USB Sticks"),
	 #('service-training-repair', 785, "Services (Training & Repair"),
	('software', 786, "Software"),
	],

	#('home-appliances', 107, "Home Appliances"),
'home-appliances' : [
	('other-home-appliance', 701, "Other"),
	('microwave-cooker', 694, "Microwaves & Cookers"),
	('coffee-maker-espresso-machine', 689, "Coffee Makers"),
	('heater-humidifier-dehumidifier', 692, "Heaters, Humidifiers & Dehumidifiers"),
	('stove-oven-range', 697, "Stoves, Ovens & Ranges"),
	('washer-dryer', 700, "Washers & Dryers"),
	('vacuum', 699, "Vacuums"),
	('processor-blender-juicer', 695, "Processors, Blenders & Juicers"),
	('refrigerator-fridge', 696, "Refrigerators"),
	('toasters-toaster-oven', 698, "Toasters & Toaster Ovens"),
	('iron-garment-steamer', 693, "Irons & Garment Steamers"),
	('appliance-dishwasher', 690, "Dishwashers"),
	('freezer', 691, "Freezers"),
	],

	#('phone-tablet', 132, "Phones"),
'phone-tablet' : [
	('cell-phone', 760, "Cell Phones"),
	('cell-phone-accessories', 761, "Cell Phone Accessories"),
	##('cell-phone-services', 762, "Cell Phone Services"),
	('home-phone-answering-machine', 765, "Home Phones & Answering"),
	('phone-tablet-other', 766, "Other"),
	],

'jewelry-watch' : [
	('jewelry-watch', 133, "Jewellery & Watches"),
	],

	#('video-games-consoles', 141, "Video Games & Consoles"),
'video-games-consoles' : [
	('sony-playstation-4', 792, "Sony Playstation 4"),
	('old-video-games', 623, "Older Generation"),
	('xbox-one', 793, "XBOX One"),
	('nintendo-switch', 33035001, "Nintendo Switch"),
	('sony-playstation-5', 39730002, "Sony Playstation 5"),
	('sony-playstation-3', 627, "Sony Playstation 3"),
	('xbox-360', 622, "XBOX 360"),
	('video-games-consoles-other', 625, "Other"),
	('nintendo-ds', 619, "Nintendo DS"),
	('nintendo-wii', 626, "Nintendo Wii"),
	('pc-games', 624, "PC Games"),
	('xbox-series-x-s', 39730001, "Xbox Series X & S"),
	('nintendo-wii-u', 14654002, "Nintendo Wii U"),
	('sony-psp', 621, "Sony PSP & Vita"),
	],

'health-special-needs' : [
	('health-special-needs', 140, "Health & Special Needs")],

	#('bikes', 644, "Bikes"),
'bikes' : [
	('kids-bike', 646, "Kids"),
	('road-bike', 644, "Road"),
	('mountain-bike', 647, "Mountain"),
	('bike-frames-parts', 649, "Frames & Parts"),
	('bike-clothes-shoes-accessories', 650, "Clothing, Shoes & Accessories"),
	('cruiser-commuter-hybrid', 15096001, "Cruiser, Commuter & Hybrid"),
	('ebike', 14654001, "eBike"),
	('other-bike', 651, "Other"),
	('bmx-bike', 645, "BMX"),
	('fixie-single-speed', 15096002, "Fixie (Single Speed)"),
	],

	#('business-industrial', 29659003, "Business & Industrial"),
'business-industrial' : [
	('other-business-industrial', 145, "Other Business & Industrial"),
	('industrial-kitchen-supplies', 29659004, "Industrial Kitchen Supplies"),
	('storage-containers', 29659006, "Storage Containers"),
	('industrial-shelving-racking', 29659005, "Industrial Shelving & Racking"),
	],

'cd-dvd-blu-ray' : [
	('cd-dvd-blu-ray', 104, "CDs, DVDs & Blu-ray"),
	],

	#('home-renovation', 727, "Home Renovation Materials"),
'home-renovation' : [
	('plumbing-sink-toilet-shower', 734, "Plumbing, Sinks, Toilets & Showers"),
	('renovation-window-door-trim', 736, "Windows, Doors & Trim"),
	('renovation-cabinet-counter', 728, "Cabinets & Countertops"),
	('renovation-flooring-wall', 730, "Floors & Walls"),
	('renovation-other', 737, "Other"),
	('renovation-electrical', 729, "Electrical"),
	('heating-cooling-air', 732, "Heating, Cooling & Air"),
	('renovation-hardware-nail-screw', 731, "Hardware, Nails & Screws"),
	('paint-and-painting-supplies', 733, "Painting & Paint Supplies"),
	('roofing', 735, "Roofing"),
	],

'hobbies-craft' : [
	('hobbies-craft', 139, "Hobbies & Crafts"),
	],

	#('home-outdoor', 19, "Home - Outdoors & Garden"),
'home-outdoor' : [
	('gardening-plant-fertilizer-soil', 687, "Plants, Fertilizer & Soil"),
	('home-outdoor-other', 726, "Other"),
	('patio-garden-furniture', 19, "Patio & Garden Furniture"),
	('lawnmower-leaf-blower', 682, "Lawnmowers & Leaf Blowers"),
	('outdoor-decor', 683, "Outdoor Decor"),
	('bbq-outdoor-cooking', 678, "BBQs & Outdoor Cooking"),
	('outdoor-tools-storage', 685, "Outdoor Tools & Storage"),
	('outdoor-lighting', 684, "Outdoor Lighting"),
	('hot-tub-pool', 681, "Hot Tubs & Pools"),
	('snowblower', 688, "Snowblowers"),
	('deck-fence', 679, "Decks & Fences"),
	('garage-door-opener', 680, "Garage Doors & Openers"),
	],

'camera-camcorder-lens' : [
	('camera-camcorder-lens', 103, "Cameras & Camcorders"),
	],

	#('audio', 767, "Audio"),
'audio' : [
	('speakers', 14922002, "Speakers"),
	('headphones', 770, "Headphones"),
	('stereo-systems-home-theatre', 14922001, "Stereo Systems & Home Theatre"),
	('ipod-mp3-player-other', 771, "Other"),
	('ipod-mp3-player', 768, "iPods & MP3s"),
	('ipod-mp3-player-accessories', 769, "iPods & MP3s Accessories"),
	],

	#('computer', 16, "Computers"),
'computer' : [
	('laptops', 773, "Laptops"),
	('desktop-computers', 772, "Desktop Computers"),
	('ipads-tablets', 776, "iPads & Tablets"),
	('other', 29324001, "Other"),
	('servers', 774, "Servers"),
	],

	#('tool', 110, "Tools"),
'tool' : [
	('power-tool', 703, "Power Tools"),
	('hand-tool', 702, "Hand Tools"),
	('tool-other', 715, "Other"),
	('tool-storage-bench', 704, "Tool Storage & Benches"),
	('ladder-scaffolding', 705, "Ladders & Scaffolding"),
	],

	#('musical-instrument', 17, "Musical Instruments"),
'musical-instrument' : [
	('guitar', 613, "Guitars"),
	('amp-pedal', 610, "Amps & Pedals"),
	('piano-keyboard', 614, "Pianos & Keyboards"),
	('pro-audio-recording', 615, "Pro Audio & Recording Equipment"),
	('drum-percussion', 612, "Drums & Percussion"),
	('performance-dj-equipment', 14922003, "Performance & DJ Equipment"),
	('other-musical-instrument', 618, "Other"),
	('string-instrument', 616, "String"),
	('woodwind', 617, "Woodwind"),
	('brass-instrument-horn', 611, "Brass"),
	],

	#('tvs-video', 15093001, "TVs & Video"),
'tvs-video' : [
	('tvs', 15093002, "TVs"),
	('video-tv-accessories', 15093003, "Video & TV Accessories"),
	],

'free-stuff' : [
	('free-stuff', 17220001, "Free Stuff"),
	],

'garage-sale-yard-sale' : [
	('garage-sale-yard-sale', 638, "Garage Sales"),
	],
	}

for tup in category_list:
	disabled = tup[0] in disabled_list
	Category(*tup, parent=buy_sell, disabled=disabled)

for cat in category_dict:
	for tup in category_dict[cat]:
		disabled = tup[0] in disabled_list
		Category(*tup, parent=by_name(cat), disabled=disabled)

#print(len([item.name for item in items(disabled=True) if item not in items()]))
