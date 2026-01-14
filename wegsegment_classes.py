"""
wegsegment_classes.py
---------------------
Bevat de gedeelde klasse BaseWeg en twee subklassen:
- Weg (Wallonië)
- WegBrussel (Brussels Hoofdstedelijk Gewest)
"""

import re
from dataclasses import dataclass, field
from typing import Any, Optional

from wegsegment_constants import (
    MORFOLOGIE, WEGCAT, TYPOLOGIE_WEGCAT,
    DEFAULT_STATUS, DEFAULT_LBLSTATUS,
    DEFAULT_MORF, DEFAULT_LBLMORF,
    DEFAULT_LEGENDE,
    DEFAULT_METHODE, DEFAULT_LBLMETHOD,
    DEFAULT_DATUM,
    DEFAULT_TGBEP, DEFAULT_LBLTGBEP,
    NOT_KNOWN, NOT_KNOWN_LABEL, NOT_KNOWN_ID
)
from wegsegment_utils import OidnManager
from wegsegment_events import make_event_rijstrook, make_event_wegbreedte, make_event_wegverharding


# -------------------------
# BaseWeg
# -------------------------
@dataclass
class BaseWeg:
    """Basisklasse met gedeelde logica: events + export."""

    geometrie: Any
    bron: Optional[str] = None

    beginM: float = field(init=False)
    eindM: float = field(init=False)
    ws_oidn: int = field(init=False)
    ws_uidn: str = field(init=False)
    ws_gidn: str = field(init=False)
    lblmorf: str = field(init=False)
    status: int = field(init=False)
    wegcat: str = field(init=False)
    beheer: str = field(init=False)
    lblbeheer: str = field(init=False)

    # Events
    rsoidn: Optional[int] = field(init=False, default=None)
    strnmid: Optional[int] = field(init=False, default=None)
    rijstroken_aantal: Optional[int] = field(init=False, default=None)
    rijstroken_richting: Optional[int] = field(init=False, default=None)
    rijstroken_lblricht: Optional[str] = field(init=False, default=None)
    wboidn: Optional[int] = field(init=False, default=None)
    breedte: Optional[float] = field(init=False, default=None)
    wvoidn: Optional[int] = field(init=False, default=None)
    type_wegverharding: Optional[int] = field(init=False, default=None)
    lbltype_wegverharding: Optional[str] = field(init=False, default=None)
    ident2: Optional[str] = field(init=False, default=None)
    nwoidn: Optional[int] = field(init=False, default=None)
    ident8: Optional[str] = field(init=False, default=None)
    gwoidn: Optional[int] = field(init=False, default=None)
    volgnummer: Optional[int] = field(init=False, default=None)

    # Vaste attributen
    methode: int = field(init=False, default=DEFAULT_METHODE)
    lblmethod: str = field(init=False, default=DEFAULT_LBLMETHOD)
    opndatum: str = field(init=False, default=DEFAULT_DATUM)
    begintijd: str = field(init=False, default=DEFAULT_DATUM)
    tgbep: int = field(init=False, default=DEFAULT_TGBEP)
    lbltgbep: str = field(init=False, default=DEFAULT_LBLTGBEP)
    # Defaults
    status_val: int = field(init=False, default=DEFAULT_STATUS)
    lblstatus: str = field(init=False, default=DEFAULT_LBLSTATUS)
    morf: int = field(init=False, default=DEFAULT_MORF)
    legende: int = field(init=False, default=DEFAULT_LEGENDE)

    def __init__(self):
        self.lblricht_ident8 = None
        self.richting_ident8 = None

    def __post_init__(self):
        OidnManager.initialize_oidns(self.bron)
        self.beginM = round(self.geometrie[0][0].M, 3)
        self.eindM = round(self.geometrie[-1][-1].M, 3)
        self.ws_oidn = OidnManager.ws_oidn
        self.ws_uidn = f"{self.ws_oidn}_1"
        self.ws_gidn = f"{self.ws_oidn}_1"
        self.strnmid = OidnManager.strnmid
        OidnManager.ws_oidn += 1
        self.legende = DEFAULT_LEGENDE

    def _set_legende(self):
        # mapping op basis van lblmorf
        lblmorf_mapping = {
            "dienstweg": 8,
            "in- of uitrit van een dienst": 8,
            "tramweg, niet toegankelijk voor andere voertuigen": 12,
            "veer": 12,
            "aardeweg": 10,
            "wandel- of fietsweg, niet toegankelijk voor andere voertuigen": 9,
        }

        # mapping op basis van wegcat
        wegcat_mapping = {
            "EW": 8,  # let op: je had 2 verschillende waarden voor EW (8 en 7) → keuze maken!
            "OW": None,  # speciale logica → hieronder
            "RW": 4,
            "IW": 4,
            "VHW": 3,
            "EHW": 1,
        }

        # status krijgt voorrang
        if getattr(self, "status", None) == "in aanbouw":
            self.legende = 14
            return

        # lblmorf mapping
        if self.lblmorf in lblmorf_mapping:
            self.legende = lblmorf_mapping[self.lblmorf]
            return

        # wegcat speciale case OW
        if self.wegcat == "OW":
            if "AWV" in (self.lblbeheer or ""):
                self.legende = 5
            else:
                self.legende = 6
            return

        # wegcat mapping
        if self.wegcat in wegcat_mapping and wegcat_mapping[self.wegcat] is not None:
            self.legende = wegcat_mapping[self.wegcat]
            return

        # fallback
        self.legende = DEFAULT_LEGENDE

    def _add_events(self, sens_bk=None, richting=None):
        make_event_rijstrook(self)
        make_event_wegbreedte(self)
        make_event_wegverharding(self)

    # ---- Exportmethodes ----
    def export_wegsegment_as_list(self):
        return [self.geometrie, self.ws_oidn, self.ws_uidn, self.ws_gidn,
                getattr(self, "status_val", None), getattr(self, "lblstatus", None),
                getattr(self, "morf", None), getattr(self, "lblmorf", None),
                getattr(self, "wegcat", None), getattr(self, "lblwegcat", None),
                getattr(self, "lstrnmid", None), getattr(self, "lstrnm", None),
                getattr(self, "rstrnmid", None), getattr(self, "rstrnm", None),
                getattr(self, "beheer", None), getattr(self, "lblbeheer", None),
                self.methode, self.lblmethod, self.opndatum, self.begintijd,
                getattr(self, "beginorg", None), getattr(self, "lblbgnorg", None),
                self.tgbep, self.lbltgbep, getattr(self, "legende", None), self.bron]

    def export_nationweg_as_list(self):
        return [getattr(self, "nwoidn", None), self.ws_oidn,
                self.ident2, self.begintijd,
                getattr(self, "beginorg", None), getattr(self, "lblbgnorg", None)]

    def export_genummerdeweg_as_list(self):
        return [getattr(self, "gwoidn", None), self.ws_oidn,
                getattr(self, "ident8", None), getattr(self, "richting_ident8", NOT_KNOWN),
                getattr(self, "lblricht_ident8", NOT_KNOWN_LABEL),
                getattr(self, "volgnummer", NOT_KNOWN), self.begintijd,
                getattr(self, "beginorg", None), getattr(self, "lblbgnorg", None)]

    def export_rijstroken_as_list(self):
        return [self.rsoidn, self.ws_oidn, self.ws_gidn, self.rijstroken_aantal,
                self.rijstroken_richting, self.rijstroken_lblricht,
                self.beginM, self.eindM, self.begintijd,
                getattr(self, "beginorg", None), getattr(self, "lblbgnorg", None)]

    def export_wegbreedte_as_list(self):
        return [self.wboidn, self.ws_oidn, self.ws_gidn, self.breedte,
                self.beginM, self.eindM, self.begintijd,
                getattr(self, "beginorg", None), getattr(self, "lblbgnorg", None)]

    def export_wegverharding_as_list(self):
        return [self.wvoidn, self.ws_oidn, self.ws_gidn,
                self.type_wegverharding, self.lbltype_wegverharding,
                self.beginM, self.eindM, self.begintijd,
                getattr(self, "beginorg", None), getattr(self, "lblbgnorg", None)]


# -------------------------
# Weg (Wallonië)
# -------------------------
@dataclass
class WegWallonie(BaseWeg):
    """Wallonië‐wegsegment."""

    nature_desc: Optional[str] = None
    icarrueid1: Optional[int] = None
    rue_nom1: Optional[str] = None
    commu_nom1: Optional[str] = None
    commu_ins1: Optional[str] = None
    icarrueid2: Optional[int] = None
    rue_nom2: Optional[str] = None
    commu_nom2: Optional[str] = None
    commu_ins2: Optional[str] = None
    gestion: Optional[str] = None
    voirie_nom: Optional[str] = None
    sens_bk: Optional[str] = None
    amenag: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self.beginorg, self.lblbgnorg = "SPW", "Service public de Wallonie"

        # Specifieke logica
        self.set_morfologie()
        self.set_straatnaam()
        self.set_beheer()
        self.set_wegcat()
        self._set_legende()
        self.set_ident2()
        self.set_ident8()

        # Events
        self._add_events(sens_bk=self.sens_bk)

    def set_morfologie(self):
        if self.nature_desc and self.nature_desc in MORFOLOGIE.values():
            for k, v in MORFOLOGIE.items():
                if v == self.nature_desc:
                    self.morf, self.lblmorf = k, v
                    break
        else:
            self.morf, self.lblmorf = DEFAULT_MORF, DEFAULT_LBLMORF

        wegnummer_pattern = r'^[A-Z]\d{7}$'
        if self.nature_desc == 'Autoroute':
            if len(self.voirie_nom) == 7 and re.match(wegnummer_pattern, self.voirie_nom):
                if int(self.voirie_nom[4]) < 5:
                    self.morf = 107
                elif int(self.voirie_nom[4]) == 5:
                    self.morf = 109
                else:
                    self.morf = 101
            else:
                self.morf = 101
        elif self.nature_desc == 'Ring':
            if len(self.voirie_nom) == 7:
                if int(self.voirie_nom[4]) < 5:
                    self.morf = 107
                elif int(self.voirie_nom[4]) == 5:
                    self.morf = 109
                else:
                    self.morf = 101
            elif len(self.voirie_nom) == 2:
                self.morf = 101
        elif self.amenag == "RP":
            self.morf = 104
        elif self.sens_bk in ("C", "D"):
            self.morf = 102
        else:
            self.morf = 103  # Standaard waarde als geen andere voorwaarden zijn voldaan

        # Gebruik de morf code om de beschrijving te krijgen, of 'onbekend' als de code niet in de dictionary voorkomt
        self.lblmorf = MORFOLOGIE.get(self.morf, 'onbekend')

    def set_wegcat(self):
        self.wegcat = NOT_KNOWN
        self.lblwegcat = NOT_KNOWN_LABEL
        if self.nature_desc == 'Autoroute':
            self.wegcat = "EHW"
        elif self.nature_desc == 'Ring':
            if len(self.voirie_nom) == 2:
                self.wegcat = "EHW"
            elif self.voirie_nom[2] != 0:
                self.wegcat = "EHW"
        elif self.voirie_nom not in ("", " "):
            self.wegcat = "RW"
        else:
            self.wegcat = "OW"

        # Gebruik de morf code om de beschrijving te krijgen, of 'onbekend' als de code niet in de dictionary voorkomt
        self.lblwegcat = WEGCAT.get(self.wegcat, 'onbekend')

    def set_straatnaam(self):
        # Linkerzijde
        if self.icarrueid1 is not None and self.icarrueid1 != 0:
            self.lstrnmid = self.icarrueid1 + self.strnmid
            self.lstrnm = self.rue_nom1
        else:
            self.lstrnmid = NOT_KNOWN_ID
            self.lstrnm = NOT_KNOWN_LABEL

        # Rechterzijde
        if self.icarrueid2 is not None and self.icarrueid2 != 0:
            self.rstrnmid = self.icarrueid2 + self.strnmid
            self.rstrnm = self.rue_nom2
        elif self.icarrueid1 is not None and self.icarrueid1 != 0:
            self.rstrnmid = self.lstrnmid
            self.rstrnm = self.lstrnm
        else:
            self.rstrnmid = NOT_KNOWN_ID
            self.rstrnm = NOT_KNOWN_LABEL

    def set_beheer(self, d_beheer=None):
        """
        Stel beheer en labelbeheer in op basis van de bron.

        bron: 'wallonie', 'brussel', of 'generiek'
        d_beheer: optioneel, alleen gebruikt voor 'brussel'
        """
        if self.bron == 'WAL':
            if self.gestion == 'Service public de Wallonie':
                self.beheer = "SPW"
                self.lblbeheer = 'Service public de Wallonie'
            elif self.gestion == 'Commune':
                self.beheer = getattr(self, "commu_ins1", NOT_KNOWN)
                self.lblbeheer = f"gemeente {getattr(self, 'commu_nom1', NOT_KNOWN_LABEL)}"
            else:
                self.beheer = NOT_KNOWN
                self.lblbeheer = NOT_KNOWN_LABEL

        elif self.bron == 'BRU':
            self.beheer = getattr(self, "admin", NOT_KNOWN)
            self.lblbeheer = d_beheer.get(self.beheer, NOT_KNOWN_LABEL) if d_beheer else NOT_KNOWN_LABEL

        else:  # generiek
            self.beheer = getattr(self, "gestion", NOT_KNOWN)
            self.lblbeheer = getattr(self, "voirie_nom", NOT_KNOWN_LABEL)

    def set_ident2(self):
        pattern = r"^[A-Z]\d{1,3}[a-z]{0,1}$"
        if self.voirie_nom and re.match(pattern, self.voirie_nom):
            self.ident2 = self.voirie_nom
            self.nwoidn = OidnManager.nw_oidn
            OidnManager.nw_oidn += 1

    def set_ident8(self, alfabet: str = "abcdefghijklmnopqrstuvwxyz") -> None:
        import re
        """
        Zet self.ident8 volgens het wegenregister-formaat.
        - Hoofdbaan: [A-Z][1-3 cijfers][optionele letter]
                     -> A001 of A001901
        - Niet-hoofdbaan: [A-Z][6 cijfers]
                     -> A001501
        """
        if not self.voirie_nom:
            return None  # Geen invoer => geen ident8

        pattern_hoofdbaan = r"^[A-Z]\d{1,3}[a-z]?$"
        pattern_niethoofd = r"^[A-Z]\d{6}$"

        self.gwoidn = OidnManager.gw_oidn
        OidnManager.gw_oidn += 1

        wegtype = self.voirie_nom[0]

        if re.match(pattern_hoofdbaan, self.voirie_nom):
            # Voorbeeld: A1, A1a, A220
            nummer_match = re.search(r"\d{1,3}", self.voirie_nom)
            wegnummer = f"{int(nummer_match.group()):03d}" if nummer_match else "000"

            # Optionele letter → 900 + positie in alfabet
            letter = self.voirie_nom[-1].lower()
            if letter is not None and letter in alfabet:
                pos = alfabet.index(letter) + 1  # a=1, b=2, ...
                wegindex = f"9{pos:02d}"  # 901, 902, ...
            else:
                wegindex = "000"

        elif re.match(pattern_niethoofd, self.voirie_nom):
            # Voorbeeld: A001501
            wegnummer = self.voirie_nom[1:4]
            wegindex = self.voirie_nom[4:]  # laatste 3 cijfers
        else:
            # Onbekend formaat
            wegnummer = None
            wegindex = None

        if self.sens_bk in ("C", "", "CD"):
            opdalend = 1
            self.richting_ident8 = 1
            self.lblricht_ident8 = "gelijklopend met de digitalisatiezin"
        elif self.sens_bk == "D":
            opdalend = 2
            self.richting_ident8 = 2
            self.lblricht_ident8 = "tegengesteld aan de digitalisatiezin"
        else:
            opdalend = 0

        # Samenstellen ident8
        self.ident8 = f"{wegtype}{wegnummer}{wegindex}{opdalend}"

        # Extra attributen (indien gewenst later ingevuld)
        self.volgnummer = NOT_KNOWN


# -------------------------
# WegBrussel
# -------------------------
@dataclass
class WegBrussel(BaseWeg):
    """Brussels wegsegment."""

    from_node: Any = None
    to_node: Any = None
    pn_id_l: Optional[str] = None
    pn_id_r: Optional[str] = None
    nat_road_i: Optional[str] = None
    lvl: Optional[int] = None
    morphology: Optional[int] = None
    admin: Optional[str] = None
    typology: Optional[str] = None
    status: Any = None
    richting: Optional[int] = None
    d_status: Optional[dict] = None
    d_morphology: Optional[dict] = None
    d_straatnaam_links: Optional[dict] = None
    d_straatnaam_rechts: Optional[dict] = None
    d_beheer: Optional[dict] = None

    def __post_init__(self):
        super().__post_init__()
        self.beginorg, self.lblbgnorg = "BG", "Brussels Gewest"

        # Status
        self.status_val = int(self.status) if self.status is not None else DEFAULT_STATUS
        self.lblstatus = self.d_status.get(self.status_val, DEFAULT_LBLSTATUS)

        # Morfologie
        self.morf = int(self.morphology) if self.morphology not in (None, 130) else DEFAULT_MORF
        self.lblmorf = self.d_morphology.get(self.morf, DEFAULT_LBLMORF)

        # Wegcat via typology
        self.wegcat = TYPOLOGIE_WEGCAT.get(self.typology, NOT_KNOWN)
        self.lblwegcat = WEGCAT.get(self.wegcat, NOT_KNOWN_LABEL)

        # Straatnamen
        self.lstrnmid = int(self.pn_id_l.strip()) if self.pn_id_l and self.pn_id_l.strip().isdigit() else NOT_KNOWN_ID
        self.lstrnm = self.d_straatnaam_links.get(self.lstrnmid, NOT_KNOWN_LABEL)
        self.rstrnmid = int(self.pn_id_r.strip()) if self.pn_id_r and self.pn_id_r.strip().isdigit() else NOT_KNOWN_ID
        self.rstrnm = self.d_straatnaam_rechts.get(self.rstrnmid, NOT_KNOWN_LABEL)

        # Beheer
        self.set_beheer(d_beheer=self.d_beheer)
        # self.beheer = self.admin if self.admin is not None else NOT_KNOWN
        # self.lblbeheer = self.d_beheer.get(self.beheer, NOT_KNOWN_LABEL)

        # Legende & Ident2
        self._set_legende()
        self.set_ident2()

        # Events
        self._add_events(richting=self.richting)

    def set_ident2(self):
        pattern = r"^[A-Z]\\d{1,3}[a-z]{0,1}$"
        if self.nat_road_i and re.match(pattern, self.nat_road_i):
            self.ident2 = self.nat_road_i
            self.nwoidn = OidnManager.nw_oidn
            OidnManager.nw_oidn += 1
