variable "subscription_id" {
  type    = string
  default = "dbbcdca6-1b09-4291-bc2c-cf41162fdc05"
}

variable "tenant_id" {
  type    = string
  default = "5d30fd05-535c-4b0e-bd25-bb39a1c98fe3"
}
variable "client_id" {
  type    = string
  default = "d14fc959-9ec7-43c3-b26d-ef40968f031a"
}
variable "client_secret" {
  type    = string
  default = "eee8Q~~3ky0CCHc7MMTDE5g7Vnu~3TFVttwEkaM~"
}
##############################
## Resource Group Variables
##############################
variable "basename" {
  type    = string
  default = "mlops"
}

variable "project_code" {
  type    = string
  default = "v2test"
}

variable "version_num" {
  type    = string
  default = "001"
}

variable "location" {
  type    = string
  default = "westus2"
}