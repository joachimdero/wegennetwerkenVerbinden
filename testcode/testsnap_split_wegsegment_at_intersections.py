from wegennetwerkWallonieToWrvorm import snap_split_wegsegment_at_endpoint

in_wegsegmenten = r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\wegennetten " \
                  r"verbinden\wegennettenVerbinden3.gdb\wegsegmentWallonie_tmp6copySnap"

if __name__ == '__main__':
    snap_split_wegsegment_at_endpoint(in_wegsegmenten, "test_intersection")