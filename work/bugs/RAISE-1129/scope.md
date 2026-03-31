# RAISE-1129: docs.raiseframework.com caído

WHAT:      docs.raiseframework.com no sirve contenido — el sitio de documentación está caído
WHEN:      Desde que se separó el sitio marketing (raise-gtm) del de documentación
WHERE:     .github/workflows/deploy-site.yml — apunta a site/ (proyecto raise-gtm), no a docs/
EXPECTED:  docs.raiseframework.com sirve la documentación del framework, accesible y actualizada
Done when: Existe un pipeline funcional que despliega docs/ a Cloudflare Pages y el sitio responde HTTP 200
