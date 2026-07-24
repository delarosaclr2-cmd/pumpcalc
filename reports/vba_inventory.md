# VBA Inventory Report (Complete)

**File:** C:\PUMPCALC\original\KEETP-60-DM-008 - HOJA DE ESPECIFICACIÓN BOMBA 005PU001 REV C (1).xlsm
**Inspection time:** 2026-07-20T14:02:47.060446
**VBA Project Size:** 78,336 bytes
**Classification:** VBA_CODE_FOUND

## VBA Modules Summary

| Module | Type | Sheet/Description | Procedures |
|--------|------|-------------------|------------|
| Hoja1.cls | Worksheet | PAGINA PRINCIPAL | Private Sub BOMBA_Click()

End Sub |
| Hoja2.cls | Worksheet | CAIDA PRESION DE TUBERIA | (empty) |
| Hoja3.cls | Worksheet | CALCULO DE BOMBA | (empty) |
| Hoja4.cls | Worksheet | TABLA DE ACCESORIOS DESCARGA | (empty) |
| Hoja12.cls | Worksheet | 005PU001 | (empty) |
| Hoja11.cls | Worksheet | RESUMEN PARA PDF | (empty) |
| Módulo1.bas | Standard Module |  | presiontub, paginaprincipal, ESPECTUBERIAS |
| ThisWorkbook.cls | ThisWorkbook |  | (empty) |
| Hoja13.cls | Worksheet | REGISTROS | (empty) |
| Módulo2.bas | Standard Module |  | TABLACC, bomba, imprimir, eliminarultimoreg |
| Módulo3.bas | Standard Module |  | (empty) |
| Módulo4.bas | Standard Module |  | RAMAL |
| Hoja5.cls | Worksheet | TABLA DE ACCESORIOS SUCCION | (empty) |
| Módulo5.bas | Standard Module |  | nuevoregistro, generareporte |
| Hoja6.cls | Worksheet | VELOCIDADES RECOMENDADAS | (empty) |
| Hoja14.cls | Worksheet | REPORTE GENERAL | (empty) |
| Módulo6.bas | Standard Module |  | Macro5, Macro6, Macro7, Macro8, Macro9 |
| Hoja7.cls | Worksheet | ESPECIFICACIÓN DE TUBERIA | (empty) |
| Hoja8.cls | Worksheet | PAGINA PRINCIPAL (2?) | (empty) |

## Detailed Procedures

### Módulo1.bas (Standard Module)
- **presiontub** (Shortcut: CTRL+w): Selects 'CAIDA PRESION DE TUBERIA' sheet
- **paginaprincipal** (Shortcut: CTRL+q): Selects 'PAGINA PRINCIPAL' sheet
- **ESPECTUBERIAS** (Shortcut: CTRL+e): Selects 'ESPECIFICACIÓN DE TUBERIA' sheet

### Módulo2.bas (Standard Module)
- **TABLACC** (Shortcut:  ): Selects 'TABLA DE ACCESORIOS' sheet
- **bomba** (Shortcut:  ): Selects 'CALCULO DE BOMBA' sheet
- **imprimir** (Shortcut: CTRL+i): Complex print setup and print macro
- **eliminarultimoreg** (Shortcut:  ): Deletes row 2 (last record)

### Módulo4.bas (Standard Module)
- **RAMAL** (Shortcut:  ): Copies calculation data from CALCULO DE BOMBA and CAIDA PRESION DE TUBERIA to RAMALES sheet, inserts columns, sets formulas

### Módulo5.bas (Standard Module)
- **nuevoregistro** (Shortcut:  ): Clears input cells across multiple sheets (CAIDA PRESION DE TUBERIA, CALCULO DE BOMBA, REPORTE GENERAL, RAMALES)
- **generareporte** (Shortcut:  ): Generates report by copying data from CAIDA PRESION DE TUBERIA and CALCULO DE BOMBA to REPORTE GENERAL

### Módulo6.bas (Standard Module)
- **Macro5** (Shortcut: Ctrl+Shift+M): Copies H6:I40 to N6 as values
- **Macro6** (Shortcut: Ctrl+Shift+V): Copies H6:I40 to R6 as values
- **Macro7** (Shortcut: Ctrl+Shift+B): Copies H6:I40 to X6 as values
- **Macro8** (Shortcut: Ctrl+Shift+N): Copies H6:I40 to AB6 as values
- **Macro9** (Shortcut: Ctrl+Shift+M): Copies H6:I40 to AF6 as values

## Sheet Module Code

### Hoja1.cls - Sheet: PAGINA PRINCIPAL
```vba
Private Sub BOMBA_Click()

End Sub
```

## Warnings from olevba

- ⚠️ AutoExec: BOMBA_Click runs when file opened and ActiveX objects trigger events
- ⚠️ Suspicious: Hex Strings detected (possible obfuscation)
- ⚠️ Suspicious: Base64 Strings detected (possible obfuscation)

## Keyboard Shortcuts Summary

| Shortcut | Macro | Module | Action |
|----------|-------|--------|--------|
| CTRL+w | presiontub | Módulo1 | Go to CAIDA PRESION DE TUBERIA |
| CTRL+q | paginaprincipal | Módulo1 | Go to PAGINA PRINCIPAL |
| CTRL+e | ESPECTUBERIAS | Módulo1 | Go to ESPECIFICACIÓN DE TUBERIA |
| CTRL+i | imprimir | Módulo2 | Print with custom setup |
| CTRL+SHIFT+M | Macro5 | Módulo6 | Copy H6:I40 to N6 (values) |
| CTRL+SHIFT+V | Macro6 | Módulo6 | Copy H6:I40 to R6 (values) |
| CTRL+SHIFT+B | Macro7 | Módulo6 | Copy H6:I40 to X6 (values) |
| CTRL+SHIFT+N | Macro8 | Módulo6 | Copy H6:I40 to AB6 (values) |
| CTRL+SHIFT+M | Macro9 | Módulo6 | Copy H6:I40 to AF6 (values) - CONFLICT |

⚠️ **Conflict:** CTRL+SHIFT+M assigned to both Macro5 and Macro9
