variable "subscription_id" {
  type    = string
  default = "310ab569-9762-484e-8ce9-a650803297ea"
}
variable "tenant_id" {
  type    = string
  default = "16b3c013-d300-468d-ac64-7eda0820b6d3"
}
variable "client_id" {
  type    = string
  default = "78c775fe-e914-408d-8105-2ab2b2f4b775"
}
variable "client_secret" {
  type    = string
  default = "brU8Q~C2n1C2X9BD9y1busRqQaEV65AN2lOPZcdj"
}

##############################
## Resource Group Variables
##############################
variable "basename" {
  type    = string
  default = "mlopstest"
}

variable "project_code" {
  type    = string
  default = "v2"
}

variable "version_num" {
  type    = string
  default = "001"
}

variable "location" {
  type    = string
  default = "westus2"
}