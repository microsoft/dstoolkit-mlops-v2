variable "subscription_id" {
  type    = string
  default = ""
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
variable "rg_name" {
  type    = string
    validation {
        condition = (length(var.rg_name) <= 90 && length(var.rg_name) > 2 && can(regex("[-\\w\\._\\(\\)]+", var.rg_name)) )
        error_message = "Resource group name may only contain alphanumeric characters, dash, underscores, parentheses and periods."
    }
}
variable "basename" {
  type    = string
  default = ""
}

variable "project_code" {
  type    = string
  default = ""
}

variable "version_num" {
  type    = string
  default = ""
}

variable "location" {
  type    = string
  default = ""
}