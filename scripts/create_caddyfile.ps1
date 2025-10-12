# Script PowerShell per generare il Caddyfile
# Salva come create_caddyfile.ps1 e lancia da PowerShell


$ip_server = Read-Host "Inserisci l'IP del server (es: 192.168.1.10)"
$clone_dir = Read-Host "Inserisci la directory dove hai clonato il progetto (es: E:/progetti/pareri)"

$static_dir = Join-Path $clone_dir "server/staticfiles"
$caddyfile_path = Join-Path $PSScriptRoot "Caddyfile"

$caddyfile_content = @"
http://$ip_server {
    handle /pareri/static/* {
        root * $static_dir
        file_server
    }
    handle /pareri* {
        reverse_proxy 127.0.0.1:8000
    }
    log {
        output stdout
        format console
    }
}
"@

Set-Content -Path $caddyfile_path -Value $caddyfile_content -Encoding UTF8
Write-Host "Caddyfile generato in $caddyfile_path con root static: $static_dir"
