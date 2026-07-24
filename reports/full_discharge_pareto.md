# Full Discharge Pareto Analysis

## PARETO_LEQ_ONLY (denominator = 3.4583148148 ft)

Only the standard Leq formula column (I/O column) contributions.

| # | Row | Accessory | Loss (ft) | % of Leq Total | Cumulative % | Method |
|---|---|---|---|---|---|---|
| 1 | 15 | Valvula de angulo de Retencion | 2.568056 | 74.26% | 74.26% | LEQ_OVER_D |
| 2 | 39 | Codo  Soldado 90 (Radio Largo) | 0.616333 | 17.82% | 92.08% | LEQ_OVER_D |
| 3 | 7 | Valvula de Compuerta 100% Abierta | 0.273926 | 7.92% | 100.00% | LEQ_OVER_D |
| 4 | 8 | Valvula de Compuerta 1/2 Cerrada | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 5 | 9 | Valvula de Compuerta 3/4 Cerrada | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 6 | 10 | Valvula de Globo 100% Abierta | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 7 | 11 | Valvula de Globo  1/2 Cerrada | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 8 | 12 | Valvula de Globo de Retencion (Check) | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 9 | 13 | Valvula de Globo Vertical de Retencion | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 10 | 14 | Valvula de Angulo | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 11 | 16 | Valvula Check de Balancin | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 12 | 17 | Valvula Check de Levante | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 13 | 18 | Valvula Check de Disco | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 14 | 19 | Valvula de Pie con Colador de Visagra | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 15 | 20 | Valvula de Pie con Colador de Cabezal | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 16 | 21 | Valvula de Bola | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 17 | 22 | Valvula de Mariposa | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 18 | 23 | Valvula de Macho de Mariposa 3 vias | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 19 | 24 | Valvula Macho (Tapon) | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |
| 20 | 25 | Codo Roscado 90 | 0.000000 | 0.00% | 100.00% | LEQ_OVER_D |

## PARETO_FULL_DISCHARGE_TOTAL (denominator = 188.5586148148 ft)

Each row contribution + each pressure entry listed individually.

| # | Type | Row | Accessory | Loss (ft) | % of Full Total | Cumulative % | Column | Source |
|---|---|---|---|---|---|---|---|---|
| 1 | U_COLUMN_PRESSURE | 40 | Codo Soldado 45 ( Radio Largo) | 184.268700 | 97.72% | 97.72% | U (pressure * 2.31) | U_COLUMN_PRESSURE |
| 2 | O_COLUMN_LEQ | 15 | Valvula de angulo de Retencion | 2.568056 | 1.36% | 99.09% | O (Leq formula group 1) | O_COLUMN_LEQ |
| 3 | U_COLUMN_PRESSURE | 39 | Codo  Soldado 90 (Radio Largo) | 0.831600 | 0.44% | 99.53% | U (pressure * 2.31) | U_COLUMN_PRESSURE |
| 4 | O_COLUMN_LEQ | 39 | Codo  Soldado 90 (Radio Largo) | 0.616333 | 0.33% | 99.85% | O (Leq formula group 1) | O_COLUMN_LEQ |
| 5 | O_COLUMN_LEQ | 7 | Valvula de Compuerta 100% Abierta | 0.273926 | 0.15% | 100.00% | O (Leq formula group 1) | O_COLUMN_LEQ |
