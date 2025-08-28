import arcpy

from selectieSegmentdelenWegenregister_functions import selectie_wegsegment_en_knopen, splits_segmenten, \
    maak_nieuwe_fc_segmenten, maak_nieuwe_fc_knopen, test_wegknopen, edit_begin_eindknoop, maak_nieuwe_atttables

arcpy.env.overwriteOutput = True
arcpy.env.workspace = "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten " \
                      "verbinden\\wegennettenVerbinden3.gdb"

# ------------------------------------------------------------


if __name__ == '__main__':
    arcpy.env.workspace = "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten " \
                          "verbinden\\wegennettenVerbinden3.gdb"
    in_wegsegmenten = "Wegsegment_input"
    # in_wegsegmenten = r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\wegennetten verbinden\wegennettenVerbinden3.gdb\wr_wegsegment_testselectie_input"
    vlaanderen = "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten verbinden\\wegennetten verbinden.gdb\\AdmEenhGemeentenVoorlRefBestand2019"

    in_wegknopen = "Wegknoop_input"
    # in_wegknopen = r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Projecten\WRapp\wegennetten verbinden\wegennettenVerbinden3.gdb\wr_wegknoop_testselectie_input"
    wbn = r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Gedeeld\GISdata\grb.gdb\Wbn"
    knw = r"C:\GoogleTeamAim\Team AIM\Team AIM\Data beheer\Gedeeld\GISdata\grb.gdb\Knw_1"

    vlaanderen = arcpy.Dissolve_management(vlaanderen, "Vlaanderen_dissolve")
    # wbn_knw_resultaat = maak_gebied(wbn, knw, vlaanderen)
    wbn_knw_resultaat = "C:\\GoogleTeamAim\\Team AIM\\Team AIM\\Data beheer\\Projecten\\WRapp\\wegennetten verbinden\\wegennettenVerbinden3.gdb\\wbn_knw_vlaanderen_resultaat"

    wsoidn_uit_vlaanderen_b, wsoidn_uit_vlaanderen_e, wegsegment_te_splitsen_fc, wegknopen_lyr = selectie_wegsegment_en_knopen(
        wegsegmenten=in_wegsegmenten,
        wegknopen=in_wegknopen,
        vlaanderen=vlaanderen
    )

    wegsegmenten_split_verwijderen, wegknopen_verplaatst = splits_segmenten(
        wegsegmenten=in_wegsegmenten,
        vlaanderen=vlaanderen,
        wsoidn_uit_vlaanderen_b=wsoidn_uit_vlaanderen_b,
        wsoidn_uit_vlaanderen_e=wsoidn_uit_vlaanderen_e,
        wegsegment_te_splitsen_fc=wegsegment_te_splitsen_fc,
        knopen_uit_vlaanderen=wegknopen_lyr
    )

    segmenten_resultaat = maak_nieuwe_fc_segmenten(
        wegsegmenten=in_wegsegmenten,
        wegsegmenten_split_verwijderen=wegsegmenten_split_verwijderen,
        wegknopen_verplaatst=wegknopen_verplaatst
    )

    wegknopen_resultaat, wegknopen_duplicate = maak_nieuwe_fc_knopen(
        wegknopen=in_wegknopen,
        knopen_nieuw=wegknopen_verplaatst,
        wegsegmenten_split_verwijderen=wegsegmenten_split_verwijderen
    )

    # bij ERASE verschuift het segment soms waardoor het niet meer aansluit bij het gecreëerde punt
    arcpy.edit.Snap(
        in_features=segmenten_resultaat,
        snap_environment=f"{wegknopen_resultaat} END '1 Centimeters'"
    )

    edit_begin_eindknoop(segmenten_resultaat, wegknopen_duplicate, wegknopen_resultaat)

    test_wegknopen(
        wegknopen=wegknopen_resultaat,
        wegsegmenten=segmenten_resultaat
    )
    maak_nieuwe_atttables(
        wegsegment=segmenten_resultaat,
        atttables=[
            "AttWegbreedte_input",
            "AttEuropweg_input",
            "AttGenumweg_input",
            "AttNationweg_input",
            "AttRijstroken_input",
            "AttWegverharding_input"
        ]
    )

