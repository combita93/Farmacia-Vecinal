---
name: terraform-scaffold
description: |
  Crea un proyecto Terraform desde cero siguiendo los estándares organizacionales EST-TF-001 (estructura modular base/composición) y EST-TF-002 (etiquetado Azure). Úsala cuando el usuario quiera inicializar infraestructura Azure con Terraform para un nuevo microservicio o dominio, cuando diga frases como "crea el proyecto de Terraform para X", "necesito la infraestructura de este servicio", "arranca el terraform de este microservicio", "voy a crear la infra para...", "qué módulos de Terraform necesito para...", o cuando describa una arquitectura de servicios Azure y quiera generar el código base. El usuario describe los servicios que va a usar y cómo se conectan; la skill genera automáticamente los módulos base, el módulo de composición y los environment roots, con etiquetado corporativo obligatorio, todo conforme a EST-TF-001 y EST-TF-002.
---

# terraform-scaffold — Generador de proyectos Terraform EST-TF-001 + EST-TF-002

Tu misión es crear un proyecto Terraform completo y conforme al **EST-TF-001** y **EST-TF-002** a partir de la descripción de arquitectura que te da el usuario. El resultado es código Terraform real y funcional, con etiquetado corporativo incluido desde el inicio.

Lee **ambas** referencias antes de generar código:
- [EST-TF-001.md](references/EST-TF-001.md) — estructura modular obligatoria, restricciones y criterios de calidad.
- [EST-TF-002.md](references/EST-TF-002.md) — estándar de etiquetado (tags) en Azure: taxonomía corporativa, patrón `locals`+`merge()`, variables con validaciones y checklist de cumplimiento.

---

## Fase 1 — Entender la arquitectura

Antes de generar nada, necesitas entender qué se va a construir. Si el usuario no lo describió con suficiente detalle, pregunta:

1. **¿Qué servicios AWS vas a usar?** (Lambda, DynamoDB, SQS, S3, API Gateway, ECR, RDS, etc.)
2. **¿Cómo se conectan?** (qué servicio invoca a cuál, qué permisos necesita cada uno)
3. **¿Cuál es el nombre del dominio o microservicio?** (será el nombre del módulo de composición)
4. **¿Hay algún parámetro que varía entre entornos?** (por ejemplo: nombre de imagen ECR, capacidad de DynamoDB, timeout de Lambda)

Con esa información, antes de escribir código, presenta un **resumen de la arquitectura planificada** para que el usuario confirme:

```
## Plan de arquitectura — [nombre del dominio]

### Módulos base a crear
- modules/base/lambda/        ← función Lambda con imagen ECR
- modules/base/dynamodb/      ← tabla DynamoDB
- [otros según lo descrito]

### Módulo de composición
- modules/composition/[nombre-dominio]/
  Orquesta: Lambda → DynamoDB (permisos IAM incluidos)
  Variables de entrada: image_uri, environment, table_name

### Environment roots
- environments/dev/   → llama a composition/[nombre-dominio]
- environments/stg/   → llama a composition/[nombre-dominio]
- environments/prod/  → llama a composition/[nombre-dominio]

¿Te parece correcto? ¿Quieres ajustar algo antes de generar el código?
```

No generes código hasta que el usuario confirme el plan.

---

## Fase 2 — Generación de código

Tras la confirmación, genera los archivos en este orden:

### 0. Etiquetas (tags) — primer archivo a crear

Antes de cualquier recurso, crea `tags.tf` en el módulo de composición siguiendo **EST-TF-002 §3.2**:

```hcl
# tags.tf — módulo de composición
locals {
  base_tags = {
    Environment = var.environment
    ProjectName = var.project_name
    Owner       = var.owner_email
    CostCenter  = var.cost_center
    ManagedBy   = "Terraform"
  }

  # Incluir security_tags solo si el dominio maneja datos sensibles / secretos
  security_tags = {
    DataClassification = "Restricted"
    ContainsSecrets    = "True"
    ComplianceScope    = "None"
    PII                = "False"
  }
}
```

Y agrega al `variables.tf` del módulo de composición las variables de etiquetado con validaciones (ver **EST-TF-002 §3.3**).

Todo `resource {}` en el código generado debe incluir:
- `tags = local.base_tags` para recursos estándar.
- `tags = merge(local.base_tags, local.security_tags, {...})` para recursos críticos (Key Vault, Storage con datos, DBs).

### 1. Módulos base

Por cada servicio AWS identificado, crea la carpeta correspondiente bajo `terraform/modules/base/`. Cada módulo base sigue esta estructura:

**`main.tf`** — define el recurso AWS con variables como parámetros:
```hcl
# Ejemplo: modules/base/lambda/main.tf
resource "aws_lambda_function" "this" {
  function_name = var.function_name
  role          = var.execution_role_arn
  package_type  = "Image"
  image_uri     = var.image_uri
  timeout       = var.timeout
  memory_size   = var.memory_size

  environment {
    variables = var.environment_variables
  }

  tags = var.tags
}
```

**`variables.tf`** — toda variable con `description` y `type` obligatorios:
```hcl
variable "function_name" {
  description = "Nombre de la función Lambda"
  type        = string
}
variable "image_uri" {
  description = "URI de la imagen ECR a desplegar"
  type        = string
}
# ... resto de variables
```

**`outputs.tf`** — expone los atributos que el módulo de composición necesitará:
```hcl
output "function_arn" {
  description = "ARN de la función Lambda creada"
  value       = aws_lambda_function.this.arn
}
output "function_name" {
  description = "Nombre de la función Lambda creada"
  value       = aws_lambda_function.this.function_name
}
```

**`README.md`** — documentación del módulo:
```markdown
# Módulo base: lambda

Crea una función AWS Lambda desplegada desde una imagen de contenedor en ECR.

## Inputs
| Variable | Tipo | Requerida | Descripción |
|----------|------|-----------|-------------|
| function_name | string | sí | Nombre de la función |
| image_uri | string | sí | URI de imagen ECR |
| ...

## Outputs
| Output | Descripción |
|--------|-------------|
| function_arn | ARN de la función |
| ...

## Ejemplo de uso
\`\`\`hcl
module "my_lambda" {
  source        = "../base/lambda"
  function_name = "order-processor"
  image_uri     = "123456789.dkr.ecr.us-east-1.amazonaws.com/order-processor:latest"
  ...
}
\`\`\`
```

### 2. Módulo de composición

En `terraform/modules/composition/{nombre-dominio}/`:

**`main.tf`** — orquesta los módulos base, define permisos IAM y wiring entre servicios:
```hcl
# Llama a módulos base — NUNCA define resource {} de AWS directamente
module "processor_lambda" {
  source             = "../base/lambda"
  function_name      = "${var.domain_name}-processor-${var.environment}"
  image_uri          = var.image_uri
  execution_role_arn = aws_iam_role.lambda_exec.arn
  # ...
}

module "orders_table" {
  source     = "../base/dynamodb"
  table_name = "${var.domain_name}-orders-${var.environment}"
  # ...
}

# Permisos IAM van aquí, en la composición
resource "aws_iam_role" "lambda_exec" {
  name = "${var.domain_name}-lambda-exec-${var.environment}"
  # ...
}

resource "aws_iam_role_policy" "lambda_dynamo" {
  # permiso de Lambda para escribir en DynamoDB
  # ...
}
```

**`variables.tf`** — variables que el environment root deberá pasar:
```hcl
variable "environment" {
  description = "Entorno de despliegue (dev, stg, prod)"
  type        = string
}
variable "domain_name" {
  description = "Nombre del dominio o microservicio"
  type        = string
}
variable "image_uri" {
  description = "URI de imagen ECR para el Lambda principal"
  type        = string
}
```

**`outputs.tf`** — lo que el environment root puede necesitar consultar.

**`README.md`** — documenta la solución completa, sus inputs y un ejemplo de uso desde un environment root.

### 3. Environment roots

En `terraform/environments/{dev,stg,prod}/`:

**`main.tf`** — solo llama al módulo de composición:
```hcl
module "[nombre_dominio]" {
  source      = "../../modules/composition/[nombre-dominio]"
  environment = var.environment
  domain_name = var.domain_name
  image_uri   = var.image_uri
}
```

**`variables.tf`** — declara las variables que recibe del tfvars:
```hcl
variable "environment" {
  description = "Entorno de despliegue"
  type        = string
}
variable "image_uri" {
  description = "URI de imagen ECR"
  type        = string
}
```

**`terraform.tfvars`** — valores concretos para este entorno:
```hcl
environment = "dev"
domain_name = "[nombre-dominio]"
image_uri   = "PLACEHOLDER — completar con URI real de ECR"
```

> ⚠️ Nota en el tfvars: "Los valores sensibles (credenciales, tokens) deben gestionarse via AWS Secrets Manager o SSM Parameter Store — nunca en este archivo."

---

## Fase 3 — Resumen y próximos pasos

Al finalizar la generación, presenta:

```
## ✅ Proyecto generado

Estructura creada:
terraform/
├── modules/
│   ├── base/
│   │   ├── [servicio-1]/     ← listo
│   │   └── [servicio-2]/     ← listo
│   └── composition/
│       └── [nombre-dominio]/ ← listo
└── environments/
    ├── dev/                  ← listo
    ├── stg/                  ← listo
    └── prod/                 ← listo

## Próximos pasos

1. Completar los PLACEHOLDER en `terraform.tfvars` de cada environment con los valores reales.
2. Configurar el backend remoto (S3 + DynamoDB) en cada environment root:
   \`\`\`hcl
   terraform {
     backend "s3" {
       bucket         = "tu-bucket-de-tfstate"
       key            = "[nombre-dominio]/{env}/terraform.tfstate"
       region         = "us-east-1"
       dynamodb_table = "terraform-lock"
     }
   }
   \`\`\`
3. Ejecutar `terraform validate` en cada módulo para verificar la sintaxis.
4. Ejecutar `terraform plan` en `environments/dev/` para el primer despliegue.
5. El Arquitecto debe revisar `modules/composition/` antes del primer apply en stg/prod.
```

---

## Principios de generación

- **Sigue R-01 a R-04 sin excepción.** Ningún `resource {}` de Azure en environment roots. Ningún `resource {}` de Azure directo en módulos de composición (salvo recursos IAM/RBAC de wiring, que sí van ahí).
- **Etiquetado obligatorio (EST-TF-002).** Ningún `resource {}` puede generarse sin `tags`. El módulo de composición siempre incluye `tags.tf` con `base_tags`. Recursos críticos usan `merge(local.base_tags, local.security_tags, {...})`. Incumplir esto es un defecto bloqueante.
- **Genera código real, no placeholders vacíos.** Si no conoces el valor exacto, usa `"PLACEHOLDER — completar"` con una nota explicativa.
- **Sé explícito en los permisos RBAC/IAM.** No los omitas ni los dejes como "TODO". La composición es el lugar correcto para definirlos; ponlos aunque sean una base inicial.
- **Naming consistente.** Aplica kebab-case en directorios y snake_case en variables Terraform. Claves de etiqueta en PascalCase.
- **Un módulo de composición por dominio.** Si el usuario describe múltiples dominios independientes, crea un módulo de composición por cada uno.
- **Paridad entre environments.** Los tres `environments/*/main.tf` deben llamar al mismo módulo de composición con los mismos parámetros requeridos — solo cambian los valores en `terraform.tfvars`.
- **Checklist EST-TF-002 antes de entregar.** Antes de presentar el código generado, verifica mentalmente el checklist del §7 de `references/EST-TF-002.md`. Si algo falta, corrígelo antes de mostrar el resultado.
