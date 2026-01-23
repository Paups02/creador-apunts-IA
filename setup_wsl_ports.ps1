# Script PowerShell para configurar port forwarding de WSL a Windows
# Ejecutar como Administrador

Write-Host "Configurando port forwarding para Agente IA Documental..." -ForegroundColor Cyan

# Obtener la IP de WSL
$wslIP = bash.exe -c "hostname -I | awk '{print `$1}'"
$wslIP = $wslIP.Trim()

Write-Host "IP de WSL detectada: $wslIP" -ForegroundColor Green

# Eliminar reglas existentes (si existen)
Write-Host "`nEliminando reglas antiguas..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenport=3000 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=8000 listenaddress=0.0.0.0 2>$null

# Agregar nuevas reglas de port forwarding
Write-Host "`nCreando reglas de port forwarding..." -ForegroundColor Yellow
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=$wslIP
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=$wslIP

# Configurar reglas de firewall
Write-Host "`nConfigurando reglas de firewall..." -ForegroundColor Yellow
netsh advfirewall firewall delete rule name="WSL Frontend Port 3000" 2>$null
netsh advfirewall firewall delete rule name="WSL Backend Port 8000" 2>$null

netsh advfirewall firewall add rule name="WSL Frontend Port 3000" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="WSL Backend Port 8000" dir=in action=allow protocol=TCP localport=8000

# Mostrar configuración
Write-Host "`n=== Configuración completada ===" -ForegroundColor Green
Write-Host "`nPort forwarding activo:" -ForegroundColor Cyan
netsh interface portproxy show all

Write-Host "`n=== Instrucciones ===" -ForegroundColor Yellow
Write-Host "Ahora puedes acceder a la aplicación en:" -ForegroundColor White
Write-Host "  http://localhost:3000" -ForegroundColor Green
Write-Host "  http://127.0.0.1:3000" -ForegroundColor Green
Write-Host "`nAPI Backend en:" -ForegroundColor White
Write-Host "  http://localhost:8000" -ForegroundColor Green
Write-Host "`nPresiona cualquier tecla para abrir el navegador..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Process "http://localhost:3000"
