
variable "region" {
  description = "Region where Code Engine project will be created"
  type        = string
  default     = "us-south"
}

variable "resource_group" {
  type    = string
  default = "Default"
  description = "Resource group where Code Engine project and application will reside. Must already exist"
}

variable "source_url" {
  type    = string
  default = "https://github.com/ibm-build-lab/milvus-rag-service.git"
  description = "Git repo source name"
}

variable "source_revision" {
  type    = string
  default = "main"
  description = "Git repo branch name"
}

variable "source_context_dir" {
  type    = string
  default = "application"
  description = "Subdirectory where Dockerfile and application files are located"
}

variable "cr_namespace" {
  type    = string
  default = ""
  description = "Container Registry namespace. Must be between 4 and 24 characters"
}

variable "cr_imagename" {
  type        = string
  description = "Build image"
  default = "milvus-rag-service"
}

variable "ce_project_name" {
  type    = string
  default = ""
  description = "Name of Code Engine project"
}

variable "ce_buildsecret" {
  type        = string
  description = "Code Engine build secret"
  default = "buildsecret"
}

variable "ce_buildname" {
  type        = string
  description = "Code Engine build name"
  default = "milvus-rag-service-build"
}

variable "ce_appname" {
  type        = string
  description = "Code Engine application name"
  default = "milvus-rag-service"
}

variable "cos_ibm_cloud_api_key" {
  type        = string
  description = "COS Bucket API Key. Service Credentials -> <bucket name>"
  default = ""
}

variable "cos_instance_id" {
  type        = string
  description = "COS Instance ID. Service Credentials -> <bucket name>. Ends with ::"
  default = ""
}

variable "cos_endpoint_url" {
  type        = string
  description = "COS endpoint. Open bucket, go into Configuration tab, public endpoint, make sure to add the https://<URL>"
  default = "https://s3.us-east.cloud-object-storage.appdomain.cloud"
}

variable "cos_auth_endpoint" {
  type        = string
  description = "COS auth . Open bucket, go into Configuration tab, public endpoint, make sure to add the https://<URL>"
  default = "https://iam.cloud.ibm.com/identity/token"
}

variable "cos_bucket_name" {
  type        = string
  description = "COS Bucket Name"
  default = "milvus-service-docs"
}

variable "default_docs_folder" {
  type        = string
  description = "default folder for local document upload"
  default = "data"
}

variable "rag_app_api_key" {
  type        = string
  description = "RAG APP User Created Key, used for API authentication"
  default = ""
}

variable "wx_project_id" {
  type        = string
  description = "watsonx.ai project id. Open the project, go to Management->General->Details"
  default = ""
}

variable "wx_url" {
  type        = string
  description = "watsonx.ai endpoint url."
  default = ""
}

variable "wx_space_id" {
  type        = string
  description = "watsonx.ai space id. Open deployments->Spaces, select the saopce and go to Management->General->Details"
  default = ""
}

variable "prompt_name" {
  type        = string
  description = "watsonx.ai prompt name."
  default = ""
}

variable "wxd_milvus_host" {
  type        = string
  description = "The GRPC hostname for Milvus"
  default = ".cloud.ibm.com"
}

variable "wxd_milvus_port" {
  type        = string
  description = "Milvus port number"
  default = ""
}

variable "wxd_milvus_user" {
  type        = string
  description = "Milvus User"
  default = "ibmlhapikey"
}

variable "wxd_milvus_password" {
  type        = string
  description = "Milvus password"
  default = ""
}

variable "wxd_milvus_collection" {
  type        = string
  description = "Milvus Collection name"
  default = ""
}


