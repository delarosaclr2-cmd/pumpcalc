# Hydraulic Equations Inventory

This document catalogs all identified hydraulic calculations in the workbook.

## CAIDA PRESION DE TUBERIA

### CAIDA PRESION DE TUBERIA!G8
- **Variable:** Diameter (inches) - Discharge
- **Excel Formula:** `=G7*(G5/G6)^0.5`
- **Engineering Equation:** D = K * sqrt(Q/v)
- **Description:** Pipe diameter calculation from flow and velocity
- **Units:** G5=GPM, G6=ft/s, G7=const, D=inches
- **Source/Reference:** Empirical sizing formula
- **Verification Status:** PENDING

### CAIDA PRESION DE TUBERIA!V8
- **Variable:** Diameter (inches) - Suction
- **Excel Formula:** `=V7*(V5/V6)^0.5`
- **Engineering Equation:** D = K * sqrt(Q/v)
- **Description:** Pipe diameter calculation from flow and velocity
- **Units:** V5=GPM, V6=ft/s, V7=const, D=inches
- **Source/Reference:** Empirical sizing formula
- **Verification Status:** PENDING

### CAIDA PRESION DE TUBERIA!G11
- **Variable:** Reynolds Number - Discharge
- **Excel Formula:** `=50.6*G5*G9/(G8*G10)`
- **Engineering Equation:** Re = 50.6 * Q * ρ / (D * μ)
- **Description:** Reynolds number for pipe flow (imperial units)
- **Units:** Q=GPM, ρ=lb/ft³, D=inches, μ=cP
- **Source/Reference:** Imperial Reynolds formula derivation
- **Verification Status:** PENDING

### CAIDA PRESION DE TUBERIA!V11
- **Variable:** Reynolds Number - Suction
- **Excel Formula:** `=50.6*V5*V9/(V8*V10)`
- **Engineering Equation:** Re = 50.6 * Q * ρ / (D * μ)
- **Description:** Reynolds number for pipe flow (imperial units)
- **Units:** Q=GPM, ρ=lb/ft³, D=inches, μ=cP
- **Source/Reference:** Imperial Reynolds formula derivation
- **Verification Status:** PENDING

### CAIDA PRESION DE TUBERIA!G15
- **Variable:** Relative Roughness - Discharge
- **Excel Formula:** `=G14/(G12/12)`
- **Engineering Equation:** ε/D = ε_abs / D_ft
- **Description:** Relative roughness for Moody chart
- **Units:** G14=ft (absolute roughness), G12=inches (nominal diameter)
- **Source/Reference:** Standard definition
- **Verification Status:** PENDING

### CAIDA PRESION DE TUBERIA!V15
- **Variable:** Relative Roughness - Suction
- **Excel Formula:** `=V14/(V12/12)`
- **Engineering Equation:** ε/D = ε_abs / D_ft
- **Description:** Relative roughness for Moody chart
- **Units:** V14=ft (absolute roughness), V12=inches (nominal diameter)
- **Source/Reference:** Standard definition
- **Verification Status:** PENDING

### CAIDA PRESION DE TUBERIA!V16
- **Variable:** Friction Factor (Laminar) - Suction
- **Excel Formula:** `= 64/V11`
- **Engineering Equation:** f = 64/Re
- **Description:** Laminar flow friction factor (Hagen-Poiseuille)
- **Units:** Re = Reynolds number
- **Source/Reference:** Theoretical laminar flow
- **Verification Status:** PENDING

### CAIDA PRESION DE TUBERIA!G19
- **Variable:** Friction Head Loss (ft/ft) - Discharge
- **Excel Formula:** `=(((G17*G16*G9*(G5^2))/(G8^5))*2.3071)*G18`
- **Engineering Equation:** hf/L = f * (L/D) * (V²/2g) -> converted to ft/ft using Q
- **Description:** Darcy-Weisbach head loss per unit length (imperial)
- **Units:** G17=f, G16=?, G9=lb/ft³, G5=GPM, G8=inches, 2.3071=const, G18=length factor
- **Source/Reference:** Darcy-Weisbach with imperial conversions
- **Verification Status:** PENDING

### CAIDA PRESION DE TUBERIA!V19
- **Variable:** Friction Head Loss (ft/ft) - Suction
- **Excel Formula:** `=(((V17*V16*V9*(V5^2))/(V8^5))*2.3071)*V18`
- **Engineering Equation:** hf/L = f * (L/D) * (V²/2g) -> converted to ft/ft using Q
- **Description:** Darcy-Weisbach head loss per unit length (imperial)
- **Units:** V17=f, V16=?, V9=lb/ft³, V5=GPM, V8=inches, 2.3071=const, V18=length factor
- **Source/Reference:** Darcy-Weisbach with imperial conversions
- **Verification Status:** PENDING

## CALCULO DE BOMBA

### CALCULO DE BOMBA!C9
- **Variable:** Static Suction Head (ft)
- **Excel Formula:** `=500/304.8`
- **Engineering Equation:** Hs = elevation_diff_m / 0.3048
- **Description:** Static suction head from elevation difference
- **Units:** 500 = mm, 304.8 = mm/ft, result = ft
- **Source/Reference:** Geometry conversion
- **Verification Status:** PENDING

### CALCULO DE BOMBA!C12
- **Variable:** Suction Pipe Length (ft)
- **Excel Formula:** `=2.12*3.281`
- **Engineering Equation:** L_ft = L_m * 3.281
- **Description:** Suction pipe length conversion from meters to feet
- **Units:** 2.12 = meters, 3.281 = ft/m, result = ft
- **Source/Reference:** Unit conversion
- **Verification Status:** PENDING

### CALCULO DE BOMBA!C13
- **Variable:** Suction Friction Loss per ft (ft/ft)
- **Excel Formula:** `='CAIDA PRESION DE TUBERIA'!V19`
- **Engineering Equation:** hf_suction_per_ft = from suction pipe calc
- **Description:** Suction line friction loss per foot
- **Units:** ft/ft
- **Source/Reference:** From CAIDA PRESION DE TUBERIA suction calc
- **Verification Status:** PENDING

### CALCULO DE BOMBA!C14
- **Variable:** Total Suction Pipe Friction Loss (ft)
- **Excel Formula:** `=C12*C13`
- **Engineering Equation:** Hf_suction = L_suction * hf_per_ft
- **Description:** Total suction pipe friction loss
- **Units:** ft
- **Source/Reference:** Basic multiplication
- **Verification Status:** PENDING

### CALCULO DE BOMBA!E14
- **Variable:** NPSH Available (ft)
- **Excel Formula:** `=((C8+E8)*(2.31/E11))+C9-C11-C14-E9`
- **Engineering Equation:** NPSHa = (Patm + Pvessel) * 2.31/SG + Hs - Hf_acc - Hf_pipe - Pv
- **Description:** Net Positive Suction Head Available
- **Units:** C8=psia, E8=psig, 2.31=psi->ft, E11=SG, C9=ft, C11=ft, C14=ft, E9=ft
- **Source/Reference:** Standard NPSH formula
- **Verification Status:** PENDING

### CALCULO DE BOMBA!E20
- **Variable:** Hydraulic Power (HP)
- **Excel Formula:** `=(E4*C28*E11)/3960`
- **Engineering Equation:** P_hyd = Q * TDH * SG / 3960
- **Description:** Hydraulic horsepower
- **Units:** Q=GPM, TDH=ft, SG=specific gravity, 3960=constant, result=HP
- **Source/Reference:** Standard pump power formula
- **Verification Status:** PENDING

### CALCULO DE BOMBA!E21
- **Variable:** Brake Power (HP)
- **Excel Formula:** `=E20/C22`
- **Engineering Equation:** P_brake = P_hyd / η_pump
- **Description:** Power at pump shaft
- **Units:** E20=hydraulic HP, C22=pump efficiency, result=HP
- **Source/Reference:** Pump power definition
- **Verification Status:** PENDING

### CALCULO DE BOMBA!E22
- **Variable:** Brake Power (kW)
- **Excel Formula:** `=E21*0.7456`
- **Engineering Equation:** P_kW = P_HP * 0.7456
- **Description:** Brake power conversion to kW
- **Units:** HP to kW
- **Source/Reference:** Unit conversion
- **Verification Status:** PENDING

### CALCULO DE BOMBA!E23
- **Variable:** Torque (lb-ft)
- **Excel Formula:** `=(E21*5252)/1700`
- **Engineering Equation:** T = HP * 5252 / RPM
- **Description:** Shaft torque at rated speed
- **Units:** E21=HP, 5252=constant, 1700=RPM, result=lb-ft
- **Source/Reference:** Torque-power-speed relationship
- **Verification Status:** PENDING

### CALCULO DE BOMBA!E24
- **Variable:** TDH (meters)
- **Excel Formula:** `=C28*0.3048`
- **Engineering Equation:** TDH_m = TDH_ft * 0.3048
- **Description:** Total Dynamic Head in meters
- **Units:** ft to m conversion
- **Source/Reference:** Unit conversion
- **Verification Status:** PENDING

### CALCULO DE BOMBA!E25
- **Variable:** Flow (LPM)
- **Excel Formula:** `=E4*3.7854`
- **Engineering Equation:** Q_LPM = Q_GPM * 3.7854
- **Description:** Flow rate conversion to LPM
- **Units:** GPM to LPM
- **Source/Reference:** Unit conversion
- **Verification Status:** PENDING

### CALCULO DE BOMBA!E27
- **Variable:** Specific Speed (Ns)
- **Excel Formula:** `=(C29*(E4^0.5))/(E24^0.75)`
- **Engineering Equation:** Ns = N * sqrt(Q) / H^0.75
- **Description:** Pump specific speed (imperial units)
- **Units:** N=RPM, Q=GPM, H=ft, result=dimensionless (US units)
- **Source/Reference:** Specific speed definition
- **Verification Status:** PENDING

### CALCULO DE BOMBA!C28
- **Variable:** Total Dynamic Head (ft)
- **Excel Formula:** `=C11+C14+C21+C24+C26`
- **Engineering Equation:** TDH = Hf_suc_acc + Hf_suc_pipe + H_static + Hf_dis_acc + Hf_dis_pipe
- **Description:** Total Dynamic Head = sum of all head losses + static head
- **Units:** All terms in ft
- **Source/Reference:** System head summation
- **Verification Status:** PENDING

## RAMALES

### RAMALES!D10
- **Variable:** Velocity (ft/s)
- **Excel Formula:** `=(4*(D9/448.8309))/(PI()*(D8/12)*(D8/12))`
- **Engineering Equation:** V = 4Q / (πD²)
- **Description:** Flow velocity in pipe
- **Units:** D9=GPM, 448.8309=GPM->ft³/s, D8=inches, result=ft/s
- **Source/Reference:** Continuity equation
- **Verification Status:** PENDING

### RAMALES!D12
- **Variable:** Discharge Pipe Friction Loss per ft (ft/ft)
- **Excel Formula:** `=((('CAIDA PRESION DE TUBERIA'!$G$17*'CAIDA PRESION DE TUBERIA'!$G$16*'CAIDA PRESION DE TUBERIA'!$G$9*(D9^2))/(('CAIDA PRESION DE TUBERIA'!$G$7*(D9/D10)^0.5)^5))*2.3071)*'CAIDA PRESION DE TUBERIA'!$G$18`
- **Engineering Equation:** hf/L = f * (V²/2g) / D
- **Description:** Discharge pipe friction loss per unit length
- **Units:** Complex - uses friction factor, velocity, density from other sheet
- **Source/Reference:** Darcy-Weisbach via reference sheet
- **Verification Status:** PENDING

## RESUMEN PARA PDF

### RESUMEN PARA PDF!B28
- **Variable:** Total Dynamic Head (ft)
- **Excel Formula:** `=(B21+C23+C24+C25+C26)*1`
- **Engineering Equation:** TDH = H_static + Hf_suc_acc + Hf_suc_pipe + Hf_dis_acc + Hf_dis_pipe
- **Description:** Total Dynamic Head from component summation
- **Units:** All terms in ft
- **Source/Reference:** System head curve summation
- **Verification Status:** PENDING

### RESUMEN PARA PDF!D28
- **Variable:** TDH (psi)
- **Excel Formula:** `=B28/2.31`
- **Engineering Equation:** P_psi = TDH_ft / 2.31
- **Description:** Head to pressure conversion
- **Units:** ft to psi (assuming SG=1)
- **Source/Reference:** Standard conversion
- **Verification Status:** PENDING

## TABLA DE ACCESORIOS DESCARGA

### TABLA DE ACCESORIOS DESCARGA!I7
- **Variable:** Accessory Equivalent Length (ft)
- **Excel Formula:** `=((D7*F7)*($H$2^2)/(32.4*2))*H7`
- **Engineering Equation:** Leq = K * V² / (2g) * (1/D) * count? or Leq = f * L/D...
- **Description:** Equivalent length of fitting (Crane method)
- **Units:** D7=ft (from table), F7=K factor, H2=V ft/s, 32.4=2g?, H7=quantity
- **Source/Reference:** Crane TP-410 method
- **Verification Status:** PENDING

### TABLA DE ACCESORIOS DESCARGA!U41
- **Variable:** Sum of accessory losses (ft)
- **Excel Formula:** `=(SUM(U7:U40))*2.31`
- **Engineering Equation:** Total_accessory_head = sum * 2.31
- **Description:** Accessory losses converted to head
- **Units:** U7:U40=psi?, *2.31 -> ft
- **Source/Reference:** Pressure to head conversion
- **Verification Status:** PENDING

---

## Numerical Constants Audit

| Sheet | Cell | Constant | Description | Status |
|-------|------|----------|-------------|--------|
| CAIDA PRESION DE TUBERIA | G8 | 0.5 | UNVERIFIED - needs analysis | UNVERIFIED |
| CAIDA PRESION DE TUBERIA | V8 | 0.5 | UNVERIFIED - needs analysis | UNVERIFIED |
| CAIDA PRESION DE TUBERIA | G11 | 50.6 | Reynolds number constant for imperial units (Q in GPM, D in inches, ρ in lb/ft³, μ in cP) | KNOWN |
| CAIDA PRESION DE TUBERIA | V11 | 50.6 | Reynolds number constant for imperial units (Q in GPM, D in inches, ρ in lb/ft³, μ in cP) | KNOWN |
| CAIDA PRESION DE TUBERIA | V16 | 64.0 | UNVERIFIED - needs analysis | UNVERIFIED |
| CAIDA PRESION DE TUBERIA | G19 | 2.3071 | Darcy-Weisbach constant for ft head loss (imperial units) | KNOWN |
| CAIDA PRESION DE TUBERIA | V19 | 2.3071 | Darcy-Weisbach constant for ft head loss (imperial units) | KNOWN |
| CALCULO DE BOMBA | C8 | 14.7 | Standard atmospheric pressure (psi) | KNOWN |
| CALCULO DE BOMBA | C9 | 500.0 | UNVERIFIED - needs analysis | UNVERIFIED |
| CALCULO DE BOMBA | C9 | 304.8 | UNVERIFIED - needs analysis | UNVERIFIED |
| CALCULO DE BOMBA | C12 | 3.281 | Meters to feet conversion | KNOWN |
| CALCULO DE BOMBA | C12 | 2.12 | UNVERIFIED - needs analysis | UNVERIFIED |
| CALCULO DE BOMBA | E14 | 2.31 | psi to ft water conversion (1 psi = 2.31 ft H2O @ SG=1) | KNOWN |
| CALCULO DE BOMBA | E20 | 3960 | Hydraulic horsepower constant (Q*TDH*SG/3960 = HP) | KNOWN |
| CALCULO DE BOMBA | E22 | 0.7456 | HP to kW conversion (1 HP = 0.7456 kW) | KNOWN |
| CALCULO DE BOMBA | E23 | 5252 | Torque constant (HP * 5252 / RPM = lb-ft) | KNOWN |
| CALCULO DE BOMBA | E23 | 1700 | Motor speed constant (appears to be rated RPM) | KNOWN |
| CALCULO DE BOMBA | E24 | 0.3048 | Feet to meters conversion | KNOWN |
| CALCULO DE BOMBA | E25 | 3.7854 | GPM to LPM conversion (1 GPM = 3.78541 LPM) | KNOWN |
| CALCULO DE BOMBA | E27 | 0.5 | UNVERIFIED - needs analysis | UNVERIFIED |
| CALCULO DE BOMBA | E27 | 0.75 | UNVERIFIED - needs analysis | UNVERIFIED |
| TABLA DE ACCESORIOS DESCARGA | I7 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I8 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I9 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I10 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I11 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I12 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I13 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I14 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I15 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I16 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I17 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I18 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I19 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I20 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I21 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I22 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I23 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I24 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I25 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I26 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I27 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I28 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I29 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I30 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I31 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I32 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I33 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I34 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I35 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I36 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I37 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I38 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I39 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I40 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | U41 | 2.31 | psi to ft water conversion (1 psi = 2.31 ft H2O @ SG=1) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | O42 | 2.31 | psi to ft water conversion (1 psi = 2.31 ft H2O @ SG=1) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | S42 | 2.31 | psi to ft water conversion (1 psi = 2.31 ft H2O @ SG=1) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | U42 | 2.31 | psi to ft water conversion (1 psi = 2.31 ft H2O @ SG=1) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | Y42 | 2.31 | psi to ft water conversion (1 psi = 2.31 ft H2O @ SG=1) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | AC42 | 2.31 | psi to ft water conversion (1 psi = 2.31 ft H2O @ SG=1) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | AG42 | 2.31 | psi to ft water conversion (1 psi = 2.31 ft H2O @ SG=1) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I77 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I78 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS DESCARGA | I79 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| RAMALES | D10 | 448.8309 | GPM to ft³/s conversion (1 GPM = 0.002228 ft³/s, 1/0.002228 = 448.83) | KNOWN |
| RAMALES | D12 | 2.3071 | Darcy-Weisbach constant for ft head loss (imperial units) | KNOWN |
| RAMALES | D12 | 0.5 | UNVERIFIED - needs analysis | UNVERIFIED |
| TABLA DE ACCESORIOS SUCCION | I6 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I7 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I8 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I9 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I10 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I11 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I12 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I13 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I14 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I15 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I16 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I17 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I18 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I19 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I20 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I21 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I22 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I23 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I24 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I25 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I26 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I27 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I28 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I29 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I30 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I31 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I32 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I33 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I34 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I35 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I36 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I37 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I38 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| TABLA DE ACCESORIOS SUCCION | I39 | 32.4 | Velocity head constant (V²/(2g) in imperial, g=32.174 ft/s², 2g=64.348, V in ft/s, V²/64.348 = V²/32.174/2... checking: 32.4 is approximately 2g/2? Actually V²/(2g) with g=32.2 -> 64.4, half is 32.2, close to 32.4) | KNOWN |
| 005PU001 | H10 | 3.281 | Meters to feet conversion | KNOWN |
| RESUMEN PARA PDF | D13 | 3.785 | UNVERIFIED - needs analysis | UNVERIFIED |
| RESUMEN PARA PDF | D15 | 3.785 | UNVERIFIED - needs analysis | UNVERIFIED |
| RESUMEN PARA PDF | D16 | 3.785 | UNVERIFIED - needs analysis | UNVERIFIED |
| RESUMEN PARA PDF | D19 | 3.28 | UNVERIFIED - needs analysis | UNVERIFIED |
| RESUMEN PARA PDF | D20 | 3.28 | UNVERIFIED - needs analysis | UNVERIFIED |
| RESUMEN PARA PDF | D21 | 3.28 | UNVERIFIED - needs analysis | UNVERIFIED |
| RESUMEN PARA PDF | D28 | 2.31 | psi to ft water conversion (1 psi = 2.31 ft H2O @ SG=1) | KNOWN |
| VELOCIDADES RECOMENDADAS | AB5 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB5 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB6 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB6 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB7 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB7 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB8 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB8 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB9 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB9 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB10 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB10 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB11 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB11 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB12 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB12 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB13 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB13 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB14 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB14 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB15 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB15 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB16 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB16 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB17 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB17 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB18 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB18 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB19 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB19 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB20 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB20 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB21 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB21 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB22 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB22 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB23 | 3.2808 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | AB23 | 1.422 | UNVERIFIED - needs analysis | UNVERIFIED |
| VELOCIDADES RECOMENDADAS | V27 | 2.3071 | Darcy-Weisbach constant for ft head loss (imperial units) | KNOWN |
| VELOCIDADES RECOMENDADAS | V28 | 2.3071 | Darcy-Weisbach constant for ft head loss (imperial units) | KNOWN |
| VELOCIDADES RECOMENDADAS | V29 | 2.3071 | Darcy-Weisbach constant for ft head loss (imperial units) | KNOWN |
| VELOCIDADES RECOMENDADAS | V30 | 2.3071 | Darcy-Weisbach constant for ft head loss (imperial units) | KNOWN |
| REPORTE GENERAL | C16 | 0.05 | UNVERIFIED - needs analysis | UNVERIFIED |
