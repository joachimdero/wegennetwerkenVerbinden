import re
import sys
import traceback

import arcpy.da


class Weg:
    ws_oidn = 0
    nw_oidn = 0
    rs_oidn = 0
    wb_oidn = 0
    wv_oidn = 0
    strnmid = 0
    initialized = {'VLA': False, 'WAL': False, 'GRENS': False, 'BRU': False}

    @classmethod
    def initialize_oidns(cls, bron):
        if not cls.initialized.get(bron, False):
            if bron == 'WAL':
                cls.ws_oidn = cls.nw_oidn = cls.rs_oidn = cls.wb_oidn = cls.wv_oidn = cls.strnmid = 200000000
            elif bron == 'GRENS':
                cls.ws_oidn = cls.nw_oidn = cls.rs_oidn = cls.wb_oidn = cls.wv_oidn = cls.strnmid = 300000000
            elif bron == 'BRU':
                cls.ws_oidn = cls.nw_oidn = cls.rs_oidn = cls.wb_oidn = cls.wv_oidn = cls.strnmid = 400000000
            else:
                cls.ws_oidn = cls.nw_oidn = cls.rs_oidn = cls.wb_oidn = cls.wv_oidn = cls.strnmid = 0  # default value if bron is unknown
            cls.initialized[bron] = True

    # def __init__(self, geometrie, nature_desc=None, icarrueid1: int = None, rue_nom1: str = None, commu_nom1=None,
    #              commu_ins1=None, icarrueid2: int = None,
    #              rue_nom2: str = None, commu_nom2=None, commu_ins2=None, gestion: str = None, voirie_nom: str = None,
    #              sens_bk=None, amenag=None, bron=None):
    def __init__(self, geometrie,
                 from_node, to_node,
                 pn_id_l, pn_id_r, nat_road_i,
                 lvl, morphology, admin, typology,
                 status, richting,
                 bron=None,
                 d_status=None,
                 d_morphology=None,
                 d_straatnaam_links=None,
                 d_straatnaam_rechts=None,
                 d_beheer=None
                 ):

        self.richting = richting
        self.nat_road_i = nat_road_i
        self.admin = admin
        self.pn_id_l = pn_id_l
        self.pn_id_r = pn_id_r
        self.typology = typology
        self.bron = bron
        Weg.initialize_oidns(bron)  # Set initial values based on bron
        self.legende = 8
        self.lbltype_wegverharding = None
        self.type_wegverharding = None
        self.wvoidn = None
        self.breedte = None
        self.wboidn = None
        self.nwoidn = None
        self.beginM = round(geometrie[0][0].M, 3)
        self.eindM = round(geometrie[-1][-1].M, 3)
        self.rijstroken_lblricht = None
        self.rijstroken_richting = None
        self.rijstroken_aantal = None
        self.rsoidn = None
        self.ident2 = None

        self.lstrnm = None
        self.lstrnmid = None
        self.rstrnm = None
        self.rstrnmid = None
        self.lblwegcat = None
        self.wegcat = None
        self.lblbeheer = None
        self.beheer = None
        self.geometrie = geometrie

        # WS_?IDN automatisch toewijzen en verhogen
        self.ws_oidn = Weg.ws_oidn
        self.ws_uidn = str(Weg.ws_oidn) + "_1"
        self.ws_gidn = str(Weg.ws_oidn) + "_1"
        Weg.ws_oidn += 1

        # Status toekennen
        self.status = int(status)
        self.lblstatus = d_status[self.status]

        self.morf = int(morphology) if morphology not in (130,) else -8
        self.lblmorf = d_morphology.get(int(morphology), "niet gekend").lower()

        self.set_wegcat()
        self.set_straatnaam(d_straatnaam_links, d_straatnaam_rechts)
        self.set_beheer(d_beheer)
        self.set_legende()

        # methode
        self.methode = 2
        self.lblmethod = "ingemeten"
        self.opndatum = "19500101T000000"
        self.begintijd = "19500101T000000"
        self.beginorg = "BG"
        self.lblbgnorg = "Brussels Gewest"
        self.tgbep = 1
        self.lbltgbep = "openbare weg"

        self.set_ident2()
        self.make_event_rijstrook()
        self.make_event_wegbreedte()
        self.make_event_wegverharding()

    def set_wegcat(self):
        wegcat = {
            '-8': 'niet gekend',
            '-9': 'niet van toepassing',
            'H': 'hoofdweg',
            'L': 'lokale weg',
            'L1': 'lokale weg type 1',
            'L2': 'lokale weg type 2',
            'L3': 'lokale weg type 3',
            'PI': 'primaire weg I',
            'PII': 'primaire weg II',
            'PII-1': 'primaire weg II type 1',
            'PII-2': 'primaire weg II type 2',
            'PII-4': 'primaire weg II type 4',
            'S': 'secundaire weg',
            'S1': 'secundaire weg type 1',
            'S2': 'secundaire weg type 2',
            'S3': 'secundaire weg type 3',
            'S4': 'secundaire weg type 4'
        }
        typologie_wegcat = {
            'A0': "H",
            'A0b': "H",
            "A1": "S",
            "A2": "S",
            "A3": "L1",
            "A4": "L2",
            "A5": "L3",
            "B1": "L3",
        }

        self.wegcat = typologie_wegcat.get(self.typology, -8)
        # Gebruik de morf code om de beschrijving te krijgen, of 'onbekend' als de code niet in de dictionary voorkomt
        self.lblwegcat = wegcat.get(self.wegcat, 'onbekend')

    def set_straatnaam(self, d_straatnaam_links, d_straatnaam_rechts):
        self.lstrnmid = int(self.pn_id_l.strip()) if self.pn_id_l and self.pn_id_l.strip().isdigit() else 0
        self.lstrnm = d_straatnaam_links.get(self.lstrnmid, "onbekend")
        self.rstrnmid = int(self.pn_id_r.strip()) if self.pn_id_r and self.pn_id_r.strip().isdigit() else 0
        self.rstrnm = d_straatnaam_rechts.get(self.rstrnmid, "onbekend")

    def set_beheer(self, d_beheer):
        self.beheer = self.admin
        self.lblbeheer = d_beheer.get(self.beheer, "onbekend")

    def set_legende(self):
        if self.lblmorf == 'dienstweg':
            self.legende = 8
        elif self.status == 'in aanbouw':
            self.legende = 14
        elif self.wegcat == 'L3':
            self.legende = 8

        legenda_mapping = {
            "in aanbouw": 14,  # status
            "dienstweg": 8,  # morf
            "dienstweg"
            "in- of uitrit van een dienst": 8,  # morf
            "veer": 12,  # morf
            "tramweg, niet toegankelijk voor andere voertuigen": 12,  # morf
            "aardeweg": 10,  # morf
            "wandel- of fietsweg, niet toegankelijk voor andere voertuigen": 9,  # morf
            "Particulier, privaat persoon of instelling": 10  # beheer
        }

        def legenda_mapping_awv_l(wegcat, beheer):
            if wegcat in ("L1", "OW") and "District" in beheer:
                return 5
            return None

        wegcat_waarden = {
            "H": 1, "EHW": 1, "VHW": 3, "P": 3, "PI": 3, "PII": 3, "PII-1": 3, "PII-2": 3, "PII-4": 3,
            "RW": 4, "IW": 4, "S": 4, "S1": 4, "S2": 4, "S3": 4, "S4": 4, 'OW': 6, "L": 8, "L2": 7, 'L1': 6, "L3": 8,
            "EW": 8,
            '-8': 8, '-9': 8
        }
        # Bepaal de legenda op basis van de mapping
        legende = (
                legenda_mapping.get(self.lblstatus) or
                legenda_mapping.get(self.lblbeheer) or
                legenda_mapping.get(self.lblmorf) or
                legenda_mapping_awv_l(self.wegcat, self.lblbeheer) or
                wegcat_waarden.get(self.wegcat) or
                0  # Standaardwaarde als alles None is
        )

    def set_ident2(self):
        pattern = r'^[A-Z]\d{1,3}[a-z]{0,1}$'
        if self.nat_road_i is not None and re.match(pattern, self.nat_road_i):
            self.ident2 = self.nat_road_i
            # NW_OIDN automatisch toewijzen en verhogen
            self.nwoidn = Weg.nw_oidn
            Weg.nw_oidn += 1

    def make_event_rijstrook(self):
        # print("make_event_rijstrook")
        # NW_OIDN automatisch toewijzen en verhogen
        self.rsoidn = Weg.rs_oidn
        Weg.rs_oidn += 1
        self.rijstroken_aantal = 1
        if self.richting == 2:
            self.rijstroken_richting = 1
            self.rijstroken_lblricht = "gelijklopend met de digitalisatiezin"
        if self.richting == 3:
            self.rijstroken_richting = 2
            self.rijstroken_lblricht = "tegengesteld aan de digitalisatiezin"
        else:
            self.rijstroken_richting = 1
            self.rijstroken_lblricht = "onafhankelijk van de digitalisatiezin"

    def make_event_wegbreedte(self):
        # print("make_event_wegbreedte")
        # WB_OIDN automatisch toewijzen en verhogen
        self.wboidn = Weg.wb_oidn
        Weg.wb_oidn += 1
        # self.rijstroken_aantal = 1
        self.breedte = -8

    def make_event_wegverharding(self):
        # print("make_event_wegverharding")
        # WV_OIDN automatisch toewijzen en verhogen
        self.wvoidn = Weg.wv_oidn
        Weg.wv_oidn += 1
        self.type_wegverharding = 1
        self.lbltype_wegverharding = "weg met vaste verharding"

    def export_wegsegment_as_list(self):
        attr_list = [self.geometrie, self.ws_oidn, self.ws_uidn, self.ws_gidn, self.status, self.lblstatus, self.morf,
                     self.lblmorf,
                     self.wegcat, self.lblwegcat, self.lstrnmid, self.lstrnm, self.rstrnmid, self.rstrnm, self.beheer,
                     self.lblbeheer, self.methode, self.lblmethod, self.opndatum, self.begintijd,
                     self.beginorg, self.lblbgnorg, self.tgbep, self.lbltgbep, self.legende, self.bron]
        return attr_list

    def export_nationweg_as_list(self):
        attr_list = [self.nwoidn, self.ws_oidn, self.ident2, self.begintijd, self.beginorg, self.lblbgnorg]
        return attr_list

    def export_rijstroken_as_list(self):
        attr_list = [self.rsoidn, self.ws_oidn, self.ws_gidn, self.rijstroken_aantal, self.rijstroken_richting,
                     self.rijstroken_lblricht, self.beginM, self.eindM, self.begintijd, self.beginorg, self.lblbgnorg]
        return attr_list

    def export_wegbreedte_as_list(self):
        attr_list = [self.wboidn, self.ws_oidn, self.ws_gidn, self.breedte,
                     self.beginM, self.eindM, self.begintijd, self.beginorg, self.lblbgnorg]
        return attr_list

    def export_wegverharding_as_list(self):
        attr_list = [self.wvoidn, self.ws_oidn, self.ws_gidn, self.type_wegverharding, self.lbltype_wegverharding,
                     self.beginM, self.eindM, self.begintijd, self.beginorg, self.lblbgnorg]
        return attr_list

