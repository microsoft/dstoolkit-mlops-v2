# ⚠️ DEPRECATED: Bicep Infrastructure

**Status:** This Bicep implementation is **no longer actively maintained** as of December 2025.

## Why Deprecated?

This project has standardized on **Terraform** for infrastructure provisioning to:
- Maintain a single source of truth
- Reduce maintenance burden
- Avoid configuration drift between two IaC tools

## Migration Path

**Use Terraform instead:**
- See [`../terraform/`](../terraform/) for the actively maintained infrastructure code
- See [`.github/workflows/infra_provision_terraform.yml`](../../.github/workflows/infra_provision_terraform.yml) for the deployment workflow

## Legacy Files

These files are kept for reference only and may be out of sync with current infrastructure requirements:
- [`public_workspace/`](public_workspace/) - Bicep modules and main template

---

For questions or issues, please use Terraform for all infrastructure provisioning.
