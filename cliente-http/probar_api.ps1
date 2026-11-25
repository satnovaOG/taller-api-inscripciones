<#
Ejecuta la secuencia de 9 peticiones del Paso 6 contra la API local y verifica
cada codigo de respuesta. Requiere la API levantada con datos limpios:

    .\.venv\Scripts\python.exe -m uvicorn app.main:app

Uso:
    .\cliente-http\probar_api.ps1 [-BaseUrl http://127.0.0.1:8000]
Termina con codigo 0 si todo pasa y 1 si alguna verificacion falla.
#>
param([string]$BaseUrl = "http://127.0.0.1:8000")

$ErrorActionPreference = "Stop"
$script:fallos = 0

function Invoke-Api {
    param([string]$Metodo, [string]$Ruta, $Cuerpo = $null)
    $params = @{ Uri = "$BaseUrl$Ruta"; Method = $Metodo; UseBasicParsing = $true }
    if ($null -ne $Cuerpo) {
        $params.Body = ($Cuerpo | ConvertTo-Json -Compress)
        $params.ContentType = "application/json"
    }
    try {
        $r = Invoke-WebRequest @params
        $codigo = [int]$r.StatusCode
        # La API responde UTF-8 sin charset; se decodifica a mano para conservar las tildes.
        $texto = [Text.Encoding]::UTF8.GetString($r.RawContentStream.ToArray())
    } catch {
        if ($null -eq $_.Exception.Response) { throw }
        $codigo = [int]$_.Exception.Response.StatusCode
        $texto = $_.ErrorDetails.Message
    }
    $json = $null
    if ($texto) { $json = $texto | ConvertFrom-Json }
    [pscustomobject]@{ Codigo = $codigo; Json = $json; Texto = $texto }
}

function Confirmar {
    param([int]$N, [string]$Titulo, $Resp, [int]$CodigoEsperado, [string]$DetailEsperado = $null, [bool]$ExtraOk = $true, [string]$ExtraMsg = "")
    $ok = ($Resp.Codigo -eq $CodigoEsperado)
    if ($DetailEsperado) { $ok = $ok -and ($Resp.Json.detail -eq $DetailEsperado) }
    $ok = $ok -and $ExtraOk
    $estado = if ($ok) { "OK  " } else { "FALLO"; $script:fallos++ }
    $esperado = "$CodigoEsperado"
    if ($DetailEsperado) { $esperado += " $DetailEsperado" }
    Write-Host ("[{0}] {1}. {2} -> esperado {3}, obtenido {4} {5}" -f $estado, $N, $Titulo, $esperado, $Resp.Codigo, $Resp.Texto)
    if ($ExtraMsg) { Write-Host "       $ExtraMsg" }
}

Write-Host "Probando $BaseUrl"

$r = Invoke-Api POST "/inscripciones" @{ estudiante_id = "e1"; curso_codigo = "IS2" }
$inscripcionId = $r.Json.id
Confirmar 1 "POST inscribir e1 en IS2" $r 201 -ExtraOk ($null -ne $inscripcionId) -ExtraMsg "inscripcion_id = $inscripcionId"

$r = Invoke-Api POST "/inscripciones" @{ estudiante_id = "e1"; curso_codigo = "IS2" }
Confirmar 2 "POST inscribir e1 en IS2 otra vez" $r 409 "DUPLICADA"

$r = Invoke-Api POST "/inscripciones" @{ estudiante_id = "e4"; curso_codigo = "IS2" }
Confirmar 3 "POST inscribir e4 en IS2" $r 409 "PRERREQUISITOS_PENDIENTES"

$r = Invoke-Api POST "/inscripciones" @{ estudiante_id = "e2"; curso_codigo = "IS2" }
Confirmar 4 "POST inscribir e2 en IS2" $r 201

$r = Invoke-Api POST "/inscripciones" @{ estudiante_id = "e3"; curso_codigo = "IS2" }
Confirmar 5 "POST inscribir e3 en IS2" $r 409 "SIN_CUPO"

$r = Invoke-Api GET "/inscripciones/$inscripcionId"
Confirmar 6 "GET /inscripciones/$inscripcionId" $r 200 -ExtraOk ($r.Json.id -eq $inscripcionId)

$r = Invoke-Api GET "/estudiantes/e1/inscripciones"
Confirmar 7 "GET /estudiantes/e1/inscripciones" $r 200 -ExtraOk (@($r.Json).Count -ge 1)

$r = Invoke-Api PATCH "/inscripciones/$inscripcionId" @{ estado = "CANCELADA" }
Confirmar 8 "PATCH /inscripciones/$inscripcionId a CANCELADA" $r 200 -ExtraOk ($r.Json.estado -eq "CANCELADA")

$r = Invoke-Api GET "/cursos"
$is2 = $r.Json | Where-Object { $_.codigo -eq "IS2" }
Confirmar 9 "GET /cursos (IS2 con 1 cupo disponible)" $r 200 -ExtraOk ($is2.cupos_disponibles -eq 1) -ExtraMsg "IS2 cupos_disponibles = $($is2.cupos_disponibles)"

Write-Host ""
if ($script:fallos -eq 0) { Write-Host "RESULTADO: las 9 peticiones pasaron." } else { Write-Host "RESULTADO: $($script:fallos) verificacion(es) fallaron." }
exit ([int]($script:fallos -gt 0))
