# IBM Cloud variables
ibmcloud_api_key = "" # See https://cloud.ibm.com/docs/account?topic=account-userapikey&interface=ui#create_user_key
region = "us-south"   # Region where this app is to be deployed
resource_group = ""   # Resource group where application is to be deployed
cr_namespace = ""     # Container Registry Namespace. Script will create if doesn't exist. Can create via "ibmcloud cr namespace-add <unique namespace>"

# Cloud Object Storage variables
cos_ibm_cloud_api_key = ""  # Retrieve this from your COS instance service credentials.  See https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-service-credentials
cos_endpoint_url = "https://s3.us-south.cloud-object-storage.appdomain.cloud" # retrieve this from the location of your bucket
cos_auth_endpoint = "https://iam.cloud.ibm.com/identity/token"
cos_bucket_name = ""
cos_instance_id = "" # Retrieve this from your COS instance service credentials.
default_docs_folder = "data"

# Watsonx.ai environment variables
wx_url = "https://us-south.ml.cloud.ibm.com"
wx_project_id = ""
wx_space_id = ""
prompt_name = ""

# Milvus variables
# The following are optional if you choose to use Watson Discovery
wxd_milvus_host = ""
wxd_milvus_port = ""
wxd_milvus_user = ""
wxd_milvus_password = ""
wxd_milvus_collection = ""


# Code Engine variables
rag_app_api_key = "" # custom key/password you create as a key to pass along to the header for the RAG app (for basic security).
ce_project_name = "" # Can be new or existing Code Engine project
source_revision = "" # Git repo branch to pull source from
source_url = "https://github.com/ibm-build-lab/milvus-rag-service.git"    # update <your_org>
