"""Panchanga element names: tithi, nakshatra, yoga, karana."""

# 30 tithi names (index 0 = Pratipada Shukla, ... 14 = Purnima, 15 = Pratipada Krishna, ... 29 = Amavasya)
TITHI_NAMES_BN = [
    # Shukla paksha (1-15)
    "প্রতিপদ", "দ্বিতীয়া", "তৃতীয়া", "চতুর্থী", "পঞ্চমী",
    "ষষ্ঠী", "সপ্তমী", "অষ্টমী", "নবমী", "দশমী",
    "একাদশী", "দ্বাদশী", "ত্রয়োদশী", "চতুর্দশী", "পূর্ণিমা",
    # Krishna paksha (16-30)
    "প্রতিপদ", "দ্বিতীয়া", "তৃতীয়া", "চতুর্থী", "পঞ্চমী",
    "ষষ্ঠী", "সপ্তমী", "অষ্টমী", "নবমী", "দশমী",
    "একাদশী", "দ্বাদশী", "ত্রয়োদশী", "চতুর্দশী", "অমাবস্যা",
]

TITHI_NAMES_EN = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

# 27 nakshatra names (index 0 = Ashwini)
NAKSHATRA_NAMES_BN = [
    "অশ্বিনী", "ভরণী", "কৃত্তিকা", "রোহিণী", "মৃগশিরা",
    "আর্দ্রা", "পুনর্বসু", "পুষ্যা", "আশ্লেষা", "মঘা",
    "পূর্ব ফাল্গুনী", "উত্তর ফাল্গুনী", "হস্তা", "চিত্রা", "স্বাতী",
    "বিশাখা", "অনুরাধা", "জ্যেষ্ঠা", "মূলা", "পূর্বাষাঢ়া",
    "উত্তরাষাঢ়া", "শ্রবণা", "ধনিষ্ঠা", "শতভিষা", "পূর্ব ভাদ্রপদ",
    "উত্তর ভাদ্রপদ", "রেবতী",
]

NAKSHATRA_NAMES_EN = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]

# 27 yoga names (index 0 = Vishkambha)
YOGA_NAMES_BN = [
    "বিষ্কম্ভ", "প্রীতি", "আয়ুষ্মান", "সৌভাগ্য", "শোভন",
    "অতিগণ্ড", "সুকর্মা", "ধৃতি", "শূল", "গণ্ড",
    "বৃদ্ধি", "ধ্রুব", "ব্যাঘাত", "হর্ষণ", "বজ্র",
    "সিদ্ধি", "ব্যতীপাত", "বরীয়ান", "পরিঘ", "শিব",
    "সিদ্ধ", "সাধ্য", "শুভ", "শুক্ল", "ব্রহ্ম",
    "ইন্দ্র", "বৈধৃতি",
]

YOGA_NAMES_EN = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]

# 11 karana types (7 repeating + 4 fixed)
# Repeating (index 0-6): Bava, Balava, Kaulava, Taitila, Garaja, Vanija, Vishti (Bhadra)
# Fixed: Shakuni, Chatushpada, Naga, Kimstughna
KARANA_NAMES_BN = [
    # Repeating (mapped from karana_index)
    "বব", "বালব", "কৌলব", "তৈতিল", "গরজ", "বণিজ", "বিষ্টি",
    # Fixed
    "শকুনি", "চতুষ্পদ", "নাগ", "কিংস্তুঘ্ন",
]

KARANA_NAMES_EN = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna",
]

PAKSHA_SHUKLA_BN = "শুক্লপক্ষ"
PAKSHA_KRISHNA_BN = "কৃষ্ণপক্ষ"
PAKSHA_SHUKLA_EN = "Shukla"
PAKSHA_KRISHNA_EN = "Krishna"
