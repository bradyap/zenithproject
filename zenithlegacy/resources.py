import itertools

languages = [
    'aa', 'Afar',
    'ab', 'Abkhazian',
    'af', 'Afrikaans',
    'ak', 'Akan',
    'sq', 'Albanian',
    'am', 'Amharic',
    'ar', 'Arabic',
    'an', 'Aragonese',
    'hy', 'Armenian',
    'as', 'Assamese',
    'av', 'Avaric',
    'ae', 'Avestan',
    'ay', 'Aymara',
    'az', 'Azerbaijani',
    'ba', 'Bashkir',
    'bm', 'Bambara',
    'eu', 'Basque',
    'be', 'Belarusian',
    'bn', 'Bengali',
    'bh', 'Bihari',
    'bi', 'Bislama',
    'bo', 'Tibetan',
    'bs', 'Bosnian',
    'br', 'Breton',
    'bg', 'Bulgarian',
    'my', 'Burmese',
    'ca', 'Catalan',
    'ca', 'Valencian',
    'cs', 'Czech',
    'ch', 'Chamorro',
    'ce', 'Chechen',
    'zh', 'Chinese',
    'cu', 'Slavic',
    'cv', 'Chuvash',
    'kw', 'Cornish',
    'co', 'Corsican',
    'cr', 'Cree',
    'cy', 'Welsh',
    'cs', 'Czech',
    'da', 'Danish',
    'de', 'German',
    'dv', 'Divehi',
    'nl', 'Dutch',
    'dz', 'Dzongkha',
    'el', 'Greek',
    'en', 'English',
    'eo', 'Esperanto',
    'et', 'Estonian',
    'eu', 'Basque',
    'ee', 'Ewe',
    'fo', 'Faroese',
    'fa', 'Persian',
    'fj', 'Fijian',
    'fi', 'Finnish',
    'fr', 'French',
    'fy', 'Frisian',
    'ff', 'Fulah',
    'Ga', 'Georgian',
    'de', 'German',
    'gd', 'Gaelic',
    'ga', 'Irish',
    'gl', 'Galician',
    'gv', 'Manx',
    'gn', 'Guarani',
    'gu', 'Gujarati',
    'ht', 'Haitian',
    'ha', 'Hausa',
    'he', 'Hebrew',
    'hz', 'Herero',
    'hi', 'Hindi',
    'hr', 'Croatian',
    'hu', 'Hungarian',
    'hy', 'Armenian',
    'ig', 'Igbo',
    'is', 'Icelandic',
    'io', 'Ido',
    'iu', 'Inuktitut',
    'ie', 'Interlingue',
    'ia', 'Interlingua',
    'id', 'Indonesian',
    'ik', 'Inupiaq',
    'is', 'Icelandic',
    'it', 'Italian',
    'jv', 'Javanese',
    'ja', 'Japanese',
    'kl', 'Kalaallisut',
    'kn', 'Kannada',
    'ks', 'Kashmiri',
    'ka', 'Georgian',
    'kr', 'Kanuri',
    'kk', 'Kazakh',
    'ki', 'Kikuyu',
    'rw', 'Kinyarwanda',
    'ky', 'Kirghiz',
    'kv', 'Komi',
    'kg', 'Kongo',
    'ko', 'Korean',
    'kj', 'Kuanyama',
    'ku', 'Kurdish',
    'lo', 'Lao',
    'la', 'Latin',
    'lv', 'Latvian',
    'li', 'Limburgan',
    'ln', 'Lingala',
    'lt', 'Lithuanian',
    'lb', 'Luxembourgish',
    'lu', 'Luba-Katanga',
    'lg', 'Ganda',
    'mk', 'Macedonian',
    'mh', 'Marshallese',
    'ml', 'Malayalam',
    'mi', 'Maori',
    'mr', 'Marathi',
    'ms', 'Malay',
    'Mi', 'Micmac',
    'mk', 'Macedonian',
    'mg', 'Malagasy',
    'mt', 'Maltese',
    'mn', 'Mongolian',
    'mi', 'Maori',
    'ms', 'Malay',
    'my', 'Burmese',
    'na', 'Nauru',
    'nv', 'Navajo',
    'ng', 'Ndonga',
    'ne', 'Nepali',
    'nl', 'Dutch',
    'no', 'Norwegian',
    'oc', 'Occitan',
    'oj', 'Ojibwa',
    'or', 'Oriya',
    'om', 'Oromo',
    'os', 'Ossetian',
    'pa', 'Panjabi',
    'fa', 'Persian',
    'pi', 'Pali',
    'pl', 'Polish',
    'pt', 'Portuguese',
    'ps', 'Pushto',
    'qu', 'Quechua',
    'rm', 'Romansh',
    'ro', 'Romanian',
    'rn', 'Rundi',
    'ru', 'Russian',
    'sg', 'Sango',
    'sa', 'Sanskrit',
    'si', 'Sinhala',
    'sk', 'Slovak',
    'sl', 'Slovenian',
    'sm', 'Samoan',
    'sn', 'Shona',
    'sd', 'Sindhi',
    'so', 'Somali',
    'st', 'Sotho',
    'es', 'Spanish',
    'sq', 'Albanian',
    'sc', 'Sardinian',
    'sr', 'Serbian',
    'ss', 'Swati',
    'su', 'Sundanese',
    'sw', 'Swahili',
    'sv', 'Swedish',
    'ty', 'Tahitian',
    'ta', 'Tamil',
    'tt', 'Tatar',
    'te', 'Telugu',
    'tg', 'Tajik',
    'tl', 'Tagalog',
    'th', 'Thai',
    'bo', 'Tibetan',
    'ti', 'Tigrinya',
    'to', 'Tonga',
    'tn', 'Tswana',
    'ts', 'Tsonga',
    'tk', 'Turkmen',
    'tr', 'Turkish',
    'tw', 'Twi',
    'ug', 'Uighur',
    'uk', 'Ukrainian',
    'ur', 'Urdu',
    'uz', 'Uzbek',
    've', 'Venda',
    'vi', 'Vietnamese',
    'vo', 'Volapük',
    'cy', 'Welsh',
    'wa', 'Walloon',
    'wo', 'Wolof',
    'xh', 'Xhosa',
    'yi', 'Yiddish',
    'yo', 'Yoruba',
    'za', 'Zhuang',
    'zh', 'Chinese',
    'zu', 'Zulu'
]

langs = dict(itertools.zip_longest(*[iter(languages)] * 2, fillvalue=""))

pickupLines = [
    "https://cdn.discordapp.com/attachments/681621066472357909/821406315158437898/636435082407071080-sst1.png",  
    "Hey {name}, are you a cat? Because you're purr-fect.",
    "Hey {name}, I’d like to take you to the movies, but they don’t let you bring in your own snacks.",
    "{name}: If I were a cat, I’d spend all nine of my lives with you.",
    "{name}: if you were a chicken, you’d be impeccable.",
    "Hey {name}: my name's {author}. Just so you know what to scream.",
    "{name}, I only have 12 hours to live... please don’t let me die a virgin.",
    "Hey {name}, kiss me if I’m wrong, but dinosaurs still exist, right?",
    "{name}, did it hurt when you fell from the vending machine? Cause you look like a snack!",
    "Hey {name}, I’m no electrician, but I can light up your day.",
    "{name}: You're hotter than the bottom of my laptop.",
    "Hey {name}, are you a tower? Because eiffel for you!",
    "{name} - I’d never play hide and seek with you because someone like you is impossible to find.",
    "Hey {name}, are you australian? Because you meet all of my koalafications.",
    "Hey {name}, are you a keyboard? Because you’re just my type.",
    "If you let me borrow a kiss, {name}, I promise I’ll give it right back.",
    "There must be something wrong with my eyes, {name}... I can’t seem to take them off of you.",
    "Hey {name}, let’s commit the perfect crime: I’ll steal you’re heart, and you’ll steal mine.",
    "Hey {name}, I’ve been wondering, do your lips taste as good as they look?",
    "Hey {name}, I’m on top of things. Would you like to be one of them?",
    "Hey {name}, I was wondering if you had an extra heart, mine seems to have been stolen.",
    "Hey {name}, I know you’re busy today but can you add me to your to-do list?",
    "Hey {name}, I’m feeling a little bit off today, but you definitely turned me on.",
    "Hey {name}, you look cold. Want to use me as a blanket?",
    "Hey {name}, are you retarded? Cause you lookin extra special today.",
    "Damn {name}, you a bagel? Cause I'd spread my cream all over you.",
    "Hey {name}, are you my flute? Cause I want to blow you.",
    "Hey {name}, are you a drum? Cause I'd hit it.",
    "Hey {name}, are you a pair of gloves? Cause I wanna put my hands in you.",
    "Hey {name}, are you a guitar? Cause I'd like to finger you.",
    "Ayo {name}, are you a bath tub? Cause I'd like to fill you up.",
    "Hey {name}, sorry for untying your shoes, I just want you to fall for me.",
    "Hey {name}, my car broke down. Can I ride you insead?",
    "{name}, are you my dinner? Cause you're a full course meal.",
    "Hey {name}, are you ice cream? Because your face looks like Rocky Road.",
    "{name}, are you a chair? Cause I wanna sit on your face.",
    "{name}. You may not be Jesus, but I'd still nail the heck out of you.",
    "{name}, I put the \"std\" in \"stud.\" The only thing I need now is \"u.\",",
    "Hey {name}, are you a stimulus check? Cause you stimulate me. ;)",
    "Hey {name}, are you a roller coaster. Cause whenever I'm riding you, I never wanna stop.",
    "Hey {name}, are you a roller coaster. Cause when I ride you, I'm always screaming.",
    "{name}: I'm no weatherman, but I can gaurantee that you'll be getting a few inches tonight.",
    "Hey {name}, are you my homework? Cause I wanna slam you against the table and do you all night long.",
    "{name}: there are 8 planets in our solar system, but there'll be 7 after I destroy Uranus.",
    "Hey {name}, are you the Pfizer vaccine? Because I'm a minor and I want you in me.",
]