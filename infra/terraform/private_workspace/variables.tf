variable "subscription_id" {
  type    = string
  default = "0b3f04a9-6375-4341-a513-dd53731a99a4"
}

variable "tenant_id" {
  type    = string
  default = ""
}
variable "client_id" {
  type    = string
  default = ""
}
variable "client_secret" {
  type    = string
  default = ""
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
