"""
Reynolds Number Derivation for Imperial Units
==============================================

Fundamental definition: Re = ρVD/μ

Given:
- Q = GPM (US gallons per minute)
- ρ = lbm/ft³ (mass density)
- D = inches
- μ = cP (centipoise)

Step-by-step derivation:

1. Convert Q to ft³/s:
   1 GPM = 1 gal/min = (231 in³)/min = 231/1728 ft³/min = 0.1336806 ft³/min
   1 GPM = 0.1336806/60 ft³/s = 0.002228009 ft³/s
   So: Q_ft3s = Q_GPM × 0.002228009

2. Convert D to feet:
   D_ft = D_in / 12

3. Convert μ from cP to lbm/(ft·s):
   1 cP = 0.01 P = 0.01 g/(cm·s)
   1 g = 0.00220462 lbm
   1 cm = 0.0328084 ft
   1 cP = 0.01 × 0.00220462 / 0.0328084 lbm/(ft·s) = 0.000671969 lbm/(ft·s)
   So: μ_lbm_ft_s = μ_cP × 0.000671969

4. Velocity V = Q / A
   A = π × D² / 4
   V = Q_ft3s / (π × (D_ft)² / 4)
   V = (Q_GPM × 0.002228009) / (π × (D_in/12)² / 4)
   V = (Q_GPM × 0.002228009 × 4 × 144) / (π × D_in²)
   V = (Q_GPM × 1.28378) / (π × D_in²)

5. Re = ρ × V × D / μ
   Re = ρ_lbm_ft3 × V_ft_s × D_ft / μ_lbm_ft_s
   Re = ρ × [(Q × 1.28378)/(π × D²)] × (D/12) / (μ × 0.000671969)
   Re = ρ × Q × 1.28378 / (π × D × 12 × 0.000671969)
   Re = ρ × Q × 1.28378 / (π × 12 × 0.000671969) × 1/D
   Re = ρ × Q / (D × μ) × [1.28378 / (π × 12 × 0.000671969)]

Let's compute the constant:
   C = 1.28378 / (π × 12 × 0.000671969)
   C = 1.28378 / (3.14159 × 12 × 0.000671969)
   C = 1.28378 / 0.025355
   C = 50.629

So Re = 50.63 × Q × ρ / (D × μ)

This matches the 50.6 factor in the workbook!

The factor is CORRECT for:
- Q in GPM
- ρ in lbm/ft³ (MASS density, not specific gravity)
- D in inches
- μ in cP

My previous conclusion was WRONG - the formula uses mass density (lbm/ft³), not specific gravity.
The standard formula Re = 50.6 × Q × SG / (D × μ) assumes SG = ρ/62.4 (for water at 60°F).
But here ρ is explicitly mass density in lbm/ft³.

Let's verify with current values:
- G5 = 770.5 GPM
- G9 = 62.4 lbm/ft³ (water density from VLOOKUP)
- G8 = 6.048 in (calculated diameter)
- G10 = 1.0 cP (water viscosity from VLOOKUP)

Re = 50.6 × 770.5 × 62.4 / (6.048 × 1.0) = 50.6 × 48079.2 / 6.048 = 50.6 × 7949.6 = 402,250

Wait, the workbook shows 768,552. Let me check the actual values...

Actually G9 comes from VLOOKUP(A20, OUTPIPES, 6, FALSE). Let me check what value that returns.
A20 = 6 (fluid code). OUTPIPES table column 6.

From the workbook inventory, OUTPIPES references 'VELOCIDADES RECOMENDADAS'!$B$4:$I$23
Column 6 would be the 6th column in that range.

Looking at VELOCIDADES RECOMENDADAS sheet structure:
Columns B-I (8 columns):
B: Item, C: Product, D: Velocity, E: Max Vel, F: Min Vel, G: Density, H: Viscosity, I: Friction Factor

So column 6 = column G = Density (lb/ft³)
For item 6 (row 6 in table): "Licor negro (15-25%)" has density 62
But A20 = 6, which might be a different fluid code.

Let me trace: A20 is the fluid selection cell. The value in A20 determines the VLOOKUP.

From the inventory, CAIDA!A20 = 6 (constant). So fluid code 6.

In VELOCIDADES RECOMENDADAS, the OUTPIPES range is B4:I23 (rows 4-23, columns B-I).
Row 4: headers. Row 5: Item 1. Row 6: Item 2... Row 10: Item 6.

Item 6 in the table (row 10): "Aceite automotriz" with density 43.59 lb/ft³, viscosity 6 cP.

But wait, OUTPIPES is B4:I23, so column B = Item number, column C = Product, D = Velocity, E = Max Vel, F = Min Vel, G = Density, H = Viscosity, I = Friction Factor.

VLOOKUP(A20, OUTPIPES, 6, FALSE) looks for value in column B (Item), returns column 6 = G = Density.
VLOOKUP(A20, OUTPIPES, 7, FALSE) returns column 7 = H = Viscosity.
VLOOKUP(A20, OUTPIPES, 8, FALSE) returns column 8 = I = Friction Factor.

For A20=6: Item 6 is "Aceite automotriz" (row 10 in table, row 10 in sheet).
Density = 43.59 lb/ft³ (G10)
Viscosity = 6 cP (H10)
Friction Factor = 0.00013 (I10)

But the workbook shows G9 = VLOOKUP(A20, OUTPIPES, 6) = 43.59? Let me check the actual value.

From the formula inventory:
G9 = VLOOKUP(A20, OUTPIPES, 6, FALSE)
G10 = VLOOKUP(A20, OUTPIPES, 7, FALSE)
G16 = VLOOKUP(A20, OUTPIPES, 8, FALSE)

And G11 = 50.6*G5*G9/(G8*G10) = 50.6*770.5*G9/(G8*G10)

The workbook shows G11 = 768,552.52

Let's solve for G9/G10 ratio:
768552 = 50.6 * 770.5 * G9 / (G8 * G10)
G8 = 6.048 (from G7*(G5/G6)^0.5 where G7=0.639, G5=770.5, G6=8.6)
G8 = 0.639 * sqrt(770.5/8.6) = 0.639 * sqrt(89.593) = 0.639 * 9.465 = 6.048

So:
768552 = 50.6 * 770.5 * G9 / (6.048 * G10)
G9/G10 = 768552 * 6.048 / (50.6 * 770.5) = 4647840 / 38987.3 = 119.2

If G9 = 43.59 (density) and G10 = 6 (viscosity), then G9/G10 = 7.265
Then Re = 50.6 * 770.5 * 7.265 / 6.048 = 50.6 * 924.7 = 46,790

That doesn't match 768,552.

Let me check the actual VLOOKUP results more carefully. Maybe the fluid code is different.

From the workbook inventory, the cell values show:
G9 formula: =VLOOKUP(A20,OUTPIPES,6,FALSE)
G10 formula: =VLOOKUP(A20,OUTPIPES,7,FALSE)

And A20 = 6 (constant)

In VELOCIDADES RECOMENDADAS, OUTPIPES = 'VELOCIDADES RECOMENDADAS'!$B$4:$I$23

Looking at the table data from the inventory:
Row 5 (item 1): Licor negro (15-25%) - density 62, visc 1.5
Row 6 (item 2): Aceite automotriz - density 43.59, visc 6
Row 7 (item 3): Aceite diesel - density 41.2, visc 4
Row 8 (item 4): Agua clara - density 62.4, visc 1
Row 9 (item 5): Agua de mar - density 64, visc 1.2
Row 10 (item 6): ... need to check

Actually the inventory shows up to row 23. Let me look at the actual data.

From the cell sample of VELOCIDADES RECOMENDADAS:
B5=1, C5="Licor negro (15-25%)", D5=7, E5=13, F5=4, G5=62, H5=1.5, I5=0.00013
B6=2, C6="Aceite automotriz", D6=4, E6=6, F6=4, G6=43.59, H6=6, I6=0.00013
B7=3, C7="Aceite diesel", D7=4, E7=6, F7=4, G7=41.2, H7=4, I7=0.00013
B8=4, C8="Agua clara", D8=7, E8=13, F8=4, G8=62.4, H8=1, I8=0.00013
B9=5, C9="Agua de mar", D9=7, E9=13, F9=4, G9=64, H9=1.2, I9=0.00013

So for A20=6, we need item 6. The table has at least 9 items (B5 to B13 for 1-9?).

B10 would be item 6. Let me check if there's data for item 6.

The table goes to row 23. Items 1-9 in rows 5-13? Let me check.

Actually from the inventory: B5=1, B6=2, B7=3, B8=4, B9=5... so B10=6, B11=7, etc.

But the inventory only shows first 20 cells. Let me check the full data.

Wait, the named range OUTPIPES is $B$4:$I$23, so rows 4-23 (20 rows of data,000 data rows).
Row 4 is header, rows 5-23 are data (19 items).

So item 6 would be at row 10 (row 4 + 6 = row 10).

But we don't have the value for row 10 in the sample. Let me check if the fluid is actually water.

Actually, looking at the suction side (INPIPE), V9 and V10 use INPIPE table.
And CALCULO DE BOMBA references fluid code from A32.

In CALCULO DE BOMBA:
A32 = 9 (constant)
E9 = VLOOKUP(A32, presionvapor, 4, FALSE) - vapor pressure
E11 = VLOOKUP(A32, gravedadespecifica, 5, FALSE) - specific gravity

So fluid code 9 is used for vapor pressure and specific gravity.

But CAIDA PRESION DE TUBERIA uses A20=6 for discharge and B20=6 for suction.

The two sides might use different fluid codes! But both are 6.

Let me check what fluid code 6 is in the OUTPIPES table.

From the VLOOKUP results, we know the workbook calculates Re = 768,552 for discharge.
If G9 = density and G10 = viscosity, and Re = 50.6*Q*G9/(G8*G10) = 768552
Then G9/G10 = 768552 * G8 / (50.6 * Q) = 768552 * 6.048 / (50.6 * 770.5) = 4647840 / 38987.3 = 119.2

So density/viscosity ratio = 119.2
If viscosity = 1 cP (water), density = 119.2 lb/ft³ - not water.
If viscosity = 1.5, density = 178.8 - no.
If density = 62.4 (water), viscosity = 0.52 cP - close to water at higher temp.

Wait, maybe the OUTPIPES table returns different values. Let me look at the actual VLOOKUP columns.

OUTPIPES is 'VELOCIDADES RECOMENDADAS'!$B$4:$I$23
Columns: B=Item, C=Product, D=Vel, E=MaxVel, F=MinVel, G=Density, H=Viscosity, I=FrictionFactor

VLOOKUP(A20, OUTPIPES, 6, FALSE) - 6th column of range = column G (Density)
VLOOKUP(A20, OUTPIPES, 7, FALSE) - 7th column = column H (Viscosity)
VLOOKUP(A20, OUTPIPES, 8, FALSE) - 8th column = column I (Friction Factor)

For item 6 (row 10 in data), what are G and H values?

The inventory shows up to item 5 (row 9). Items 6+ not shown in sample.

But wait - the CALCULO DE BOMBA sheet uses fluid code 9 (A32=9) for vapor pressure and specific gravity.
And it gets density from gravedadespecifica table (column 5).

Let me check the gravedadespecifica named range: 'VELOCIDADES RECOMENDADAS'!$Y$4:$AC$23
Columns Y-AC = 4 columns? Y, Z, AA, AB, AC = 5 columns.
Column 5 = AC.

From the inventory: Y4=?, Z4=?, AA4=?, AB4=?, AC4=?
The headers for gravedadespecifica table are not shown.

But CALCULO!E11 = VLOOKUP(A32, gravedadespecifica, 5, FALSE) returns specific gravity (column 5).

And CALCULO!C4 = VLOOKUP('CAIDA'!A20, OUTPIPES, 2, FALSE) returns fluid name (column 2 = Product name).

So the fluid in CAIDA!A20=6 gives a name, and fluid in CALCULO!A32=9 gives vapor pressure and SG.

They could be different fluids! But likely the same system.

Let me check: OUTPIPES column 2 = C = Product name.
For item 6 (if row 10), product name would be in C10.

And gravedadespecifica table: if it has the same items, column 5 (AC) would be SG.

The key question: does the workbook use MASS DENSITY (lbm/ft³) or SPECIFIC GRAVITY in the Reynolds formula?

CAIDA!G11 = 50.6*G5*G9/(G8*G10)
G9 = VLOOKUP(A20, OUTPIPES, 6) = column G = Density (lb/ft³) - explicitly labeled "Densidad lb/pie 3"
G10 = VLOOKUP(A20, OUTPIPES, 7) = column H = Viscosity (cP) - labeled "Viscosidad centipoise"

So G9 IS mass density in lbm/ft³, not specific gravity.

Therefore the formula Re = 50.6 * Q * ρ / (D * μ) with ρ in lbm/ft³ IS CORRECT.

My previous finding FIND-005 was INCORRECT. The factor 50.6 is derived for mass density, not specific gravity.

Let me confirm by computing 50.6 with exact values:
Q_ft3s_per_GPM = 1/448.8309 (since 448.8309 GPM = 1 ft³/s)
Actually: 1 ft³ = 7.48052 gal, so 1 ft³/s = 7.48052 × 60 = 448.831 GPM. Yes.

V = Q / A = (Q_GPM / 448.831) / (π/4 × (D_in/12)²) = Q_GPM × 4 × 144 / (448.831 × π × D_in²)
V = Q_GPM × 0.4085 / D_in² (approximately)

Re = ρ × V × D / μ
   = ρ_lbm_ft3 × (Q_GPM × 0.4085 / D_in²) × (D_in/12) / (μ_cP × 6.7197e-4)
   = ρ × Q × 0.4085 / (D_in × 12 × 6.7197e-4) / μ
   = ρ × Q / (D × μ) × (0.4085 / (12 × 6.7197e-4))
   = ρ × Q / (D × μ) × (0.4085 / 0.0080636)
   = ρ × Q / (D × μ) × 50.66

So 50.66 is the exact constant for ρ in lbm/ft³, Q in GPM, D in inches, μ in cP.

The workbook uses 50.6 which is correct to 3 significant figures.

CONCLUSION: FORMULA_CORRECT_WITH_DENSITY

My previous FIND-005 was wrong. The formula correctly uses mass density (lbm/ft³), not specific gravity.
The standard formula Re = 50.6 × Q × SG / (D × μ) is for when you use SG and assume ρ = 62.4 × SG.
But here ρ is explicitly the mass density from the fluid properties table.
"""

print("Reynolds derivation complete - factor 50.6 is CORRECT for mass density in lbm/ft³")