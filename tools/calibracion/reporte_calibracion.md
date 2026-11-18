# Reporte de calibración del diccionario ROS (2026-11-18)

Módulos: STKC007.fmt, fini018.fmt, WAPIDEMO.mmt

## Resumen

- Números de propiedad ROS encontrados: **257**
- Mapeados: **235**; pares (número, tipo de objeto) mapeados: 364 (alta 261, media 81, baja 16)
- Con significado distinto según el tipo de objeto: **6**
- Sin mapear: **22**

## Tipos de objeto

| Tipo ROS | Tipo API | Objetos alineados | Ejemplos |
|---|---|---|---|
| 3 | ALERT | 6 | AL_CONFIRMAR, AL_ERROR, AL_MESSAGE |
| 5 | ATT_LIB | 3 | LIB, LIB_TALO |
| 7 | BLOCK | 13 | BCHEQ, BCLIPROV, BCUO |
| 9 | GRAPHIC | 50 | GRAPHIC343, GRAPHIC345, LINE1 |
| 11 | CANVAS | 4 | CANVAS, CHEQUES, CV_CHEQUES |
| 13 | LV_COLMAP | 40 | BCO_CODIGO, BCO_DESC, CAST_BCO_CODIGO |
| 15 | RG_COLSPEC | 40 | BCO_CODIGO, BCO_DESC, CAST_BCO_CODIGO |
| 22 | FORM_MODULE | 2 | FINI018, STKC007 |
| 24 | FORM_PARAM | 84 | EMPR_CLI_CODIGO, EMPR_PROV_CODIGO, P_1 |
| 30 | ITEM | 249 | ACEPTAR, ART_DESC_ABREV, AUX_CLAVE |
| 36 | LOV | 14 | LOV_BANCO_PAGO, LOV_BCO, LOV_CLI |
| 38 | MENU_MODULE | 1 | WAPIDEMO |
| 40 | MENU | 5 | EDIT_MENU, FILE_MENU, HELP_MENU |
| 42 | MENU_ITEM | 18 | ABOUT_D2KWUTIL, COPY, COPY_SAMPLE_CODE |
| 58 | PROG_UNIT | 78 | CHECK_PACKAGE_FAILURE, CLEAR_ALL_MASTER_DETAILS, FP_BUSCA_CTACO_CAJA |
| 62 | RADIO_BUTTON | 2 | NO, SI |
| 64 | REC_GROUP | 14 | LOV_BANCO_PAGO, LOV_BCO, LOV_CLIENTE |
| 66 | RELATION | 1 | BDOCU_BDETA |
| 68 | TRIGGER | 158 | FORMULA-CALCULATION, KEY-CLRBLK, KEY-CLRFRM |
| 74 | VIS_ATTR | 9 | VA_FONDO_AMARILLO, VA_ROJO, VISUAL_BOTONES |
| 78 | WINDOW | 3 | WINDOW0, W_CHEQUES |
| 84 | NONE | 43 | CMPTXT10, CMPTXT100, CMPTXT13 |
| 86 | ACCESS_KEY | 43 | TEXTSTR101, TEXTSTR11, TEXTSTR14 |

## Cobertura de propiedades imprescindibles

| Objeto | Propiedad | Nº ROS | Confianza |
|---|---|---|---|
| FORM_MODULE | NAME | 211 | media |
| FORM_MODULE | TITLE | 307 | media |
| FORM_MODULE | FRST_NAVIGATION_BLK_NAM | 93 | media |
| FORM_MODULE | MNU_MOD | 97 | media |
| FORM_MODULE | CONSOLE_WIN | 59 | media |
| BLOCK | NAME | 211 | alta |
| BLOCK | DB_BLK | 528 | alta |
| BLOCK | QRY_DAT_SRC_TYP | 529 | alta |
| BLOCK | QRY_DAT_SRC_NAM | 522 | alta |
| BLOCK | WHERE_CLAUSE | 359 | alta |
| BLOCK | ORDR_BY_CLAUSE | 241 | alta |
| BLOCK | RECS_DISP_COUNT | 268 | alta |
| BLOCK | INSRT_ALLOWED | 134 | alta |
| BLOCK | UPDT_ALLOWED | 322 | alta |
| BLOCK | DEL_ALLOWED | 65 | alta |
| BLOCK | QRY_ALLOWED | 257 | alta |
| BLOCK | DML_DAT_TYP | 531 | alta |
| BLOCK | DML_DAT_NAM | 521 | manual |
| BLOCK | NXT_NAVIGATION_BLK_NAM | 218 | alta |
| BLOCK | PREV_NAVIGATION_BLK_NAM | 253 | alta |
| ITEM | NAME | 211 | alta |
| ITEM | ITM_TYP | 139 | alta |
| ITEM | DAT_TYP | 141 | alta |
| ITEM | MAX_LEN | 175 | alta |
| ITEM | REQUIRED | 283 | alta |
| ITEM | DB_ITM | 20 | alta |
| ITEM | COL_NAM | 344 | alta |
| ITEM | INIT_VAL | 751 | media |
| ITEM | LOV_NAM | 165 | media |
| ITEM | CNV_NAM | 33 | alta |
| ITEM | VISIBLE | 74 | alta |
| ITEM | ENABLED | 86 | alta |
| ITEM | PRMPT | 394 | media |
| ITEM | LABEL | 151 | alta |
| ITEM | FMT_MSK | 110 | alta |
| ITEM | COPY_VAL_FROM_ITM | 140 | media |
| ITEM | CALC_MODE | 331 | alta |
| ITEM | FORMULA | 477 | alta |
| ITEM | HINT | 124 | alta |
| ITEM | INSRT_ALLOWED | 134 | alta |
| ITEM | UPDT_ALLOWED | 322 | alta |
| ITEM | QRY_ALLOWED | 257 | alta |
| ITEM | CHKED_VAL | 42 | media |
| ITEM | UNCHKED_VAL | 321 | media |
| ITEM | PRMRY_KEY | 245 | alta |
| RELATION | NAME | 211 | media |
| RELATION | DETAIL_BLK | 68 | media |
| RELATION | JOIN_COND | 148 | media |
| RELATION | DEL_REC | 66 | media |
| LOV | NAME | 211 | alta |
| LOV | TITLE | 307 | alta |
| LOV | REC_GRP_NAM | 273 | alta |
| LV_COLMAP | NAME | 211 | alta |
| LV_COLMAP | TITLE | 307 | alta |
| LV_COLMAP | RTRN_ITM | 284 | alta |
| REC_GROUP | NAME | 211 | alta |
| REC_GROUP | REC_GRP_QRY | 275 | media |
| REC_GROUP | REC_GRP_TYP | 276 | alta |
| ALERT | NAME | 211 | alta |
| ALERT | ALT_MSG | — | **sin evidencia** |
| ALERT | ALT_STY | 11 | alta |
| ALERT | BTN_1_LBL | 6 | alta |
| ALERT | BTN_2_LBL | 7 | alta |
| ALERT | BTN_3_LBL | — | **sin evidencia** |
| FORM_PARAM | NAME | 211 | alta |
| FORM_PARAM | PARAM_DAT_TYP | 115 | alta |
| FORM_PARAM | PARAM_INIT_VAL | 116 | alta |
| FORM_PARAM | MAX_LEN | 175 | alta |
| TRIGGER | NAME | 211 | alta |
| TRIGGER | TRG_TXT | 464 | alta |
| TRIGGER | TRG_STY | — | **sin evidencia** |
| PROG_UNIT | NAME | 211 | alta |
| PROG_UNIT | PGU_TXT | 464 | alta |
| PROG_UNIT | PGU_TYP | — | **sin evidencia** |
| ATT_LIB | NAME | 211 | alta |
| ATT_LIB | LIB_LOC | 156 | alta |
| ATT_LIB | LIB_SRC | 157 | alta |
| WINDOW | NAME | 211 | alta |
| WINDOW | TITLE | 307 | alta |
| WINDOW | PRMRY_CNV | 370 | alta |
| CANVAS | NAME | 211 | alta |
| CANVAS | CNV_TYP | 45 | alta |
| CANVAS | WND_NAM | 367 | alta |
| MENU | NAME | 211 | alta |
| MENU_ITEM | NAME | 211 | alta |
| MENU_ITEM | LABEL | 151 | alta |
| MENU_ITEM | MNU_ITM_TYP | 184 | alta |
| MENU_ITEM | SUB_MNU_NAM | 704 | alta |
| MENU_ITEM | MNU_ITM_CODE | 464 | media |
| MENU_ITEM | COM_TYP | 56 | alta |

Imprescindibles sin evidencia: **4**. Significa que en ningún objeto de las muestras esa propiedad tiene un valor distinto del default, así que no aparece grabada en el .fmt. El parser asumirá el default de Forms y lo registrará; conviene calibrar con un módulo que la use.

## Mapeos con confianza media o baja

| Nº | Tipo ROS | Const | Muestras | Acierto / no-def / def-aus | Alternativas |
|---|---|---|---|---|---|
| 4 | 22 (FORM_MODULE) | ALERT | 2 | 1.0 / 1.0 / 0.5 |  |
| 9 | 3 (ALERT) | DFLT_ALT_BTN | 1 | 1.0 / 1.0 / 1.0 |  |
| 13 | 22 (FORM_MODULE) | ATT_LIB | 2 | 1.0 / 1.0 / 0.5 |  |
| 16 | 66 (RELATION) | PRVNT_MSTRLESS_OPS | 1 | 1.0 / 1.0 / 0.5 | SUBCL_SUBOBJ, SUBCL_OBJGRP, DIRTY_INFO |
| 19 | 3 (ALERT) | BACK_COLOR | 1 | 1.0 / 1.0 / 0.5 |  |
| 19 | 11 (CANVAS) | BACK_COLOR | 2 | 1.0 / 1.0 / 0.5 |  |
| 22 | 78 (WINDOW) | BEVEL | 1 | 1.0 / 1.0 / 1.0 |  |
| 27 | 22 (FORM_MODULE) | BLOCK | 2 | 1.0 / 1.0 / 0.5 |  |
| 32 | 22 (FORM_MODULE) | CANVAS | 2 | 1.0 / 1.0 / 0.5 |  |
| 42 | 30 (ITEM) | CHKED_VAL | 1 | 1.0 / 1.0 / 0.5 |  |
| 57 | 7 (BLOCK) | COMMENT | 1 | 1.0 / 1.0 / 0.5 |  |
| 57 | 22 (FORM_MODULE) | COMMENT | 1 | 1.0 / 1.0 / 0.5 |  |
| 59 | 22 (FORM_MODULE) | CONSOLE_WIN | 2 | 1.0 / 1.0 / 0.5 |  |
| 63 | 22 (FORM_MODULE) | CRSR_MODE | 1 | 1.0 / 1.0 / 1.0 | RUNTIME_COMP, VALIDATION_UNIT, ISOLATION_MODE |
| 64 | 66 (RELATION) | AUTO_QRY | 1 | 1.0 / 1.0 / 0.5 | PRVNT_MSTRLESS_OPS, SUBCL_SUBOBJ, SUBCL_OBJGRP |
| 66 | 66 (RELATION) | DEL_REC | 1 | 1.0 / 1.0 / 0.5 |  |
| 68 | 66 (RELATION) | DETAIL_BLK | 1 | 1.0 / 1.0 / 0.5 |  |
| 71 | 22 (FORM_MODULE) | DEFER_REQ_ENF | 2 | 1.0 / 0.0 / 0.5 | SUBCL_SUBOBJ, SUBCL_OBJGRP, SVPNT_MODE |
| 74 | 11 (CANVAS) | VISIBLE | 1 | 1.0 / 1.0 / 1.0 | SHOW_VERT_SCRLBR, RAISE_ON_ENT, WHITE_ON_BLACK |
| 76 | 11 (CANVAS) | SUBCL_SUBOBJ (inv.) | 1 | 1.0 / 0.0 / 1.0 | SHOW_HORZ_SCRLBR, RAISE_ON_ENT, WHITE_ON_BLACK |
| 87 | 68 (TRIGGER) | EXEC_HIERARCHY | 1 | 1.0 / 1.0 / 1.0 |  |
| 90 | 9 (GRAPHIC) | GRA_FONT_STY | 40 | 1.0 / 1.0 / 0.0 | GRA_FONT_COLOR_CODE, LIN_SPCING, LANG_DIR |
| 90 | 11 (CANVAS) | FONT_SIZ | 1 | 1.0 / 0.0 / 1.0 | FONT_STY, TAB_STY, PAR_MODSTR |
| 93 | 22 (FORM_MODULE) | FRST_NAVIGATION_BLK_NAM | 1 | 1.0 / 1.0 / 0.5 | FRST_NAVIGATION_BLK_OBJ |
| 97 | 22 (FORM_MODULE) | MNU_MOD | 2 | 1.0 / 1.0 / 0.5 |  |
| 103 | 3 (ALERT) | FONT_NAM | 1 | 1.0 / 1.0 / 0.5 |  |
| 104 | 3 (ALERT) | FONT_SIZ | 1 | 1.0 / 1.0 / 1.0 |  |
| 108 | 11 (CANVAS) | FORE_COLOR | 1 | 1.0 / 1.0 / 0.5 |  |
| 113 | 22 (FORM_MODULE) | FORM_PARAM | 2 | 1.0 / 1.0 / 0.5 |  |
| 114 | 30 (ITEM) | SIZING_STY | 7 | 1.0 / 0.0 / 1.0 | PRMPT_READING_ORDR, PAR_MODSTR, COMM_MODE |
| 114 | 74 (VIS_ATTR) | VAT_TYP | 7 | 1.0 / 0.0 / 1.0 | FRAME_TTL_FONT_SIZ, PAR_MODSTR, PAR_TYP |
| 121 | 62 (RADIO_BUTTON) | HEIGHT | 2 | 1.0 / 1.0 / 0.5 | PRMPT_DISP_STY |
| 125 | 78 (WINDOW) | MAXIMIZE_ALLOWED | 3 | 1.0 / 1.0 / 0.5 | SHOW_VERT_SCRLBR, SUBCL_SUBOBJ, WHITE_ON_BLACK |
| 132 | 78 (WINDOW) | INHRT_MNU | 1 | 1.0 / 1.0 / 1.0 | DIRTY_INFO, MV_ALLOWED, RESIZE_ALLOWED |
| 133 | 30 (ITEM) | ACCESS_KEY_STRID | 27 | 1.0 / 0.0 / 1.0 | SIZING_STY, PRMPT_READING_ORDR, PAR_MODSTR |
| 140 | 30 (ITEM) | COPY_VAL_FROM_ITM | 2 | 1.0 / 1.0 / 0.5 |  |
| 146 | 62 (RADIO_BUTTON) | LABEL_STRID | 2 | 1.0 / 1.0 / 0.5 |  |
| 148 | 66 (RELATION) | JOIN_COND | 1 | 1.0 / 1.0 / 0.5 |  |
| 151 | 62 (RADIO_BUTTON) | LABEL | 2 | 1.0 / 1.0 / 0.5 |  |
| 162 | 36 (LOV) | FLTR_BEFORE_DISP | 1 | 1.0 / 1.0 / 1.0 | DIRTY_INFO, AUTO_RFRSH, SUBCL_SUBOBJ |
| 164 | 22 (FORM_MODULE) | LOV | 2 | 1.0 / 1.0 / 0.5 |  |
| 165 | 30 (ITEM) | LOV_NAM | 17 | 0.941 / 1.0 / 0.5 |  |
| 168 | 30 (ITEM) | VALIDATE_FROM_LST | 1 | 1.0 / 1.0 / 1.0 | SUBCL_SUBOBJ, HIDE, WHITE_ON_BLACK |
| 174 | 38 (MENU_MODULE) | MAIN_MNU | 1 | 1.0 / 1.0 / 0.5 | MENU |
| 180 | 38 (MENU_MODULE) | MNU_FLNAM | 1 | 1.0 / 1.0 / 0.5 |  |
| 185 | 38 (MENU_MODULE) | MENU | 1 | 1.0 / 1.0 / 0.5 |  |
| 194 | 78 (WINDOW) | MODAL | 2 | 1.0 / 1.0 / 1.0 | RESIZE_ALLOWED, HIDE_ON_EXIT, CLS_ALLOWED |
| 211 | 22 (FORM_MODULE) | NAME | 2 | 1.0 / 1.0 / 0.5 |  |
| 211 | 38 (MENU_MODULE) | NAME | 1 | 1.0 / 1.0 / 0.5 | MNU_FLNAM |
| 211 | 62 (RADIO_BUTTON) | NAME | 2 | 1.0 / 1.0 / 0.5 | LABEL |
| 211 | 66 (RELATION) | NAME | 1 | 1.0 / 1.0 / 0.5 |  |
| 220 | 30 (ITEM) | NXT_NAVIGATION_ITM_NAM | 1 | 1.0 / 1.0 / 0.5 | CHAR_MODE_LOGICAL_ATTR |
| 247 | 22 (FORM_MODULE) | PROG_UNIT | 2 | 1.0 / 1.0 / 0.5 |  |
| 252 | 66 (RELATION) | DEFERRED | 1 | 1.0 / 1.0 / 0.5 | AUTO_QRY, PRVNT_MSTRLESS_OPS, SUBCL_SUBOBJ |
| 259 | 30 (ITEM) | QRY_ONLY | 2 | 1.0 / 1.0 / 1.0 | SHOW_VOLUME, UPDT_COMMIT, RENDERED |
| 262 | 30 (ITEM) | RAD_BUT | 1 | 1.0 / 1.0 / 0.5 |  |
| 264 | 62 (RADIO_BUTTON) | RDB_VAL | 2 | 1.0 / 1.0 / 0.5 |  |
| 269 | 7 (BLOCK) | RECS_FETCHED_COUNT | 1 | 1.0 / 1.0 / 1.0 | LOCK_MODE, QRY_DAT_SRC_TYP, DML_ARY_SIZ |
| 272 | 22 (FORM_MODULE) | REC_GRP | 2 | 1.0 / 1.0 / 0.5 |  |
| 275 | 64 (REC_GROUP) | REC_GRP_QRY | 14 | 0.929 / 1.0 / 0.5 |  |
| 280 | 7 (BLOCK) | REL | 1 | 1.0 / 1.0 / 0.5 |  |
| 281 | 78 (WINDOW) | HIDE_ON_EXIT | 1 | 1.0 / 1.0 / 1.0 | INHRT_MNU, DIRTY_INFO, MV_ALLOWED |
| 307 | 3 (ALERT) | TITLE | 2 | 1.0 / 1.0 / 0.5 |  |
| 307 | 22 (FORM_MODULE) | TITLE | 2 | 1.0 / 1.0 / 0.5 | MNU_MOD |
| 314 | 22 (FORM_MODULE) | TRIGGER | 2 | 1.0 / 1.0 / 0.5 |  |
| 321 | 30 (ITEM) | UNCHKED_VAL | 1 | 1.0 / 1.0 / 0.5 | INIT_VAL |
| 324 | 30 (ITEM) | UPDT_IF_NULL | 1 | 1.0 / 1.0 / 1.0 | SHOW_VOLUME, UPDT_COMMIT, RENDERED |
| 328 | 9 (GRAPHIC) | VAT_NAM | 1 | 1.0 / 1.0 / 1.0 | FRAME_TTL_VAT_NAM |
| 328 | 62 (RADIO_BUTTON) | VAT_NAM | 2 | 1.0 / 1.0 / 0.5 | VAT_OBJ |
| 355 | 22 (FORM_MODULE) | VIS_ATTR | 2 | 1.0 / 1.0 / 0.5 |  |
| 361 | 62 (RADIO_BUTTON) | WIDTH | 2 | 1.0 / 1.0 / 0.5 |  |
| 363 | 22 (FORM_MODULE) | WINDOW | 2 | 1.0 / 1.0 / 0.5 |  |
| 366 | 3 (ALERT) | TITLE_STRID | 2 | 1.0 / 1.0 / 1.0 |  |
| 366 | 22 (FORM_MODULE) | TITLE_STRID | 2 | 1.0 / 1.0 / 0.5 |  |
| 369 | 78 (WINDOW) | WIN_STY | 1 | 1.0 / 1.0 / 1.0 |  |
| 372 | 62 (RADIO_BUTTON) | X_POS | 2 | 1.0 / 1.0 / 0.5 |  |
| 373 | 62 (RADIO_BUTTON) | Y_POS | 2 | 1.0 / 1.0 / 0.5 |  |
| 389 | 9 (GRAPHIC) | ARROW_STY | 2 | 1.0 / 1.0 / 1.0 | GRA_FONT_WGHT, GRA_FONT_SPCING, GRA_TEXT_STRID |
| 394 | 30 (ITEM) | PRMPT | 62 | 0.968 / 1.0 / 0.5 |  |
| 438 | 9 (GRAPHIC) | GRA_FONT_COLOR_CODE | 40 | 0.925 / 1.0 / 0.0 | CLIP_HGT, FRAME_TTL_FONT_SIZ, FRAME_TTL_SPCING |
| 448 | 9 (GRAPHIC) | LANG_DIR | 37 | 1.0 / 1.0 / 1.0 | CSTM_SPCING, VERT_JST, GRA_FONT_COLOR_CODE |
| 454 | 9 (GRAPHIC) | SHOW_SCRLBR | 37 | 1.0 / 0.0 / 1.0 | SUBCL_OBJGRP, SUBCL_SUBOBJ, ALLOW_STRT_ATT_PRMPTS |
| 458 | 9 (GRAPHIC) | CSTM_SPCING | 37 | 1.0 / 1.0 / 1.0 | VERT_JST, GRA_FONT_COLOR_CODE, CLIP_HGT |
| 464 | 42 (MENU_ITEM) | MNU_ITM_CODE | 8 | 1.0 / 0.875 / 0.5 |  |
| 465 | 42 (MENU_ITEM) | LONGITUD_CODIGO | 12 | 1.0 / 1.0 / 1.0 |  |
| 465 | 58 (PROG_UNIT) | LONGITUD_CODIGO | 78 | 1.0 / 1.0 / 1.0 |  |
| 465 | 68 (TRIGGER) | LONGITUD_CODIGO | 158 | 1.0 / 1.0 / 1.0 |  |
| 470 | 22 (FORM_MODULE) | NEWDEFER_REQ_ENF | 2 | 1.0 / 0.0 / 0.5 |  |
| 480 | 30 (ITEM) | ITMS_DISP | 13 | 0.923 / 1.0 / 1.0 | OLE_RESIZ_STY, CHK_BX_OTHER_VALS, PRMPT_DISP_STY |
| 521 | 7 (BLOCK) | DML_DAT_NAM | 5 | 1.0 / 1.0 / 1.0 |  |
| 530 | 7 (BLOCK) | QRY_ALL_RECS | 1 | 1.0 / 1.0 / 1.0 | DIRTY_INFO, LST_IN_BLK_MNU, UPDT_CHANGED_COLS |
| 535 | 30 (ITEM) | TOOLTIP_VAT_GRP | 1 | 1.0 / 1.0 / 0.5 | TBP_NAM |
| 577 | 22 (FORM_MODULE) | REFERENCIAS_COMPILADAS | 2 | 1.0 / 1.0 / 1.0 |  |
| 629 | 68 (TRIGGER) | FIRE_IN_QRY | 79 | 0.987 / 0.0 / 1.0 | SUBCL_SUBOBJ, SUBCL_OBJGRP |
| 675 | 38 (MENU_MODULE) | SHARE_LIB | 1 | 1.0 / 1.0 / 0.5 | SUBCL_SUBOBJ, SUBCL_OBJGRP, USE_SECURITY |
| 717 | 22 (FORM_MODULE) | RUNTIME_COMP | 2 | 1.0 / 1.0 / 0.5 | VALIDATION_UNIT, ISOLATION_MODE, PAR_MODSTR |
| 717 | 38 (MENU_MODULE) | ROLE_COUNT | 1 | 1.0 / 0.0 / 0.5 | PAR_MODSTR, PAR_TYP, PAR_MODTYP |
| 736 | 22 (FORM_MODULE) | VALIDATION_UNIT | 2 | 1.0 / 0.0 / 0.5 | ISOLATION_MODE, PAR_MODSTR, MNU_STY |
| 751 | 30 (ITEM) | INIT_VAL | 30 | 0.967 / 1.0 / 0.0 |  |
| 754 | 24 (FORM_PARAM) | PARAM_INIT_VAL_NORMALIZADO | 15 | 1.0 / 1.0 / 1.0 |  |
| 815 | 22 (FORM_MODULE) | DIRTY_INFO | 2 | 1.0 / 1.0 / 0.5 | USE_3D_CNTRLS, SVPNT_MODE, SUBCL_OBJGRP |
| 815 | 38 (MENU_MODULE) | DIRTY_INFO | 1 | 1.0 / 1.0 / 0.5 | SUBCL_SUBOBJ, SUBCL_OBJGRP, USE_SECURITY |
| 815 | 62 (RADIO_BUTTON) | DIRTY_INFO | 2 | 1.0 / 1.0 / 0.5 | VISIBLE, ENABLED, WHITE_ON_BLACK |

## Números ROS sin mapear

| Nº | Clase | Tipos ROS | Ejemplos |
|---|---|---|---|
| 21 | N | 3, 9, 11, 30, 74 | AL_CONFIRMAR: 196; LINE1: 41; RECT2: 78 |
| 55 | T | 42 | EXIT_API_DEMO_FORM: NULLP; COPY_SAMPLE_CODE: NULLP; GENERATED_CODE: NULLP |
| 196 | N | 22, 38 | STKC007: 377; FINI018: 798; WAPIDEMO: 20 |
| 348 | P | 22 |  |
| 349 | P | 11 |  |
| 356 | O | 11 | CANVAS: 384; CANVAS: 369; CHEQUES: 377 |
| 382 | N | 3, 30, 74, 86 | AL_CONFIRMAR: 31; W_DOCU_TIT1: 31; W_DOCU_TIT2: 31 |
| 440 | N | 9 | LINE1: 0; RECT2: 0; TEXT3: 0 |
| 442 | N | 9 | LINE1: 255; RECT2: 1; TEXT3: 255 |
| 467 | N | 58 | PP_CARGAR_DATOS: 128; PP_CONSTRUIR_WHERE: 128; PP_FORMAT_MASK: 128 |
| 468 | B | 22 | STKC007: 1; FINI018: 0 |
| 469 | N | 22 | STKC007: 1; FINI018: 7 |
| 471 | N | 22 | STKC007: 8; FINI018: 7 |
| 472 | N | 22 | STKC007: 17; FINI018: 14 |
| 474 | N | 22 | STKC007: 96; FINI018: 96 |
| 475 | N | 22 | STKC007: 96; FINI018: 96 |
| 498 | T | 30 | W_CLAVE_RESPALDO: ; R_EXCEL: ; DOCU_GRAV_NETO_MON:  |
| 623 | N | 30 | W_CLAVE_RESPALDO: 31; DOCU_SUC_AUX: 31; DOCU_DEP_AUX: 31 |
| 727 | N | 38 | WAPIDEMO: 16 |
| 738 | T | 22, 38 | STKC007: E; FINI018: E; WAPIDEMO: E |
| 739 | N | 22, 38 | STKC007: 31; FINI018: 31; WAPIDEMO: 31 |
| 747 | O | 22, 38 | STKC007: 2; FINI018: 2; WAPIDEMO: 2 |
