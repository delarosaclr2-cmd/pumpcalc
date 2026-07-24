# Formula Inventory

**Total formulas:** 382
**Total constants:** 1263

## Sheet: `CAIDA PRESION DE TUBERIA` (17 formulas)

| Cell | Formula | Named Ranges | Sheet Refs | Constants | Functions | Format |
|------|---------|--------------|------------|-----------|-----------|--------|
| V5 | `=G5` |  |  |  |  | General |
| G8 | `=G7*(G5/G6)^0.5` |  |  | 0.5 |  | 0.0 |
| V8 | `=V7*(V5/V6)^0.5` |  |  | 0.5 |  | 0.0 |
| G9 | `=VLOOKUP(A20,OUTPIPES,6,FALSE)` | OUTPIPE; OUTPIPES |  | 6.0 | VLOOKUP | General |
| V9 | `=VLOOKUP(B20,INPIPE,6,FALSE)` | INPIPE |  | 6.0 | VLOOKUP | General |
| G10 | `=VLOOKUP(A20,OUTPIPES,7,FALSE)` | OUTPIPE; OUTPIPES |  | 7.0 | VLOOKUP | General |
| V10 | `=VLOOKUP(B20,INPIPE,7,FALSE)` | INPIPE |  | 7.0 | VLOOKUP | General |
| G11 | `=50.6*G5*G9/(G8*G10)` |  |  | 50.6 |  | #,##0.00 |
| V11 | `=50.6*V5*V9/(V8*V10)` |  |  | 50.6 |  | #,##0.00 |
| G14 | `=VLOOKUP(A21,RUGOSIDAD,3)` | RUGOSIDAD |  | 3.0 | VLOOKUP | 0.00000 |
| V14 | `=VLOOKUP(B21,RUGOSIDAD,3)` | RUGOSIDAD |  | 3.0 | VLOOKUP | 0.00000 |
| G15 | `=G14/(G12/12)` |  |  | 4.0; 2.0; 12.0 |  | 0.00000 |
| V15 | `=V14/(V12/12)` |  |  | 4.0; 2.0; 12.0 |  | 0.00000 |
| G16 | `=VLOOKUP(A20,OUTPIPES,8,FALSE)` | OUTPIPE; OUTPIPES |  | 8.0 | VLOOKUP | 0.00000 |
| V16 | `= 64/V11` |  |  | 64.0 |  | 0.00000 |
| G19 | `=(((G17*G16*G9*(G5^2))/(G8^5))*2.3071)*G18` |  |  | 7.0; 6.0; 2.0; 5.0; 2.3071; 8.0 |  | 0.0000000 |
| V19 | `=(((V17*V16*V9*(V5^2))/(V8^5))*2.3071)*V18` |  |  | 7.0; 6.0; 2.0; 5.0; 2.3071; 8.0 |  | 0.0000000 |

## Sheet: `CALCULO DE BOMBA` (26 formulas)

| Cell | Formula | Named Ranges | Sheet Refs | Constants | Functions | Format |
|------|---------|--------------|------------|-----------|-----------|--------|
| C4 | `=VLOOKUP('CAIDA PRESION DE TUBERIA'!A20,OUTPIPES,2,FALSE)` | OUTPIPE; OUTPIPES | CAIDA PRESION DE TUBERIA | 2.0 | VLOOKUP | General |
| E4 | `='CAIDA PRESION DE TUBERIA'!G5` |  | CAIDA PRESION DE TUBERIA |  |  | 0.00 |
| E5 | `='CAIDA PRESION DE TUBERIA'!G9` |  | CAIDA PRESION DE TUBERIA |  |  | General |
| E6 | `='CAIDA PRESION DE TUBERIA'!G10` |  | CAIDA PRESION DE TUBERIA |  |  | General |
| C8 | `=14.7` |  |  | 14.7 |  | 0.00 |
| C9 | `=500/304.8` |  |  | 500.0; 304.8 |  | 0.00 |
| E9 | `=VLOOKUP(A32,presionvapor,4,FALSE)` | presionvapor |  | 2.0; 4.0 | VLOOKUP | 0.00 |
| C11 | `='TABLA DE ACCESORIOS SUCCION'!I40` | SUCCION | TABLA DE ACCESORIOS SUCCION |  |  | 0.0000 |
| E11 | `=VLOOKUP(A32,gravedadespecifica,5,FALSE)` | gravedadespecifica |  | 2.0; 5.0 | VLOOKUP | 0.00 |
| C12 | `=2.12*3.281` |  |  | 2.12; 3.281 |  | 0.00 |
| C13 | `='CAIDA PRESION DE TUBERIA'!V19` |  | CAIDA PRESION DE TUBERIA | 9.0 |  | 0.00000 |
| C14 | `=C12*C13` |  |  | 2.0; 3.0 |  | 0.0000 |
| E14 | `=((C8+E8)*(2.31/E11))+C9-C11-C14-E9` |  |  | 2.31; 4.0 |  | 0.00 |
| E20 | `=(E4*C28*E11)/3960` |  |  | 8.0; 3960.0 |  | 0.00 |
| C21 | `=C20-C9` |  |  |  |  | 0.00 |
| E21 | `=E20/C22` |  |  | 2.0 |  | 0.00 |
| E22 | `=E21*0.7456` |  |  | 0.7456 |  | 0.00 |
| E23 | `=(E21*5252)/1700` |  |  | 5252.0; 1700.0 |  | 0.00 |
| C24 | `='TABLA DE ACCESORIOS DESCARGA'!I41` | DESCARGA | TABLA DE ACCESORIOS DESCARGA |  |  | 0.000 |
| E24 | `=C28*0.3048` |  |  | 8.0; 0.3048 |  | 0.00 |
| C25 | `=RAMALES!F18` |  |  | 8.0 |  | 0.00 |
| E25 | `=E4*3.7854` |  |  | 3.7854 |  | 0.00 |
| C26 | `=RAMALES!F19` |  |  | 9.0 |  | 0.00 |
| E27 | `=(C29*(E4^0.5))/(E24^0.75)` |  |  | 9.0; 0.5; 4.0; 0.75 |  | 0.00 |
| C28 | `=C11+C14+C21+C24+C26` |  |  | 4.0; 4.0; 6.0 |  | 0.00 |
| E29 | `=VLOOKUP(A34,TIPOIMPULSOR,3,FALSE)` | TIPOIMPULSOR |  | 4.0; 3.0 | VLOOKUP | 0.00 |

## Sheet: `TABLA DE ACCESORIOS DESCARGA` (119 formulas)

| Cell | Formula | Named Ranges | Sheet Refs | Constants | Functions | Format |
|------|---------|--------------|------------|-----------|-----------|--------|
| D7 | `=VLOOKUP(K3,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G7 | `=VLOOKUP(K3,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I7 | `=((D7*F7)*($H$2^2)/(32.4*2))*H7` |  |  | 2.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D8 | `=VLOOKUP(K4,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G8 | `=VLOOKUP($K$4,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0; 4.0 | VLOOKUP | 0.00 |
| I8 | `=((D8*F8)*($H$2^2)/(32.4*2))*H8` |  |  | 2.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D9 | `=VLOOKUP(K5,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G9 | `=VLOOKUP(K5,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I9 | `=((D9*F9)*($H$2^2)/(32.4*2))*H9` |  |  | 2.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D10 | `=VLOOKUP(K6,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G10 | `=VLOOKUP(K6,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I10 | `=((D10*F10)*($H$2^2)/(32.4*2))*H10` |  |  | 2.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D11 | `=VLOOKUP(K7,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G11 | `=VLOOKUP(K7,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I11 | `=((D11*F11)*($H$2^2)/(32.4*2))*H11` |  |  | 2.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D12 | `=VLOOKUP(K8,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G12 | `=VLOOKUP(K8,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I12 | `=((D12*F12)*($H$2^2)/(32.4*2))*H12` |  |  | 2.0; 2.0; 2.0; 2.0; 32.4; 2.0; 2.0 |  | 0.000 |
| D13 | `=VLOOKUP(K9,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G13 | `=VLOOKUP(K9,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I13 | `=((D13*F13)*($H$2^2)/(32.4*2))*H13` |  |  | 3.0; 3.0; 2.0; 2.0; 32.4; 2.0; 3.0 |  | 0.000 |
| D14 | `=VLOOKUP(K10,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G14 | `=VLOOKUP(K10,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I14 | `=((D14*F14)*($H$2^2)/(32.4*2))*H14` |  |  | 4.0; 4.0; 2.0; 2.0; 32.4; 2.0; 4.0 |  | 0.000 |
| D15 | `=VLOOKUP(K11,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G15 | `=VLOOKUP(K11,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I15 | `=((D15*F15)*($H$2^2)/(32.4*2))*H15` |  |  | 5.0; 5.0; 2.0; 2.0; 32.4; 2.0; 5.0 |  | 0.000 |
| D16 | `=VLOOKUP(K12,FRICCION,3,FALSE)` | FRICCION |  | 2.0; 3.0 | VLOOKUP | 0.000 |
| G16 | `=VLOOKUP(K12,DIAMETRO,4,FALSE)` | DIAMETRO |  | 2.0; 4.0 | VLOOKUP | 0.00 |
| I16 | `=((D16*F16)*($H$2^2)/(32.4*2))*H16` |  |  | 6.0; 6.0; 2.0; 2.0; 32.4; 2.0; 6.0 |  | 0.000 |
| D17 | `=VLOOKUP(K13,FRICCION,3,FALSE)` | FRICCION |  | 3.0; 3.0 | VLOOKUP | 0.000 |
| G17 | `=VLOOKUP(K13,DIAMETRO,4,FALSE)` | DIAMETRO |  | 3.0; 4.0 | VLOOKUP | 0.00 |
| I17 | `=((D17*F17)*($H$2^2)/(32.4*2))*H17` |  |  | 7.0; 7.0; 2.0; 2.0; 32.4; 2.0; 7.0 |  | 0.000 |
| D18 | `=VLOOKUP(K14,FRICCION,3,FALSE)` | FRICCION |  | 4.0; 3.0 | VLOOKUP | 0.000 |
| G18 | `=VLOOKUP(K14,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0; 4.0 | VLOOKUP | 0.00 |
| I18 | `=((D18*F18)*($H$2^2)/(32.4*2))*H18` |  |  | 8.0; 8.0; 2.0; 2.0; 32.4; 2.0; 8.0 |  | 0.000 |
| D19 | `=VLOOKUP(K15,FRICCION,3,FALSE)` | FRICCION |  | 5.0; 3.0 | VLOOKUP | 0.000 |
| G19 | `=VLOOKUP(K15,DIAMETRO,4,FALSE)` | DIAMETRO |  | 5.0; 4.0 | VLOOKUP | 0.00 |
| I19 | `=((D19*F19)*($H$2^2)/(32.4*2))*H19` |  |  | 9.0; 9.0; 2.0; 2.0; 32.4; 2.0; 9.0 |  | 0.000 |
| D20 | `=VLOOKUP(K16,FRICCION,3,FALSE)` | FRICCION |  | 6.0; 3.0 | VLOOKUP | 0.000 |
| G20 | `=VLOOKUP(K16,DIAMETRO,4,FALSE)` | DIAMETRO |  | 6.0; 4.0 | VLOOKUP | 0.00 |
| I20 | `=((D20*F20)*($H$2^2)/(32.4*2))*H20` |  |  | 2.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D21 | `=VLOOKUP(K17,FRICCION,3,FALSE)` | FRICCION |  | 7.0; 3.0 | VLOOKUP | 0.000 |
| G21 | `=VLOOKUP(K17,DIAMETRO,4,FALSE)` | DIAMETRO |  | 7.0; 4.0 | VLOOKUP | 0.00 |
| I21 | `=((D21*F21)*($H$2^2)/(32.4*2))*H21` |  |  | 2.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D22 | `=VLOOKUP(K18,FRICCION,3,FALSE)` | FRICCION |  | 8.0; 3.0 | VLOOKUP | 0.000 |
| G22 | `=VLOOKUP(K18,DIAMETRO,4,FALSE)` | DIAMETRO |  | 8.0; 4.0 | VLOOKUP | 0.00 |
| I22 | `=((D22*F22)*($H$2^2)/(32.4*2))*H22` |  |  | 2.0; 2.0; 2.0; 2.0; 32.4; 2.0; 2.0 |  | 0.000 |
| D23 | `=VLOOKUP(K19,FRICCION,3,FALSE)` | FRICCION |  | 9.0; 3.0 | VLOOKUP | 0.000 |
| G23 | `=VLOOKUP(K19,DIAMETRO,4,FALSE)` | DIAMETRO |  | 9.0; 4.0 | VLOOKUP | 0.00 |
| I23 | `=((D23*F23)*($H$2^2)/(32.4*2))*H23` |  |  | 3.0; 3.0; 2.0; 2.0; 32.4; 2.0; 3.0 |  | 0.000 |
| D24 | `=VLOOKUP(K20,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G24 | `=VLOOKUP(K20,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I24 | `=((D24*F24)*($H$2^2)/(32.4*2))*H24` |  |  | 4.0; 4.0; 2.0; 2.0; 32.4; 2.0; 4.0 |  | 0.000 |
| D25 | `=VLOOKUP(K21,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G25 | `=VLOOKUP(K21,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I25 | `=((D25*F25)*($H$2^2)/(32.4*2))*H25` |  |  | 5.0; 5.0; 2.0; 2.0; 32.4; 2.0; 5.0 |  | 0.000 |
| D26 | `=VLOOKUP(K22,FRICCION,3,FALSE)` | FRICCION |  | 2.0; 3.0 | VLOOKUP | 0.000 |
| G26 | `=VLOOKUP(K22,DIAMETRO,4,FALSE)` | DIAMETRO |  | 2.0; 4.0 | VLOOKUP | 0.00 |
| I26 | `=((D26*F26)*($H$2^2)/(32.4*2))*H26` |  |  | 6.0; 6.0; 2.0; 2.0; 32.4; 2.0; 6.0 |  | 0.000 |
| D27 | `=VLOOKUP(K23,FRICCION,3,FALSE)` | FRICCION |  | 3.0; 3.0 | VLOOKUP | 0.000 |
| G27 | `=VLOOKUP(K23,DIAMETRO,4,FALSE)` | DIAMETRO |  | 3.0; 4.0 | VLOOKUP | 0.00 |
| I27 | `=((D27*F27)*($H$2^2)/(32.4*2))*H27` |  |  | 7.0; 7.0; 2.0; 2.0; 32.4; 2.0; 7.0 |  | 0.000 |
| D28 | `=VLOOKUP(K24,FRICCION,3,FALSE)` | FRICCION |  | 4.0; 3.0 | VLOOKUP | 0.000 |
| G28 | `=VLOOKUP(K24,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0; 4.0 | VLOOKUP | 0.00 |
| I28 | `=((D28*F28)*($H$2^2)/(32.4*2))*H28` |  |  | 8.0; 8.0; 2.0; 2.0; 32.4; 2.0; 8.0 |  | 0.000 |
| D29 | `=VLOOKUP(K25,FRICCION,3,FALSE)` | FRICCION |  | 5.0; 3.0 | VLOOKUP | 0.000 |
| G29 | `=VLOOKUP(K25,DIAMETRO,4,FALSE)` | DIAMETRO |  | 5.0; 4.0 | VLOOKUP | 0.00 |
| I29 | `=((D29*F29)*($H$2^2)/(32.4*2))*H29` |  |  | 9.0; 9.0; 2.0; 2.0; 32.4; 2.0; 9.0 |  | 0.000 |
| D30 | `=VLOOKUP(K26,FRICCION,3,FALSE)` | FRICCION |  | 6.0; 3.0 | VLOOKUP | 0.000 |
| G30 | `=VLOOKUP(K26,DIAMETRO,4,FALSE)` | DIAMETRO |  | 6.0; 4.0 | VLOOKUP | 0.00 |
| I30 | `=((D30*F30)*($H$2^2)/(32.4*2))*H30` |  |  | 2.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D31 | `=VLOOKUP(K27,FRICCION,3,FALSE)` | FRICCION |  | 7.0; 3.0 | VLOOKUP | 0.000 |
| G31 | `=VLOOKUP(K27,DIAMETRO,4,FALSE)` | DIAMETRO |  | 7.0; 4.0 | VLOOKUP | 0.00 |
| I31 | `=((D31*F31)*($H$2^2)/(32.4*2))*H31` |  |  | 2.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D32 | `=VLOOKUP(K28,FRICCION,3,FALSE)` | FRICCION |  | 8.0; 3.0 | VLOOKUP | 0.000 |
| G32 | `=VLOOKUP(K28,DIAMETRO,4,FALSE)` | DIAMETRO |  | 8.0; 4.0 | VLOOKUP | 0.00 |
| I32 | `=((D32*F32)*($H$2^2)/(32.4*2))*H32` |  |  | 2.0; 2.0; 2.0; 2.0; 32.4; 2.0; 2.0 |  | 0.000 |
| D33 | `=VLOOKUP(K29,FRICCION,3,FALSE)` | FRICCION |  | 9.0; 3.0 | VLOOKUP | 0.000 |
| G33 | `=VLOOKUP(K29,DIAMETRO,4,FALSE)` | DIAMETRO |  | 9.0; 4.0 | VLOOKUP | 0.00 |
| I33 | `=((D33*F33)*($H$2^2)/(32.4*2))*H33` |  |  | 3.0; 3.0; 2.0; 2.0; 32.4; 2.0; 3.0 |  | 0.000 |
| D34 | `=VLOOKUP(K30,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G34 | `=VLOOKUP(K30,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I34 | `=((D34*F34)*($H$2^2)/(32.4*2))*H34` |  |  | 4.0; 4.0; 2.0; 2.0; 32.4; 2.0; 4.0 |  | 0.000 |
| D35 | `=VLOOKUP(K31,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G35 | `=VLOOKUP(K31,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I35 | `=((D35*F35)*($H$2^2)/(32.4*2))*H35` |  |  | 5.0; 5.0; 2.0; 2.0; 32.4; 2.0; 5.0 |  | 0.000 |
| D36 | `=VLOOKUP(K32,FRICCION,3,FALSE)` | FRICCION |  | 2.0; 3.0 | VLOOKUP | 0.000 |
| G36 | `=VLOOKUP(K32,DIAMETRO,4,FALSE)` | DIAMETRO |  | 2.0; 4.0 | VLOOKUP | 0.00 |
| I36 | `=((D36*F36)*($H$2^2)/(32.4*2))*H36` |  |  | 6.0; 6.0; 2.0; 2.0; 32.4; 2.0; 6.0 |  | 0.000 |
| D37 | `=VLOOKUP(K33,FRICCION,3,FALSE)` | FRICCION |  | 3.0; 3.0 | VLOOKUP | 0.000 |
| G37 | `=VLOOKUP(K33,DIAMETRO,4,FALSE)` | DIAMETRO |  | 3.0; 4.0 | VLOOKUP | 0.00 |
| I37 | `=((D37*F37)*($H$2^2)/(32.4*2))*H37` |  |  | 7.0; 7.0; 2.0; 2.0; 32.4; 2.0; 7.0 |  | 0.000 |
| D38 | `=VLOOKUP(K34,FRICCION,3,FALSE)` | FRICCION |  | 4.0; 3.0 | VLOOKUP | 0.000 |
| G38 | `=VLOOKUP(K34,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0; 4.0 | VLOOKUP | 0.00 |
| I38 | `=((D38*F38)*($H$2^2)/(32.4*2))*H38` |  |  | 8.0; 8.0; 2.0; 2.0; 32.4; 2.0; 8.0 |  | 0.000 |
| D39 | `=VLOOKUP(K35,FRICCION,3,FALSE)` | FRICCION |  | 5.0; 3.0 | VLOOKUP | 0.000 |
| G39 | `=VLOOKUP(K35,DIAMETRO,4,FALSE)` | DIAMETRO |  | 5.0; 4.0 | VLOOKUP | 0.00 |
| I39 | `=((D39*F39)*($H$2^2)/(32.4*2))*H39` |  |  | 9.0; 9.0; 2.0; 2.0; 32.4; 2.0; 9.0 |  | 0.000 |
| D40 | `=VLOOKUP(K36,FRICCION,3,FALSE)` | FRICCION |  | 6.0; 3.0 | VLOOKUP | 0.000 |
| G40 | `=VLOOKUP(K36,DIAMETRO,4,FALSE)` | DIAMETRO |  | 6.0; 4.0 | VLOOKUP | 0.00 |
| I40 | `=((D40*F40)*($H$2^2)/(32.4*2))*H40` |  |  | 2.0; 2.0; 32.4; 2.0 |  | 0.000 |
| I41 | `=(O41+S41+U41+Y41+AC41+AG41)` |  |  |  |  | 0.000 |
| O41 | `=SUM(O7:O40)` |  |  |  | SUM | 0.000 |
| S41 | `=SUM(S7:S40)` |  |  |  | SUM | 0.000 |
| U41 | `=(SUM(U7:U40))*2.31` |  |  | 2.31 | SUM | General |
| Y41 | `=SUM(Y7:Y40)` |  |  |  | SUM | 0.000 |
| AC41 | `=SUM(AC7:AC40)` |  |  |  | SUM | 0.000 |
| AG41 | `=SUM(AG7:AG40)` |  |  |  | SUM | 0.000 |
| O42 | `=O41/2.31` |  |  | 2.31 |  | General |
| S42 | `=S41/2.31` |  |  | 2.31 |  | General |
| U42 | `=U41/2.31` |  |  | 2.31 |  | General |
| Y42 | `=Y41/2.31` |  |  | 2.31 |  | General |
| AC42 | `=AC41/2.31` |  |  | 2.31 |  | General |
| AG42 | `=AG41/2.31` |  |  | 2.31 |  | General |
| AH46 | `=SUM(AG41,AC41,Y41,S41,O41,U41)` |  |  |  | SUM | 0.000 |
| I77 | `=(D77*F77*(H77^2))/(32.4*2)` |  |  | 7.0; 7.0; 7.0; 2.0; 32.4; 2.0 |  | General |
| I78 | `=(D78*F78*(H78^2))/(32.4*2)` |  |  | 8.0; 8.0; 8.0; 2.0; 32.4; 2.0 |  | General |
| I79 | `=(D79*F79*(H79^2))/(32.4*2)` |  |  | 9.0; 9.0; 9.0; 2.0; 32.4; 2.0 |  | General |

## Sheet: `RAMALES` (6 formulas)

| Cell | Formula | Named Ranges | Sheet Refs | Constants | Functions | Format |
|------|---------|--------------|------------|-----------|-----------|--------|
| D9 | `='CAIDA PRESION DE TUBERIA'!G5` |  | CAIDA PRESION DE TUBERIA |  |  | 0.00 |
| D10 | `=(4*(D9/448.8309))/(PI()*(D8/12)*(D8/12))` |  |  | 4.0; 448.8309; 12.0; 12.0 | PI | 0.00 |
| D12 | `=((('CAIDA PRESION DE TUBERIA'!$G$17*'CAIDA PRESION DE TUBERIA'!$G$16*'CAIDA PRE...` |  | CAIDA PRESION DE TUBERIA | 17.0; 16.0; 9.0; 2.0; 7.0; 0.5; 5.0; 2.3071; 18.0 |  | 0.000 |
| D13 | `=D11*D12` |  |  | 2.0 |  | 0.00 |
| F18 | `=D11` |  |  |  |  | 0.00 |
| F19 | `=D13` |  |  | 3.0 |  | 0.00 |

## Sheet: `TABLA DE ACCESORIOS SUCCION` (103 formulas)

| Cell | Formula | Named Ranges | Sheet Refs | Constants | Functions | Format |
|------|---------|--------------|------------|-----------|-----------|--------|
| D6 | `=VLOOKUP(K2,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G6 | `=VLOOKUP(K2,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I6 | `=((D6*F6)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H6` |  | CAIDA PRESION DE TUBERIA | 6.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D7 | `=VLOOKUP(K3,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G7 | `=VLOOKUP(K3,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I7 | `=((D7*F7)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H7` |  | CAIDA PRESION DE TUBERIA | 6.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D8 | `=VLOOKUP(K4,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G8 | `=VLOOKUP(K4,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I8 | `=((D8*F8)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H8` |  | CAIDA PRESION DE TUBERIA | 6.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D9 | `=VLOOKUP(K5,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G9 | `=VLOOKUP(K5,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I9 | `=((D9*F9)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H9` |  | CAIDA PRESION DE TUBERIA | 6.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D10 | `=VLOOKUP(K6,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G10 | `=VLOOKUP(K6,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I10 | `=((D10*F10)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H10` |  | CAIDA PRESION DE TUBERIA | 6.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D11 | `=VLOOKUP(K7,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G11 | `=VLOOKUP(K7,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I11 | `=((D11*F11)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H11` |  | CAIDA PRESION DE TUBERIA | 6.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D12 | `=VLOOKUP(K8,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G12 | `=VLOOKUP(K8,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I12 | `=((D12*F12)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H12` |  | CAIDA PRESION DE TUBERIA | 2.0; 2.0; 6.0; 2.0; 32.4; 2.0; 2.0 |  | 0.000 |
| D13 | `=VLOOKUP(K9,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G13 | `=VLOOKUP(K9,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I13 | `=((D13*F13)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H13` |  | CAIDA PRESION DE TUBERIA | 3.0; 3.0; 6.0; 2.0; 32.4; 2.0; 3.0 |  | 0.000 |
| D14 | `=VLOOKUP(K10,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G14 | `=VLOOKUP(K10,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I14 | `=((D14*F14)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H14` |  | CAIDA PRESION DE TUBERIA | 4.0; 4.0; 6.0; 2.0; 32.4; 2.0; 4.0 |  | 0.000 |
| D15 | `=VLOOKUP(K11,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G15 | `=VLOOKUP(K11,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I15 | `=((D15*F15)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H15` |  | CAIDA PRESION DE TUBERIA | 5.0; 5.0; 6.0; 2.0; 32.4; 2.0; 5.0 |  | 0.000 |
| D16 | `=VLOOKUP(K12,FRICCION,3,FALSE)` | FRICCION |  | 2.0; 3.0 | VLOOKUP | 0.000 |
| G16 | `=VLOOKUP(K12,DIAMETRO,4,FALSE)` | DIAMETRO |  | 2.0; 4.0 | VLOOKUP | 0.00 |
| I16 | `=((D16*F16)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H16` |  | CAIDA PRESION DE TUBERIA | 6.0; 6.0; 6.0; 2.0; 32.4; 2.0; 6.0 |  | 0.000 |
| D17 | `=VLOOKUP(K13,FRICCION,3,FALSE)` | FRICCION |  | 3.0; 3.0 | VLOOKUP | 0.000 |
| G17 | `=VLOOKUP(K13,DIAMETRO,4,FALSE)` | DIAMETRO |  | 3.0; 4.0 | VLOOKUP | 0.00 |
| I17 | `=((D17*F17)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H17` |  | CAIDA PRESION DE TUBERIA | 7.0; 7.0; 6.0; 2.0; 32.4; 2.0; 7.0 |  | 0.000 |
| D18 | `=VLOOKUP(K14,FRICCION,3,FALSE)` | FRICCION |  | 4.0; 3.0 | VLOOKUP | 0.000 |
| G18 | `=VLOOKUP(K14,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0; 4.0 | VLOOKUP | 0.00 |
| I18 | `=((D18*F18)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H18` |  | CAIDA PRESION DE TUBERIA | 8.0; 8.0; 6.0; 2.0; 32.4; 2.0; 8.0 |  | 0.000 |
| D19 | `=VLOOKUP(K15,FRICCION,3,FALSE)` | FRICCION |  | 5.0; 3.0 | VLOOKUP | 0.000 |
| G19 | `=VLOOKUP(K15,DIAMETRO,4,FALSE)` | DIAMETRO |  | 5.0; 4.0 | VLOOKUP | 0.00 |
| I19 | `=((D19*F19)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H19` |  | CAIDA PRESION DE TUBERIA | 9.0; 9.0; 6.0; 2.0; 32.4; 2.0; 9.0 |  | 0.000 |
| D20 | `=VLOOKUP(K16,FRICCION,3,FALSE)` | FRICCION |  | 6.0; 3.0 | VLOOKUP | 0.000 |
| G20 | `=VLOOKUP(K16,DIAMETRO,4,FALSE)` | DIAMETRO |  | 6.0; 4.0 | VLOOKUP | 0.00 |
| I20 | `=((D20*F20)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H20` |  | CAIDA PRESION DE TUBERIA | 6.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D21 | `=VLOOKUP(K17,FRICCION,3,FALSE)` | FRICCION |  | 7.0; 3.0 | VLOOKUP | 0.000 |
| G21 | `=VLOOKUP(K17,DIAMETRO,4,FALSE)` | DIAMETRO |  | 7.0; 4.0 | VLOOKUP | 0.00 |
| I21 | `=((D21*F21)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H21` |  | CAIDA PRESION DE TUBERIA | 6.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D22 | `=VLOOKUP(K18,FRICCION,3,FALSE)` | FRICCION |  | 8.0; 3.0 | VLOOKUP | 0.000 |
| G22 | `=VLOOKUP(K18,DIAMETRO,4,FALSE)` | DIAMETRO |  | 8.0; 4.0 | VLOOKUP | 0.00 |
| I22 | `=((D22*F22)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H22` |  | CAIDA PRESION DE TUBERIA | 2.0; 2.0; 6.0; 2.0; 32.4; 2.0; 2.0 |  | 0.000 |
| D23 | `=VLOOKUP(K19,FRICCION,3,FALSE)` | FRICCION |  | 9.0; 3.0 | VLOOKUP | 0.000 |
| G23 | `=VLOOKUP(K19,DIAMETRO,4,FALSE)` | DIAMETRO |  | 9.0; 4.0 | VLOOKUP | 0.00 |
| I23 | `=((D23*F23)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H23` |  | CAIDA PRESION DE TUBERIA | 3.0; 3.0; 6.0; 2.0; 32.4; 2.0; 3.0 |  | 0.000 |
| D24 | `=VLOOKUP(K20,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G24 | `=VLOOKUP(K20,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I24 | `=((D24*F24)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H24` |  | CAIDA PRESION DE TUBERIA | 4.0; 4.0; 6.0; 2.0; 32.4; 2.0; 4.0 |  | 0.000 |
| D25 | `=VLOOKUP(K21,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G25 | `=VLOOKUP(K21,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I25 | `=((D25*F25)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H25` |  | CAIDA PRESION DE TUBERIA | 5.0; 5.0; 6.0; 2.0; 32.4; 2.0; 5.0 |  | 0.000 |
| D26 | `=VLOOKUP(K22,FRICCION,3,FALSE)` | FRICCION |  | 2.0; 3.0 | VLOOKUP | 0.000 |
| G26 | `=VLOOKUP(K22,DIAMETRO,4,FALSE)` | DIAMETRO |  | 2.0; 4.0 | VLOOKUP | 0.00 |
| I26 | `=((D26*F26)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H26` |  | CAIDA PRESION DE TUBERIA | 6.0; 6.0; 6.0; 2.0; 32.4; 2.0; 6.0 |  | 0.000 |
| D27 | `=VLOOKUP(K23,FRICCION,3,FALSE)` | FRICCION |  | 3.0; 3.0 | VLOOKUP | 0.000 |
| G27 | `=VLOOKUP(K23,DIAMETRO,4,FALSE)` | DIAMETRO |  | 3.0; 4.0 | VLOOKUP | 0.00 |
| I27 | `=((D27*F27)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H27` |  | CAIDA PRESION DE TUBERIA | 7.0; 7.0; 6.0; 2.0; 32.4; 2.0; 7.0 |  | 0.000 |
| D28 | `=VLOOKUP(K24,FRICCION,3,FALSE)` | FRICCION |  | 4.0; 3.0 | VLOOKUP | 0.000 |
| G28 | `=VLOOKUP(K24,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0; 4.0 | VLOOKUP | 0.00 |
| I28 | `=((D28*F28)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H28` |  | CAIDA PRESION DE TUBERIA | 8.0; 8.0; 6.0; 2.0; 32.4; 2.0; 8.0 |  | 0.000 |
| D29 | `=VLOOKUP(K25,FRICCION,3,FALSE)` | FRICCION |  | 5.0; 3.0 | VLOOKUP | 0.000 |
| G29 | `=VLOOKUP(K25,DIAMETRO,4,FALSE)` | DIAMETRO |  | 5.0; 4.0 | VLOOKUP | 0.00 |
| I29 | `=((D29*F29)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H29` |  | CAIDA PRESION DE TUBERIA | 9.0; 9.0; 6.0; 2.0; 32.4; 2.0; 9.0 |  | 0.000 |
| D30 | `=VLOOKUP(K26,FRICCION,3,FALSE)` | FRICCION |  | 6.0; 3.0 | VLOOKUP | 0.000 |
| G30 | `=VLOOKUP(K26,DIAMETRO,4,FALSE)` | DIAMETRO |  | 6.0; 4.0 | VLOOKUP | 0.00 |
| I30 | `=((D30*F30)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H30` |  | CAIDA PRESION DE TUBERIA | 6.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D31 | `=VLOOKUP(K27,FRICCION,3,FALSE)` | FRICCION |  | 7.0; 3.0 | VLOOKUP | 0.000 |
| G31 | `=VLOOKUP(K27,DIAMETRO,4,FALSE)` | DIAMETRO |  | 7.0; 4.0 | VLOOKUP | 0.00 |
| I31 | `=((D31*F31)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H31` |  | CAIDA PRESION DE TUBERIA | 6.0; 2.0; 32.4; 2.0 |  | 0.000 |
| D32 | `=VLOOKUP(K28,FRICCION,3,FALSE)` | FRICCION |  | 8.0; 3.0 | VLOOKUP | 0.000 |
| G32 | `=VLOOKUP(K28,DIAMETRO,4,FALSE)` | DIAMETRO |  | 8.0; 4.0 | VLOOKUP | 0.00 |
| I32 | `=((D32*F32)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H32` |  | CAIDA PRESION DE TUBERIA | 2.0; 2.0; 6.0; 2.0; 32.4; 2.0; 2.0 |  | 0.0000 |
| D33 | `=VLOOKUP(K29,FRICCION,3,FALSE)` | FRICCION |  | 9.0; 3.0 | VLOOKUP | 0.000 |
| G33 | `=VLOOKUP(K29,DIAMETRO,4,FALSE)` | DIAMETRO |  | 9.0; 4.0 | VLOOKUP | 0.00 |
| I33 | `=((D33*F33)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H33` |  | CAIDA PRESION DE TUBERIA | 3.0; 3.0; 6.0; 2.0; 32.4; 2.0; 3.0 |  | 0.000 |
| D34 | `=VLOOKUP(K30,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G34 | `=VLOOKUP(K30,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I34 | `=((D34*F34)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H34` |  | CAIDA PRESION DE TUBERIA | 4.0; 4.0; 6.0; 2.0; 32.4; 2.0; 4.0 |  | 0.000 |
| D35 | `=VLOOKUP(K31,FRICCION,3,FALSE)` | FRICCION |  | 3.0 | VLOOKUP | 0.000 |
| G35 | `=VLOOKUP(K31,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0 | VLOOKUP | 0.00 |
| I35 | `=((D35*F35)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H35` |  | CAIDA PRESION DE TUBERIA | 5.0; 5.0; 6.0; 2.0; 32.4; 2.0; 5.0 |  | 0.000 |
| D36 | `=VLOOKUP(K32,FRICCION,3,FALSE)` | FRICCION |  | 2.0; 3.0 | VLOOKUP | 0.000 |
| G36 | `=VLOOKUP(K32,DIAMETRO,4,FALSE)` | DIAMETRO |  | 2.0; 4.0 | VLOOKUP | 0.00 |
| I36 | `=((D36*F36)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H36` |  | CAIDA PRESION DE TUBERIA | 6.0; 6.0; 6.0; 2.0; 32.4; 2.0; 6.0 |  | 0.000 |
| D37 | `=VLOOKUP(K33,FRICCION,3,FALSE)` | FRICCION |  | 3.0; 3.0 | VLOOKUP | 0.000 |
| G37 | `=VLOOKUP(K33,DIAMETRO,4,FALSE)` | DIAMETRO |  | 3.0; 4.0 | VLOOKUP | 0.00 |
| I37 | `=((D37*F37)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H37` |  | CAIDA PRESION DE TUBERIA | 7.0; 7.0; 6.0; 2.0; 32.4; 2.0; 7.0 |  | 0.000 |
| D38 | `=VLOOKUP(K34,FRICCION,3,FALSE)` | FRICCION |  | 4.0; 3.0 | VLOOKUP | 0.000 |
| G38 | `=VLOOKUP(K34,DIAMETRO,4,FALSE)` | DIAMETRO |  | 4.0; 4.0 | VLOOKUP | 0.00 |
| I38 | `=((D38*F38)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H38` |  | CAIDA PRESION DE TUBERIA | 8.0; 8.0; 6.0; 2.0; 32.4; 2.0; 8.0 |  | 0.000 |
| D39 | `=VLOOKUP(K35,FRICCION,3,FALSE)` | FRICCION |  | 5.0; 3.0 | VLOOKUP | 0.000 |
| G39 | `=VLOOKUP(K35,DIAMETRO,4,FALSE)` | DIAMETRO |  | 5.0; 4.0 | VLOOKUP | 0.00 |
| I39 | `=((D39*F39)*('CAIDA PRESION DE TUBERIA'!$V$6^2)/(32.4*2))*H39` |  | CAIDA PRESION DE TUBERIA | 9.0; 9.0; 6.0; 2.0; 32.4; 2.0; 9.0 |  | 0.000 |
| I40 | `=SUM(I6:I39)` |  |  | 9.0 | SUM | 0.000 |

## Sheet: `005PU001` (12 formulas)

| Cell | Formula | Named Ranges | Sheet Refs | Constants | Functions | Format |
|------|---------|--------------|------------|-----------|-----------|--------|
| E4 | `='CALCULO DE BOMBA'!C2` |  | CALCULO DE BOMBA |  |  | General |
| E5 | `='CALCULO DE BOMBA'!C1` |  | CALCULO DE BOMBA |  |  | General |
| H6 | `='RESUMEN PARA PDF'!B13` |  | RESUMEN PARA PDF | 3.0 |  | 0.00 |
| H7 | `='RESUMEN PARA PDF'!B16` |  | RESUMEN PARA PDF | 6.0 |  | 0.00 |
| H8 | `='RESUMEN PARA PDF'!B28` |  | RESUMEN PARA PDF | 8.0 |  | 0.00 |
| D9 | `='RESUMEN PARA PDF'!G14` |  | RESUMEN PARA PDF | 4.0 |  | General |
| H9 | `='RESUMEN PARA PDF'!D28` |  | RESUMEN PARA PDF | 8.0 |  | 0.00 |
| D10 | `='RESUMEN PARA PDF'!G16` |  | RESUMEN PARA PDF | 6.0 |  | 0.00 |
| H10 | `='RESUMEN PARA PDF'!G25/3.281` |  | RESUMEN PARA PDF | 5.0; 3.281 |  | 0.00 |
| D11 | `='RESUMEN PARA PDF'!G15` |  | RESUMEN PARA PDF | 5.0 |  | General |
| H11 | `='RESUMEN PARA PDF'!G29` |  | RESUMEN PARA PDF | 9.0 |  | 0.00 |
| D23 | `='RESUMEN PARA PDF'!G28` |  | RESUMEN PARA PDF | 8.0 |  | 0% |

## Sheet: `RESUMEN PARA PDF` (61 formulas)

| Cell | Formula | Named Ranges | Sheet Refs | Constants | Functions | Format |
|------|---------|--------------|------------|-----------|-----------|--------|
| C4 | `='CALCULO DE BOMBA'!C2` |  | CALCULO DE BOMBA |  |  | General |
| B9 | `=C4` |  |  |  |  | General |
| B13 | `='CAIDA PRESION DE TUBERIA'!V5` |  | CAIDA PRESION DE TUBERIA |  |  | 0.00 |
| D13 | `=B13*3.785` |  |  | 3.0; 3.785 |  | General |
| G13 | `='CALCULO DE BOMBA'!C4` |  | CALCULO DE BOMBA |  |  | 0 |
| G14 | `='CALCULO DE BOMBA'!E6` |  | CALCULO DE BOMBA |  |  | General |
| D15 | `=B15*3.785` |  |  | 5.0; 3.785 |  | 0.00 |
| B16 | `=B13+B15` |  |  | 3.0; 5.0 |  | 0.00 |
| D16 | `=B16*3.785` |  |  | 6.0; 3.785 |  | 0.00 |
| G16 | `='CALCULO DE BOMBA'!E11` |  | CALCULO DE BOMBA |  |  | 0.00 |
| B19 | `='CALCULO DE BOMBA'!C9` |  | CALCULO DE BOMBA |  |  | 0.000 |
| D19 | `=B19/3.28` |  |  | 9.0; 3.28 |  | 0.00 |
| B20 | `='CALCULO DE BOMBA'!C20` |  | CALCULO DE BOMBA |  |  | 0.00 |
| D20 | `=B20/3.28` |  |  | 3.28 |  | General |
| B21 | `=B20-B19` |  |  | 9.0 |  | 0.00 |
| D21 | `=B21/3.28` |  |  | 3.28 |  | 0.00 |
| C23 | `='CALCULO DE BOMBA'!C14` |  | CALCULO DE BOMBA | 4.0 |  | 0.0000 |
| C24 | `='CALCULO DE BOMBA'!C11` |  | CALCULO DE BOMBA |  |  | 0.0000 |
| G24 | `='CALCULO DE BOMBA'!E10` |  | CALCULO DE BOMBA |  |  | 0.00 |
| C25 | `=RAMALES!F19` |  |  | 9.0 |  | 0.000 |
| G25 | `='CALCULO DE BOMBA'!E14` |  | CALCULO DE BOMBA | 4.0 |  | 0.00 |
| C26 | `='TABLA DE ACCESORIOS DESCARGA'!I41` | DESCARGA | TABLA DE ACCESORIOS DESCARGA |  |  | 0.000 |
| B28 | `=(B21+C23+C24+C25+C26)*1` |  |  | 3.0; 4.0; 5.0; 6.0 |  | 0.00 |
| D28 | `=B28/2.31` |  |  | 8.0; 2.31 |  | 0.00 |
| G28 | `='CALCULO DE BOMBA'!C22` |  | CALCULO DE BOMBA | 2.0 |  | 0% |
| G29 | `='CALCULO DE BOMBA'!E21` |  | CALCULO DE BOMBA |  |  | 0.00 |
| B32 | `=B14` |  |  | 4.0 |  | 0 |
| D32 | `=G14` |  |  | 4.0 |  | 0.00 |
| F32 | `=G81` |  |  |  |  | 0% |
| B33 | `=B13` |  |  | 3.0 |  | General |
| D33 | `='CALCULO DE BOMBA'!E11` |  | CALCULO DE BOMBA |  |  | 0.00 |
| B34 | `=B28` |  |  | 8.0 |  | 0.00 |
| F34 | `=E37` |  |  | 7.0 |  | 0.00 |
| B35 | `=G29` |  |  | 9.0 |  | 0.00 |
| D35 | `=G37` |  |  | 7.0 |  | 0.00 |
| B36 | `=G80` |  |  |  |  | 0.00 |
| D36 | `=G25` |  |  | 5.0 |  | 0.00 |
| A37 | `=A46` |  |  | 6.0 |  | General |
| B37 | `=B46` |  |  | 6.0 |  | General |
| C37 | `=C46` |  |  | 6.0 |  | General |
| E37 | `='005PU001'!H20` |  | 005PU001 |  |  | 0.00 |
| G37 | `='005PU001'!H19` |  | 005PU001 | 9.0 |  | 0.00 |
| C46 | `='005PU001'!D19` |  | 005PU001 | 9.0 |  | General |
| D46 | `='005PU001'!D21` |  | 005PU001 |  |  | General |
| E46 | `='005PU001'!D25` |  | 005PU001 | 5.0 |  | General |
| F46 | `=F32` |  |  | 2.0 |  | 0% |
| G46 | `='005PU001'!H19` |  | 005PU001 | 9.0 |  | General |
| H46 | `='005PU001'!H20` |  | 005PU001 |  |  | General |
| B50 | `=RAMALES!D5` |  |  |  |  | 0 |
| B51 | `=RAMALES!D6` |  |  |  |  | 0.00 |
| B52 | `=RAMALES!D7` |  |  |  |  | 0.00 |
| B53 | `=RAMALES!D8` |  |  |  |  | 0 |
| B54 | `=RAMALES!D9` |  |  |  |  | 0 |
| B55 | `=RAMALES!D10` |  |  |  |  | 0 |
| B56 | `=RAMALES!D11` |  |  |  |  | 0 |
| B57 | `=RAMALES!D12` |  |  | 2.0 |  | 0.0000 |
| B58 | `=RAMALES!D13` |  |  | 3.0 |  | 0.0000 |
| G77 | `=B16` |  |  | 6.0 |  | 0.00 |
| G78 | `=B28` |  |  | 8.0 |  | 0.00 |
| G81 | `=G28` |  |  | 8.0 |  | 0% |
| G82 | `=E37` |  |  | 7.0 |  | 0.00 |

## Sheet: `VELOCIDADES RECOMENDADAS` (23 formulas)

| Cell | Formula | Named Ranges | Sheet Refs | Constants | Functions | Format |
|------|---------|--------------|------------|-----------|-----------|--------|
| AB5 | `=(AA5*3.2808)/1.422` |  |  | 3.2808; 1.422 |  | 0.000 |
| AB6 | `=(AA6*3.2808)/1.422` |  |  | 3.2808; 1.422 |  | 0.000 |
| AB7 | `=(AA7*3.2808)/1.422` |  |  | 3.2808; 1.422 |  | 0.000 |
| AB8 | `=(AA8*3.2808)/1.422` |  |  | 3.2808; 1.422 |  | 0.000 |
| AB9 | `=(AA9*3.2808)/1.422` |  |  | 3.2808; 1.422 |  | 0.000 |
| AB10 | `=(AA10*3.2808)/1.422` |  |  | 3.2808; 1.422 |  | 0.000 |
| AB11 | `=(AA11*3.2808)/1.422` |  |  | 3.2808; 1.422 |  | 0.000 |
| AB12 | `=(AA12*3.2808)/1.422` |  |  | 2.0; 3.2808; 1.422 |  | 0.000 |
| AB13 | `=(AA13*3.2808)/1.422` |  |  | 3.0; 3.2808; 1.422 |  | 0.000 |
| AB14 | `=(AA14*3.2808)/1.422` |  |  | 4.0; 3.2808; 1.422 |  | 0.000 |
| AB15 | `=(AA15*3.2808)/1.422` |  |  | 5.0; 3.2808; 1.422 |  | 0.000 |
| AB16 | `=(AA16*3.2808)/1.422` |  |  | 6.0; 3.2808; 1.422 |  | 0.000 |
| AB17 | `=(AA17*3.2808)/1.422` |  |  | 7.0; 3.2808; 1.422 |  | 0.000 |
| AB18 | `=(AA18*3.2808)/1.422` |  |  | 8.0; 3.2808; 1.422 |  | 0.000 |
| AB19 | `=(AA19*3.2808)/1.422` |  |  | 9.0; 3.2808; 1.422 |  | 0.000 |
| AB20 | `=(AA20*3.2808)/1.422` |  |  | 3.2808; 1.422 |  | 0.000 |
| AB21 | `=(AA21*3.2808)/1.422` |  |  | 3.2808; 1.422 |  | 0.000 |
| AB22 | `=(AA22*3.2808)/1.422` |  |  | 2.0; 3.2808; 1.422 |  | 0.000 |
| AB23 | `=(AA23*3.2808)/1.422` |  |  | 3.0; 3.2808; 1.422 |  | 0.000 |
| V27 | `=(2.3071*'CALCULO DE BOMBA'!C8)-('CALCULO DE BOMBA'!E9+'CALCULO DE BOMBA'!C9+'CA...` |  | CALCULO DE BOMBA | 2.3071 |  | 0.00 |
| V28 | `=(2.3071*'CALCULO DE BOMBA'!E8)-('CALCULO DE BOMBA'!E9+'CALCULO DE BOMBA'!C9+'CA...` |  | CALCULO DE BOMBA | 2.3071 |  | 0.00 |
| V29 | `=(2.3071*'CALCULO DE BOMBA'!C8)+'CALCULO DE BOMBA'!C9-('CALCULO DE BOMBA'!E9+'CA...` |  | CALCULO DE BOMBA | 2.3071 |  | 0.00 |
| V30 | `=(2.3071*'CALCULO DE BOMBA'!E8)+'CALCULO DE BOMBA'!C9-('CALCULO DE BOMBA'!E9+'CA...` |  | CALCULO DE BOMBA | 2.3071 |  | 0.00 |

## Sheet: `REPORTE GENERAL` (15 formulas)

| Cell | Formula | Named Ranges | Sheet Refs | Constants | Functions | Format |
|------|---------|--------------|------------|-----------|-----------|--------|
| H14 | `=VLOOKUP('CAIDA PRESION DE TUBERIA'!F30,OUTPIPES,2,FALSE)` | OUTPIPE; OUTPIPES | CAIDA PRESION DE TUBERIA | 2.0 | VLOOKUP | General |
| I14 | `=VLOOKUP('CAIDA PRESION DE TUBERIA'!G30,OUTPIPES,2,FALSE)` | OUTPIPE; OUTPIPES | CAIDA PRESION DE TUBERIA | 2.0 | VLOOKUP | General |
| C15 | `=VLOOKUP('CAIDA PRESION DE TUBERIA'!A31,OUTPIPES,2,FALSE)` | OUTPIPE; OUTPIPES | CAIDA PRESION DE TUBERIA | 2.0 | VLOOKUP | General |
| D15 | `=VLOOKUP('CAIDA PRESION DE TUBERIA'!B31,OUTPIPES,2,FALSE)` | OUTPIPE; OUTPIPES | CAIDA PRESION DE TUBERIA | 2.0 | VLOOKUP | General |
| C16 | `=C14*0.05` |  |  | 4.0; 0.05 |  | General |
| C17 | `=C14+C16` |  |  | 4.0; 6.0 |  | General |
| C21 | `=C20-C11` |  |  |  |  | 0.00 |
| D21 | `=D20-D11` |  |  |  |  | 0.00 |
| C22 | `=C21-C20` |  |  |  |  | 0.00 |
| C24 | `=(RAMALES!E15)` |  |  | 5.0 |  | 0.00 |
| D24 | `=(RAMALES!#REF!)` |  |  |  |  | 0.00 |
| H28 | `='CALCULO DE BOMBA'!E10` |  | CALCULO DE BOMBA |  |  | 0.00 |
| C29 | `=C24+C25+C26+C27+C28` |  |  | 4.0; 5.0; 6.0; 7.0; 8.0 |  | 0.00 |
| H29 | `='CALCULO DE BOMBA'!E14` |  | CALCULO DE BOMBA | 4.0 |  | 0.00 |
| C30 | `=C22+C29` |  |  | 2.0; 9.0 |  | 0.00 |

