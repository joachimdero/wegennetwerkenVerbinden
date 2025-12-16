"""
wr_constants.py
---------------
Vaste waarden en mapping-tabellen voor wegenregister.
"""

# Morfologie codes en labels
MORFOLOGIE = {
    101: "autosnelweg",
    102: "weg met gescheiden rijbanen die geen autosnelweg is",
    103: "weg bestaande uit één rijbaan",
    104: "rotonde",
    105: "speciale verkeerssituatie",
    106: "verkeersplein",
    107: "op- of afrit, behorende tot een niet-gelijkgrondse verbinding",
    108: "op- of afrit, behorende tot een gelijkgrondse verbinding",
    109: "parallelweg",
    110: "ventweg",
    111: "in- of uitrit van een parking",
    112: "in- of uitrit van een dienst",
    113: "voetgangerszone",
    114: "wandel- of fietsweg, niet toegankelijk voor andere voertuigen",
    116: "tramweg, niet toegankelijk voor andere voertuigen",
    120: "dienstweg",
    125: "aardeweg",
    130: "veer"
}

# Wegcategorie codes en labels
WEGCAT = {
    "-8": "niet gekend",
    "-9": "niet van toepassing",
    "EHW": "europese hoofdweg",
    "VHW": "vlaamse hoofdweg",
    "RW": "regionale weg",
    "IW": "interlokale weg",
    "OW": "lokale ontsluitingsweg",
    "EW": "lokale erftoegangsweg",
}

# Specifiek voor Brussel: typologie → wegcat mapping
TYPOLOGIE_WEGCAT = {
    "A0": "EHW", "A0b": "VHW",
    "A1": "RW", "A2": "RW",
    "A3": "IW", "A4": "EW",
    "A5": "EW", "B1": "EW",
}

# -------------------------
# Defaults en 'niet gekend'
# -------------------------
DEFAULT_STATUS = 4
DEFAULT_LBLSTATUS = "in gebruik"

DEFAULT_MORF = -8
DEFAULT_LBLMORF = "onbekend"

DEFAULT_LEGENDE = 8

DEFAULT_METHODE = 2
DEFAULT_LBLMETHOD = "ingemeten"

DEFAULT_DATUM = "19500101T000000"

DEFAULT_TGBEP = 1
DEFAULT_LBLTGBEP = "openbare weg"

NOT_KNOWN = "-8"
NOT_KNOWN_LABEL = "niet gekend"
NOT_KNOWN_ID = -9
