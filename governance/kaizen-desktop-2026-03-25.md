# Kaizen: Desktop Optimization — 2026-03-25

**Epic:** RAISE-736
**Machine:** herbert (Ubuntu 24.04, GNOME, Kernel 6.17.0-19)
**Hardware:** AMD Ryzen 5 3600, 32GB RAM, NVMe

---

## 1. Nautilus Scripts — Right-click lag fix (RAISE-737)

**Problema:** El menú contextual de Nautilus tardaba minutos en responder tras instalar un pack de 245 scripts.

**Solución:** Backup completo en `~/.local/share/nautilus/scripts.bak/` y curación a 29 scripts útiles.

**Scripts conservados:**

| Categoría | Cantidad | Scripts |
|---|---|---|
| Archive | 3 | Extract here, Compress to .zip, Compress to .tar.gz |
| Audio and video | 5 | Extract audio, Convert to MP3 (192kbps), Convert to MP4, Convert to MP4 (no re-encoding), Show basic metadata |
| Document/PDF | 13 | Reduce (150/300 dpi), Combine, Split, Rotate (3), OCR (ES/EN), Extract images, Remove metadata, Convert to PDF, Convert to Markdown |
| Image | 8 | Convert to JPG/PNG/WEBP, Resize (50%/75%), Reduce (JPG 500kB), Combine into PDF, Remove metadata |

**Resultado:** Right-click instantáneo.

---

## 2. Memory Tuning — Swappiness y cache pressure (RAISE-738)

**Problema:** Con swappiness=60 (default), el kernel swapeaba agresivamente (5.1GB de 8GB usados) causando lag al cambiar entre aplicaciones y OOM kills (Claude Code fue matado el 19/03).

**Estado previo:**
- RAM: 31GB total, 18GB usados
- Swap: 5.1GB de 8GB usados
- `vm.swappiness = 60`
- `vm.vfs_cache_pressure = 100`

**Solución:** Archivo `/etc/sysctl.d/99-swappiness.conf`:
```
vm.swappiness = 10
vm.vfs_cache_pressure = 50
```

**Razonamiento:**
- `swappiness=10`: Preferir soltar file cache antes que mover procesos a swap. No 0 porque eso causa OOM kills al no tener margen de maniobra.
- `vfs_cache_pressure=50`: Retener más metadata de filesystem (dentries/inodes), útil para desarrollo con muchos archivos.

**Resultado:** Configuración permanente, aplicada sin reboot.

---

## 3. Disk Cleanup — ~48GB recuperados (RAISE-739)

| Acción | Espacio recuperado |
|---|---|
| Papelera (`~/.local/share/Trash/`) | ~24 GB |
| Caché navegadores (Chrome 13GB, Brave 1.3GB, tracker3 1.3GB, pip 825MB, shotwell 315MB, thumbnails 204MB) | ~17 GB |
| Caché snaps (Firefox 2.1GB, Brave 1.3GB) | ~3.4 GB |
| 17 revisiones de snaps deshabilitados | ~2-3 GB |
| Journal logs (vacuum a 200MB) | ~809 MB |
| Kernel 6.14.0-33 + headers + módulos | ~500 MB |
| **Total** | **~48 GB** |

**Caches preservados (regeneración costosa):**
- `~/.cache/uv/` (3.9GB) — paquetes Python, uso diario
- `~/.cache/whisper/` (3.6GB) — modelos Whisper, re-descarga lenta
- `~/.cache/pypoetry/` (1GB) — acelera builds
- `~/.cache/pnpm/` (256MB) — acelera installs Node
- `~/.cache/pre-commit/` (121MB) — hooks pre-commit

---

## 4. System Errors Resolution (RAISE-740)

### Canonical Livepatch — Deshabilitado
- Fallaba constantemente (502 Bad Gateway, timeouts POST a livepatch.canonical.com)
- Sin suscripción activa de Ubuntu Pro
- `sudo canonical-livepatch disable`

### pam_lastlog.so — Referencia huérfana eliminada
- `/etc/pam.d/login` referenciaba `pam_lastlog.so` que nunca existió en Ubuntu 24.04
- Módulo reemplazado por `pam_systemd` + `systemd-logind`
- Línea comentada: `#session    optional   pam_lastlog.so`

### Hallazgos documentados (no accionados)
- **OOM Kill (Mar 19):** Claude Code matado por kernel, consumió 11GB. Mitigado con swappiness tuning.
- **brcmfmac WiFi:** Firmware incompleto para BCM4366 (no clm_blob). WiFi funciona pero con canales limitados. Bajo impacto.
- **Rambox AppArmor:** Snap no puede llamar `gnome-session.Inhibit` ni ejecutar `df`. Limitación del confinamiento snap, no resoluble sin cambio del publisher.
- **ata3 softreset:** Puerto SATA no responde en resume de suspensión. Probablemente puerto vacío o lector óptico. Ralentiza resume ligeramente.

---

## Lecciones

1. **Script packs:** Instalar packs sin curar es deuda técnica inmediata. Siempre curar al instalar.
2. **Defaults de Ubuntu:** swappiness=60 es agresivo para workstations con mucha RAM. El kernel prioriza caché de archivos sobre responsividad de apps.
3. **Limpieza periódica:** 48GB acumulados sin limpieza deliberada. Considerar kaizen mensual de desktop.
4. **sudo en Claude Code:** El sandbox de Claude Code no comparte sesión TTY/PAM con el usuario. No es posible usar sudo directamente, ni con `dangerouslyDisableSandbox` ni cacheando credenciales con `sudo -v`. Workaround: usuario ejecuta comandos sudo via prefijo `!`.
