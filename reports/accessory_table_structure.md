# Accessory Table Structure

| Property | Suction | Discharge |
|---|---|---|
| sheet_name | TABLA DE ACCESORIOS SUCCION | TABLA DE ACCESORIOS DESCARGA |
| dimensions | A1:AA115 | A1:BS163 |
| data_rows | 34 (rows 6-39) | 34 (rows 7-40) |
| total_formula | I40 = SUM(I6:I39) | I41 = O41+S41+U41+Y41+AC41+AG41 |
| base_formula | =((D*F)*(V6^2)/(32.4*2))*H | =((D*F)*(H2^2)/(32.4*2))*H |
| g_approximation | 32.4 (vs 32.174 standard) | 32.4 (vs 32.174 standard) |
| active_leq_rows | 1 | 3 of 34 |
| pressure_entries | 0 | 2 (U39=0.36 PSI, U40=79.77 PSI) |
| leq_formula_total_ft | 0.0168248889 | 3.4583148148 |
| pressure_total_ft | 0.000000 | 185.100300 |
| excel_total_ft | 0.0168248889 | 188.5586148148 |
