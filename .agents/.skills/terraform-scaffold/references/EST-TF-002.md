# EST-TF-002 — Estándar de Etiquetado (Tags) en Azure con Terraform

> **Fuente oficial**: [hashicorp/terraform-provider-azurerm](https://github.com/hashicorp/terraform-provider-azurerm)
> **Alineación**: Microsoft Cloud Adoption Framework (CAF) · SecOps · FinOps

---

## 1. Principios Fundamentales

Un recurso sin etiquetar es una **vulnerabilidad operativa, financiera y de seguridad**.

Las etiquetas son pares `clave = "valor"` asociados a recursos, Resource Groups o Suscripciones de Azure. Permiten clasificar, auditar, costear y automatizar el gobierno de la nube.

### 1.1 Límites técnicos de Azure

| Restricción | Límite |
|---|---|
| Pares por recurso/RG | **50 máximo** |
| Longitud de clave (Key) | 512 caracteres (128 en Storage Accounts) |
| Longitud de valor (Value) | 256 caracteres |
| Caracteres prohibidos en clave | `< > % & \ ? /` |
| Sensibilidad | Case-sensitive a nivel de ARM API |

> Si se necesitan más de 50 atributos lógicos, consolida los extras en una cadena JSON dentro de un único valor de etiqueta.

---

## 2. Taxonomía Corporativa Obligatoria

### 2.1 Etiquetas de Identificación y Gobierno

| Key | Descripción | Valores permitidos | Obligatorio |
|---|---|---|---|
| `Environment` | Entorno de despliegue | `dev`, `qa`, `uat`, `prod`, `dr` | ✅ Sí |
| `ProjectName` | Nombre del proyecto | Texto libre (ej. `ecommerce-portal`) | ✅ Sí |
| `Owner` | Correo del responsable técnico/negocio | Formato e-mail válido | ✅ Sí |
| `ManagedBy` | Herramienta de aprovisionamiento | `Terraform`, `Bicep`, `Manual` | ✅ Sí |

### 2.2 Etiquetas Financieras (FinOps)

| Key | Descripción | Formato / Valores | Obligatorio |
|---|---|---|---|
| `CostCenter` | Código contable para chargeback | Regex `^CC-[0-9]{4,6}$` | ✅ Sí |
| `BusinessUnit` | Unidad de negocio que asume el costo | `Marketing`, `Finance`, `IT-Core` | Recomendado |

### 2.3 Etiquetas de Seguridad y Cumplimiento (SecOps)

| Key | Descripción | Valores permitidos | Cuándo usarla |
|---|---|---|---|
| `DataClassification` | Nivel de sensibilidad de datos | `Public`, `Internal`, `Confidential`, `Restricted` | Cualquier recurso con datos |
| `ContainsSecrets` | Indica que el recurso alberga credenciales/llaves | `True`, `False` | Key Vaults, Storage, App Config |
| `ComplianceScope` | Marco regulatorio aplicable | `PCI-DSS`, `HIPAA`, `GDPR`, `SOX`, `None` | Recursos bajo auditoría |
| `PII` | Contiene Información de Identificación Personal | `True`, `False` | Bases de datos, Storage, Functions |

---

## 3. Implementación Técnica con Terraform

### 3.1 Provider requerido

```hcl
# provider.tf
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}
```

### 3.2 Patrón estándar: `locals` + `merge()`

Cada módulo de composición debe incluir un archivo `tags.tf` con este patrón:

```hcl
# tags.tf — va en el módulo de composición o en el environment root
locals {
  # Etiquetas base: van en TODOS los recursos
  base_tags = {
    Environment = var.environment
    ProjectName = var.project_name
    Owner       = var.owner_email
    CostCenter  = var.cost_center
    ManagedBy   = "Terraform"
  }

  # Etiquetas de seguridad: solo para recursos críticos
  # (Key Vault, Storage con datos sensibles, DBs con PII, etc.)
  security_tags = {
    DataClassification = "Restricted"
    ContainsSecrets    = "True"
    ComplianceScope    = "PCI-DSS"
    PII                = "True"
  }
}
```

**Regla de fusión:**

```hcl
# Recurso estándar — solo base_tags
tags = local.base_tags

# Recurso crítico — fusión con security_tags y etiqueta ad-hoc
tags = merge(local.base_tags, local.security_tags, {
  Description = "Bóveda central para secretos PCI-DSS"
})
```

### 3.3 Variables requeridas en `variables.tf`

```hcl
variable "environment" {
  description = "Entorno de despliegue (dev, qa, uat, prod, dr)"
  type        = string

  validation {
    condition     = contains(["dev", "qa", "uat", "prod", "dr"], var.environment)
    error_message = "Valor inválido. Permitidos: dev, qa, uat, prod, dr."
  }
}

variable "project_name" {
  description = "Nombre del proyecto (ej. ecommerce-portal)"
  type        = string
}

variable "owner_email" {
  description = "Correo del responsable técnico o de negocio"
  type        = string
}

variable "cost_center" {
  description = "Código de centro de costos. Formato: CC-XXXXXX"
  type        = string

  validation {
    condition     = can(regex("^CC-[0-9]{4,6}$", var.cost_center))
    error_message = "CostCenter debe tener formato CC-XXXXXX (4-6 dígitos)."
  }
}
```

### 3.4 Ejemplo completo: Key Vault seguro

```hcl
# keyvault.tf — dentro del módulo de composición
resource "azurerm_resource_group" "this" {
  name     = "rg-${var.project_name}-${var.environment}-eus-01"
  location = var.location
  tags     = local.base_tags
}

resource "azurerm_key_vault" "this" {
  name                       = "kv-${var.project_name}-${var.environment}-001"
  location                   = azurerm_resource_group.this.location
  resource_group_name        = azurerm_resource_group.this.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "premium"
  purge_protection_enabled   = true
  soft_delete_retention_days = 90

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
  }

  # Fusión: base + seguridad + descripción específica
  tags = merge(local.base_tags, local.security_tags, {
    Description = "Bóveda de secretos — ${var.project_name} ${var.environment}"
  })
}
```

---

## 4. Gobernanza con Azure Policy

### 4.1 Política para requerir `CostCenter` (efecto Deny)

```json
{
  "properties": {
    "displayName": "Requerir etiqueta CostCenter",
    "description": "Deniega la creación de recursos si falta la etiqueta CostCenter.",
    "mode": "Indexed",
    "parameters": {
      "tagName": {
        "type": "String",
        "metadata": { "displayName": "Tag Name" },
        "defaultValue": "CostCenter"
      }
    },
    "policyRule": {
      "if": {
        "field": "[concat('tags[', parameters('tagName'), ']')]",
        "exists": "false"
      },
      "then": { "effect": "deny" }
    }
  }
}
```

### 4.2 Herencia de etiquetas y conflicto con Terraform

Cuando Azure Policy usa el efecto `Modify` para heredar etiquetas desde un Resource Group, el siguiente `terraform plan` detectará un desajuste. Para evitar conflictos:

```hcl
resource "azurerm_something" "example" {
  # ...
  lifecycle {
    ignore_changes = [tags]
  }
}
```

> Usa `ignore_changes` **solo** si la gobernanza de etiquetas está delegada a Azure Policy.
> Si Terraform es la única fuente de verdad para tags, **no lo uses**.

---

## 5. Validación en CI/CD (Shift-Left)

### 5.1 GitHub Actions — pipeline de cumplimiento

```yaml
# .github/workflows/terraform-tag-compliance.yml
name: Terraform Tagging Compliance CI
on:
  pull_request:
    branches: ["main"]

jobs:
  validate-and-plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: "1.9.0"

      - name: Terraform Format Check
        run: terraform fmt -check

      - name: Run Checkov (Security & Tag Compliance)
        uses: bridgecrewio/checkov-action@master
        with:
          directory: ./terraform/
          framework: terraform
          external_checks_dir: ./custom-policies/

      - name: Terraform Plan
        run: terraform plan -out=tfplan
        env:
          ARM_CLIENT_ID:       ${{ secrets.ARM_CLIENT_ID }}
          ARM_CLIENT_SECRET:   ${{ secrets.ARM_CLIENT_SECRET }}
          ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
          ARM_TENANT_ID:       ${{ secrets.ARM_TENANT_ID }}
```

---

## 6. FinOps — Presupuestos y Chargeback por Etiqueta

- **Tag-based Budgets**: En Azure Cost Management, ancla presupuestos a `ProjectName` o `CostCenter`. Si el consumo supera el umbral, dispara una alerta al equipo responsable.
- **Chargeback automatizado**: Exporta el CSV de costos amortizados, agrupa por la columna `Tags_CostCenter` y cruza con tu ERP (SAP, etc.) para imputar costos a la unidad de negocio.

---

## 7. Checklist de cumplimiento

Antes de hacer `terraform apply`, verifica:

- [ ] `tags.tf` con `base_tags` presente en el módulo de composición
- [ ] Todos los `resource {}` tienen `tags = local.base_tags` (o el `merge()` correspondiente)
- [ ] Variables `environment`, `project_name`, `owner_email`, `cost_center` declaradas con validaciones
- [ ] Recursos críticos (Key Vault, Storage con datos, DBs) usan `merge(local.base_tags, local.security_tags, {...})`
- [ ] `terraform fmt -check` pasa sin errores
- [ ] Checkov / tfsec no reporta violaciones de etiquetado

---

## 8. Convenciones de nomenclatura

| Elemento | Convención |
|---|---|
| Claves de etiqueta | `PascalCase` (ej. `ProjectName`, `CostCenter`) |
| Valores de entorno | `lowercase` (ej. `dev`, `prod`) |
| Directorios Terraform | `kebab-case` |
| Variables Terraform | `snake_case` |
| Recurso con secrets | Añade siempre `ContainsSecrets = "True"` |
