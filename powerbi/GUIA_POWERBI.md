# Construcción del informe en Power BI Desktop

## 1. Conectar al modelo dimensional

Inicio → Obtener datos → Base de datos PostgreSQL. Servidor: `localhost:5432`. Base: `proy_airbnb_rio`. Seleccionar **Importar** y autenticación de base de datos con el usuario y contraseña de tu PostgreSQL. Mantener las credenciales en el diálogo, no en archivos de código.

En Navegador selecciona las 10 tablas del esquema `bi`. En Power Query, utiliza estos nombres de consulta, sin prefijo `bi`, para que coincidan con las medidas: `dim_barrio`, `dim_tipo_alojamiento`, `dim_tipo_propiedad`, `dim_capacidad`, `dim_anfitrion`, `dim_fecha`, `dim_corte`, `fact_oferta`, `metricas_modelo`, `importancia_variables`.

Comprueba que `anuncio_id`, `host_id` y `corte_id` sean **Texto**. Son identificadores, no cantidades. Los precios deben ser numéricos y las fechas de tipo Fecha. Cerrar y aplicar.

## 2. Relaciones y granularidad

Grano de `fact_oferta`: un anuncio en un corte. En esta entrega hay un solo corte. Crea o comprueba estas relaciones activas 1:* con filtro en una dirección, dimensión → hecho:

| Dimensión, columna única | Columna de fact_oferta |
|---|---|
| dim_barrio[barrio_key] | barrio_key |
| dim_tipo_alojamiento[tipo_alojamiento_key] | tipo_alojamiento_key |
| dim_tipo_propiedad[tipo_propiedad_key] | tipo_propiedad_key |
| dim_capacidad[capacidad_key] | capacidad_key |
| dim_anfitrion[anfitrion_key] | anfitrion_key |
| dim_fecha[fecha_key] | fecha_key |
| dim_corte[corte_id] | corte_id |

`metricas_modelo` e `importancia_variables` quedan **sin relaciones**. Son resultados globales de una ejecución, no observaciones individuales. Sus visuales no responden a los filtros de barrio; indícalo. Para métricas filtrables usa las medidas basadas en `fact_oferta`.

No relaciones dimensiones entre sí. Revisa las relaciones detectadas automáticamente y evita rutas adicionales o muchos-a-muchos. Oculta las claves técnicas. Ordena `dim_capacidad[grupo_capacidad]` por `orden` y `dim_fecha[mes_nombre]` por `mes`.

## 3. Medidas y formatos

Abre `medidas_airbnb.dax` y crea cada medida por separado con Modelado → Nueva medida. El archivo completo no se pega como una sola medida. Los nombres de tablas deben coincidir con el apartado 1.

Formato moneda BRL/R$ para precios, MAE, RMSE y error mediano; 2 decimales. Formato porcentaje para cobertura, mejora MAE y desviación relativa. R² es un número decimal, no un porcentaje de aciertos.

No uses SUMA para precios ni para latitud/longitud. Los indicadores de error solo contienen datos para prueba; los registros de desarrollo y sin precio tienen errores NULL. No presentes diferencias de desarrollo como evidencia de precisión fuera de muestra.

## 4. Páginas propuestas

### Mercado y oferta

Tarjetas: Anuncios, Anfitriones, Anuncios con precio y Cobertura de precio. Barras: anuncios por barrio y por tipo de alojamiento. Segmentadores: barrio, tipo, propiedad y capacidad. Muestra el corte y las fechas de recopilación. Son anuncios observados; no equivalen a reservas ni a viviendas únicas verificadas.

### Precios y segmentos

Tarjetas: Mediana y Promedio del precio publicado, Cobertura de precio. Matriz: barrio → tipo → grupo de capacidad, con anuncios, anuncios con precio y mediana. Incluye el tamaño de cada grupo; 30 precios es una regla de presentación, no una garantía estadística. Utiliza BRL. Las medianas de grupos no son aditivas.

Si usas un mapa, utiliza latitud y longitud de la tabla de hechos, con categoría de datos correspondiente y sin sumar. Los contornos o nombres de barrio no verifican por sí solos la pertenencia espacial.

### Comparación experimental de precios

Tabla de detalle: anuncio_id, barrio, tipo, capacidad, precio publicado, precio estimado, desviación relativa, partición del modelo y soporte bajo. Encabezado: **Estimación experimental del precio anunciado**. El signo de la desviación solo describe diferencia frente al modelo; no demuestra sobreprecio, infravaloración ni rentabilidad.

Identifica los casos de entrenamiento/validación, los de prueba y los que no tienen precio observado. No mezcles sus errores en una tarjeta. Un segmento con menos de 30 comparables de desarrollo se marca con soporte bajo, no con una probabilidad de error.

### Evaluación y calidad

Tarjetas dinámicas de prueba: Anuncios evaluados, MAE, MAE referencia, Mejora MAE, Error mediano, RMSE y R². En otro bloque, claramente rotulado, muestra MAE de sensibilidad y su población. Añade alertas de capacidad, noches y precio ausente. Usa `importancia_variables` para una barra con el aumento del MAE al permutar; no es una interpretación causal.

Controles iniciales sin filtros: 48 247 anuncios, 44 147 con precio, 4 100 sin precio, 9 206 anuncios evaluados, MAE BRL 594,06, MAE referencia BRL 758,79, mejora 21,71 %, RMSE BRL 8 757,65 y R² 0,01514. Sensibilidad: 9 098 anuncios y MAE BRL 297,94. Estos valores deben coincidir con los informes de la ejecución recibida; si cambias el modelo, revisa la versión y los nuevos controles.

## 5. Límites que deben quedar visibles

El precio es anunciado. El modelo fue evaluado en anfitriones reservados del mismo corte ya explorado, sin validación temporal o externa. Su R² global es bajo; las estimaciones acompañan el análisis descriptivo y requieren revisión individual. El subconjunto hasta P99 no sustituye la evaluación completa.

`dim_fecha` contiene un calendario para relacionar la fecha de recopilación. No convierte este corte en una serie histórica ni permite afirmar cambios mensuales, estacionalidad o demanda. La disponibilidad del anuncio no es ocupación observada.

## 6. Guardar y revisar

Guarda el informe como `powerbi/Airbnb_Rio_Analisis.pbix`. Verifica primero tarjetas sin filtros y luego un filtro de barrio. Las medidas de prueba pueden quedar en blanco si un filtro no deja casos evaluados; no sustituyas esos blancos por un resultado inventado.

Documentación: https://learn.microsoft.com/en-us/power-query/connectors/postgresql y https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
