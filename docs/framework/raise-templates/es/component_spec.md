# Especificación de Componente: [NombreComponente]

**Funcionalidad/Historia de Usuario/Diseño Técnico Relacionado:** [Enlace o ID]

**Propósito:**
*(Describa la función principal del componente y su rol dentro de la aplicación o funcionalidad.)*

**Interfaz de Props:**
*(Defina las propiedades de entrada del componente usando un formato tipo TypeScript. Adhiérase a las convenciones del proyecto, ej., `iNombreComponenteProps`).*

```typescript
interface iNombreComponenteProps {
  /** Descripción del prop */
  nombreProp: string;

  /** Descripción del prop opcional */
  propOpcional?: number;

  /** Prop con valor por defecto */
  propConDefecto?: boolean = false;

  /** Prop de función callback */
  onEvento: (datos: any) => void;

  /** Prop de tipo complejo */
  datosComplejos: {
    id: string;
    valor: number;
  };

  /** Prop children si aplica */
  children?: React.ReactNode;
}
```

**Estado (Interno):**
*(Describa cualquier estado interno significativo manejado por el componente, si aplica.)*

*   `variableEstado`: (Tipo: `boolean`) - Propósito: [ej., Rastrea el estado de carga]
*   `otroEstado`: (Tipo: `string[]`) - Propósito: [ej., Almacena elementos obtenidos]

**Eventos Emitidos / Callbacks:**
*(Detalle los eventos que el componente emite o los props callback que invoca, incluyendo los datos pasados.)*

*   `onEvento(datos)`: Activado cuando [ej., el usuario hace clic en el botón guardar]. Pasa objeto `datos` conteniendo [ej., valores actuales del formulario].
*   `onCerrar()`: Activado cuando [ej., se hace clic en el icono de cerrar del modal]. No pasa argumentos.

**Apariencia Visual y Comportamiento:**

*   **Estado por Defecto:** *(Describa la apariencia y comportamiento del componente por defecto. Enlace a mockups de diseño si están disponibles.)*
*   **Variantes/Estados:**
    *   **Estado de Carga:** *(¿Cómo se ve/comporta mientras carga datos?)*
    *   **Estado de Error:** *(¿Cómo muestra los errores?)*
    *   **Estado Deshabilitado:** *(Apariencia y comportamiento cuando está deshabilitado.)*
    *   *(Agregar otros estados relevantes, ej., Activo, Seleccionado)*
*   **Responsividad:** *(¿Cómo se adapta el componente a diferentes tamaños de pantalla?)*

**Accesibilidad (a11y):**

*   **Navegación por Teclado:** *(Describa el orden esperado de tabulación, interacciones por teclado (ej., Enter/Espacio activa acción).)*
*   **Atributos ARIA:** *(Especifique roles, estados y propiedades ARIA necesarios (ej., `role="dialog"`, `aria-modal="true"`, `aria-labelledby="tituloDialogo"`).)*
*   **Gestión del Foco:** *(Cómo se maneja el foco, especialmente para modales o contenido dinámico.)*

**Ejemplo de Uso:**
*(Proporcione un fragmento de código simple mostrando cómo usar el componente.)*

```typescript
<NombreComponente
  nombreProp="Ejemplo"
  onEvento={(datos) => console.log('Evento activado:', datos)}
  datosComplejos={{ id: 'abc', valor: 123 }}
/>
```

**Notas:**
*(Cualquier detalle adicional de implementación, dependencias, consideraciones de rendimiento o casos extremos potenciales.)* 