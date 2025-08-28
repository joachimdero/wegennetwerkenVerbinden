class Wegknoop:
    # input is [x,y],[wsoidn1,wsoidn2,...]
    wk_oidn = None
    initialized = {'VLA': False, 'WAL': False, 'GRENS': False, 'BRU': False}

    @classmethod
    def initialize_oidns(cls, bron):
        if not cls.initialized.get(bron, False):
            if bron == 'WAL':
                cls.wk_oidn = 200000000
            elif bron == 'GRENS':
                cls.wk_oidn = 300000000
            elif bron == 'BRU':
                cls.wk_oidn = 400000000
            else:
                cls.wk_oidn = 0  # default value if bron is unknown
            cls.initialized[bron] = True

    def __init__(self, geometry, wsoidn_lijst, bron):
        self.bron = bron
        Wegknoop.initialize_oidns(bron=bron)
        self.type = None
        self.lbltype = None
        self.wsoidn_lijst = wsoidn_lijst
        self.geometry = geometry
        self.set_lbltype()
        # WS_?IDN automatisch toewijzen en verhogen
        self.wk_oidn = Wegknoop.wk_oidn
        self.wk_uidn = str(Wegknoop.wk_oidn) + "_1"
        Wegknoop.wk_oidn += 1

        self.begintijd = "19500101T000000"
        if self.bron == "WAL":
            self.beginorg = "SPW"
            self.lblbgnorg = "Service public de Wallonie"
        elif self.bron == "BRU":
            self.beginorg = "BG"
            self.lblbgnorg = "Brussels Gewest"

        self.export_attr_as_list

    def set_lbltype(self):
        if len(self.wsoidn_lijst) == 1:
            self.type = 1
            self.lbltype = "eindknoop"
        elif len(self.wsoidn_lijst) == 2:
            self.type = 2
            self.lbltype = "schijnknoop"
        elif len(self.wsoidn_lijst) > 2:
            self.type = 3
            self.lbltype = "echte knoop"

    def export_attr_as_list(self):
        attr_list = [self.geometry, self.wk_oidn, self.wk_uidn, self.type, self.lbltype, self.begintijd,
                     self.beginorg, self.lblbgnorg]
        # print (attr_list)
        return attr_list


if __name__ == "__main__":
    attr_list = Wegknoop((193873.84799999744, 161419.95800000057), [200000000, 2]).export_attr_as_list()
    # print (attr_list)
