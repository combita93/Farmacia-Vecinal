# EST-TF-001 — Referencia rápida para auditoría

## Estructura obligatoria

```
terraform/
├── modules/
│   ├── base/
│   │   └── {servicio}/          ← un directorio por servicio AWS
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       ├── outputs.tf
│   │       └── README.md
│   └── composition/
│       └── {nombre-solucion}/   ← un directorio por dominio/solución
│           ├── main.tf
│           ├── variables.tf
│           ├── outputs.tf
│           └── README.md
└── environments/
    ├── dev/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── terraform.tfvars
    ├── stg/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── terraform.tfvars
    └── prod/
        ├── main.tf
        ├── variables.tf
        └── terraform.tfvars
```

## Responsabilidades por capa

| Capa | Contiene | NO debe contener |
|------|----------|-----------------|
| `modules/base/{svc}/` | Definición genérica de un servicio AWS | Lógica de negocio, permisos IAM inter-servicio |
| `modules/composition/{sol}/` | Llamadas a base, permisos IAM, integraciones | Valores hardcodeados de entorno |
| `environments/{env}/` | Solo llamadas al módulo de composición + vars del entorno | Bloques `resource {}` o `data {}` de AWS directos |

## Restricciones (R-01 a R-04)

**R-01** — El `environments/{env}/main.tf` solo puede contener bloques `module {}` que llamen a `modules/composition/`. Ningún bloque `resource {}` ni `data {}` de AWS está permitido en ese archivo.

**R-02** — Prohibido copiar bloques entre environments. Un cambio arquitectónico se hace UNA VEZ en el módulo de composición; los environments lo heredan automáticamente.

**R-03** — Todo recurso AWS debe estar encapsulado en un módulo base. No se permiten bloques `resource {}` de AWS directamente en módulos de composición.

**R-04** — Toda modificación en `modules/composition/{sol}/main.tf` que agregue, elimine o cambie variables o integraciones DEBE reflejarse en el mismo commit/PR en `variables.tf` y `README.md`.

## Naming conventions

- Directorios de módulos base: `modules/base/{servicio-aws}/` — kebab-case, nombre del servicio AWS
- Directorios de composición: `modules/composition/{nombre-dominio}/` — kebab-case, nombre descriptivo del dominio
- Variables: snake_case, con `description` y `type` obligatorios en todo módulo
- Valores sensibles: nunca en `terraform.tfvars` en texto plano — usar AWS Secrets Manager o SSM Parameter Store

## DoR — Módulo listo para ser consumido

- [ ] Tiene main.tf, variables.tf, outputs.tf y README.md
- [ ] Todas las variables tienen `description` y `type`
- [ ] README.md incluye descripción, inputs, outputs y ejemplo de uso
- [ ] Pasa `terraform validate` sin errores

## DoD — Cambio completado

- [ ] `terraform plan` no muestra recursos no intencionales
- [ ] Cambio aplicado desde el environment root (no desde la raíz del módulo)
- [ ] Si se modificó composición, variables.tf y README.md están actualizados
- [ ] PR aprobado por Arquitecto (módulos) o Tech Lead (environments)
- [ ] Estado en backend remoto (S3 + DynamoDB lock)

## Roles

| Rol | Responsabilidad Terraform |
|-----|--------------------------|
| Arquitecto | Diseña y mantiene `modules/composition/`. Aprueba PRs de módulos. |
| Desarrollador | Consume módulos desde `environments/dev/`. No modifica módulos sin aprobación. |
| Tech Lead / DevOps | Despliega en `stg/` y `prod/`. Valida parámetros. Aprueba PRs de environments. |
| Auditor | Verifica cumplimiento periódico. Gestiona waivers. |
