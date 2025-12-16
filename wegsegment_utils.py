"""
wegsegment_utils.py
-----------
Hulpfuncties en state-tracking voor de Weg-klasse.
"""


class OidnManager:
    """
    Houdt counters bij voor WS/NW/RS/WB/WV en STRNMID, afhankelijk van de bron.
    """
    _initialized = {'VLA': False, 'WAL': False, 'BRU': False, 'GRENS': False}
    ws_oidn = nw_oidn = rs_oidn = wb_oidn = wv_oidn = strnmid = 0

    @classmethod
    def initialize_oidns(cls, bron):
        """Initialiseer counters per bron, enkel bij eerste gebruik."""
        if not cls._initialized.get(bron, False):
            if bron == 'WAL':
                start = 200000000
            elif bron == 'GRENS':
                start = 300000000
            elif bron == 'BRU':
                start = 400000000
            else:
                start = 0  # default

            cls.ws_oidn = cls.nw_oidn = cls.rs_oidn = cls.wb_oidn = cls.wv_oidn = cls.strnmid = start
            cls._initialized[bron] = True
