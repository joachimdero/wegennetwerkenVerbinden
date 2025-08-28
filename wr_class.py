import re
import traceback

import arcpy.da


class Weg:
    ws_oidn = 0
    nw_oidn = 0
    rs_oidn = 0
    wb_oidn = 0
    wv_oidn = 0
    strnmid = 0
    initialized = {'VLA': False, 'WAL': False, 'GRENS': False}

    @classmethod
    def initialize_oidns(cls, bron):
        if not cls.initialized.get(bron, False):
            if bron == 'WAL':
                cls.ws_oidn = cls.nw_oidn = cls.rs_oidn = cls.wb_oidn = cls.wv_oidn = cls.strnmid = 200000000
            elif bron == 'GRENS':
                cls.ws_oidn = cls.nw_oidn = cls.rs_oidn = cls.wb_oidn = cls.wv_oidn = cls.strnmid = 300000000
            else:
                cls.ws_oidn = cls.nw_oidn = cls.rs_oidn = cls.wb_oidn = cls.wv_oidn = cls.strnmid = 0  # default value if bron is unknown
            cls.initialized[bron] = True

    def __init__(self, geometrie, nature_desc=None, icarrueid1: int = None, rue_nom1: str = None, commu_nom1=None,
                 commu_ins1=None, icarrueid2: int = None,
                 rue_nom2: str = None, commu_nom2=None, commu_ins2=None, gestion: str = None, voirie_nom: str = None,
                 sens_bk=None, amenag=None, bron=None):

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
        self.rstrnm = None
        self.rstrnmid = None
        self.lstrnm = None
        self.lstrnmid = None
        self.lblwegcat = None
        self.wegcat = None
        self.lblbeheer = None
        self.beheer = None
        self.geometrie = geometrie
        self.nature_desc = nature_desc
        self.icarrueid1 = icarrueid1
        self.rue_nom1 = rue_nom1
        self.commu_nom1 = commu_nom1
        self.commu_ins1 = commu_ins1
        self.icarrueid2 = icarrueid2
        self.rue_nom2 = rue_nom2
        self.commu_nom2 = commu_nom2
        self.commu_ins2 = commu_ins2
        self.gestion = gestion
        self.voirie_nom = voirie_nom
        self.sens_bk = sens_bk
        self.amenag = amenag

        # WS_?IDN automatisch toewijzen en verhogen
        self.ws_oidn = Weg.ws_oidn
        self.ws_uidn = str(Weg.ws_oidn) + "_1"
        self.ws_gidn = str(Weg.ws_oidn) + "_1"
        Weg.ws_oidn += 1

        # Status toekennen
        self.status = 4
        self.lblstatus = "in gebruik"

        # Initieer morf met een standaardwaarde
        self.morf = -8  # of een andere logische standaardwaarde
        self.lblmorf = 'onbekend'
        self.set_morfologie()

        self.set_wegcat()
        self.set_straatnaam()
        self.set_beheer()
        self.set_legende()

        # methode
        self.methode = 2
        self.lblmethod = "ingemeten"
        self.opndatum = "19500101T000000"
        self.begintijd = "19500101T000000"
        self.beginorg = "SPW"
        self.lblbgnorg = "Service public de Wallonie"
        self.tgbep = 1
        self.lbltgbep = "openbare weg"

        self.set_ident2()
        self.make_event_rijstrook()
        self.make_event_wegbreedte()
        self.make_event_wegverharding()

    def set_morfologie(self):
        morfologie = {
            101: 'autosnelweg',
            102: 'weg met gescheiden rijbanen die geen autosnelweg is',
            103: 'weg bestaande uit één rijbaan',
            104: 'rotonde',
            105: 'speciale verkeerssituatie',
            106: 'verkeersplein',
            107: 'op- of afrit, behorende tot een niet-gelijkgrondse verbinding',
            108: 'op- of afrit, behorende tot een gelijkgrondse verbinding',
            109: 'parallelweg',
            110: 'ventweg',
            111: 'in- of uitrit van een parking',
            112: 'in- of uitrit van een dienst',
            113: 'voetgangerszone',
            114: 'wandel- of fietsweg, niet toegankelijk voor andere voertuigen',
            116: 'tramweg, niet toegankelijk voor andere voertuigen',
            120: 'dienstweg',
            125: 'aardeweg',
            130: 'veer'
        }

        pattern = r'^[A-Z]\d{7}$'
        if self.nature_desc == 'Autoroute':
            if len(self.voirie_nom) == 7 and re.match(pattern, self.voirie_nom):
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
        self.lblmorf = morfologie.get(self.morf, 'onbekend')

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

        if self.nature_desc == 'Autoroute':
            self.wegcat = "H"
        elif self.nature_desc == 'Ring':
            if len(self.voirie_nom) == 2:
                self.wegcat = "H"
            elif self.voirie_nom[2] != 0:
                self.wegcat = "H"
        elif self.voirie_nom not in ("", " "):
            self.wegcat = "S"
        else:
            self.wegcat = "L"

        # Gebruik de morf code om de beschrijving te krijgen, of 'onbekend' als de code niet in de dictionary voorkomt
        self.lblwegcat = wegcat.get(self.wegcat, 'onbekend')

    def set_straatnaam(self):
        if self.icarrueid1 != 0:
            # icarrueid1 is uniek in combi met rue_nom1
            self.lstrnmid = self.icarrueid1
            self.lstrnm = self.rue_nom1
        else:
            self.lstrnmid = -9
            self.lstrnm = ""
        if self.icarrueid2 != 0 and self.icarrueid2 is not None:
            self.rstrnmid = self.icarrueid2 + self.strnmid
            self.rstrnm = self.rue_nom2
        elif self.icarrueid1 != 0 and self.icarrueid1 is not None:
            self.rstrnmid = self.icarrueid1 + self.strnmid
            self.rstrnm = self.rue_nom1
        else:
            self.rstrnmid = -9
            self.rstrnm = ""

    def set_beheer(self):
        if self.gestion == 'Service public de Wallonie':
            self.beheer = "SPW"
            self.lblbeheer = 'Service public de Wallonie'
        elif self.gestion == 'Commune':
            self.beheer = self.commu_ins1
            self.lblbeheer = f"gemeente {self.commu_nom1}"
        else:
            self.beheer = -8
            self.lblbeheer = "niet gekend"

    def set_legende(self):
        if self.lblmorf == 'dienstweg':
            self.legende = 8
        elif self.status == 'in aanbouw':
            self.legende = 14
        elif self.lblmorf == 'in- of uitrit van een dienst':
            self.legende = 8
        elif self.lblmorf == 'tramweg, niet toegankelijk voor andere voertuigen':
            self.legende = 12
        elif self.lblmorf == 'veer':
            self.legende = 12
        elif self.lblmorf == 'aardeweg':
            self.legende = 10
        elif self.lblmorf == 'wandel- of fietsweg, niet toegankelijk voor andere voertuigen':
            self.legende = 9
        elif self.wegcat == 'L3':
            self.legende = 8
        elif self.wegcat == 'L2':
            self.legende = 7
        elif self.wegcat == 'L1' and not 'AWV' in self.beheer:
            self.legende = 6
        elif self.wegcat == 'L1' and 'AWV' in self.beheer:
            self.legende = 5
        elif 'S' in self.wegcat:
            self.legende = 4
        elif 'P' in self.wegcat:
            self.legende = 3
        elif self.wegcat == 'H':
            self.legende = 1

    def set_ident2(self):
        pattern = r'^[A-Z]\d{1,3}[a-z]{0,1}$'
        if self.voirie_nom is not None and re.match(pattern, self.voirie_nom):
            self.ident2 = self.voirie_nom
            # NW_OIDN automatisch toewijzen en verhogen
            self.nwoidn = Weg.nw_oidn
            Weg.nw_oidn += 1

    def make_event_rijstrook(self):
        # print("make_event_rijstrook")
        # NW_OIDN automatisch toewijzen en verhogen
        self.rsoidn = Weg.rs_oidn
        Weg.rs_oidn += 1
        self.rijstroken_aantal = 1
        if self.sens_bk in ("C", "D"):
            self.rijstroken_richting = 1
            self.rijstroken_lblricht = "gelijklopend met de digitalisatiezin"
        else:
            self.rijstroken_richting = 3
            self.rijstroken_lblricht = "onafhankelijk van de digitalisatiezin"

    def make_event_wegbreedte(self):
        # print("make_event_wegbreedte")
        # WB_OIDN automatisch toewijzen en verhogen
        self.wboidn = Weg.wb_oidn
        Weg.wb_oidn += 1
        self.rijstroken_aantal = 1
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


if __name__ == "__main__":
    # nodige velden uit input fc
    f_names = [
        'SHAPE@',
        'NATUR_DESC',  # type weg
        'ICARRUEID1', 'RUE_NOM1', 'COMMU_NOM1', 'COMMU_INS1',  # straatnaaminfo
        'ICARRUEID2', 'RUE_NOM2', 'COMMU_NOM2', 'COMMU_INS2',  # straatnaaminfo
        'GESTION',  # beheerder
        'VOIRIE_NOM',  # wegnummer
        'SENS_BK',  # rijrichting
        'AMENAG',  # rondpunt
    ]

    in_fc = "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten " \
            "verbinden\\wegennettenVerbinden2.gdb\\Wallonie_tmp3dissolve"
    with arcpy.da.SearchCursor(in_fc, f_names) as sc:
        i = 0
        for row in sc:
            i += 1
            if i > 5:
                break
            try:
                row_new = Weg(*row).export_wegsegment_as_list()
                print(f"row_new: {row_new}")
            except Exception as e:
                print(f"An error occurred: {row}")
                print(traceback.format_exc())
                break
