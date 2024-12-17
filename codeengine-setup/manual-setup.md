# Deploying in Code Engine using the manual method

1. Log into [IBM Cloud](cloud.ibm.com)

1. Create an IBM Cloud API Key.  See [Creating and IBM Cloud API Key](https://www.ibm.com/docs/en/app-connect/container?topic=servers-creating-cloud-api-key)

1. Create an image container registry namespace

    Open the IBM Cloud Shell from the IBM Cloud Console (4th icon from the top right, looks like a console window).
    
    Run the command:
    ```
    ibmcloud cr namespace-add <cr namespace>
    ```
    This must be unique globally, so choose something like <company-name>-rag-app-images.  The name needs to be between 4 and 30 characters.
    
1. Navigate to **Code Engine**

    Follow this link to get to Code Engine: https://cloud.ibm.com/codeengine/projects

    Create a new project, click the blue **Create** button

1. Create secrets within the project

    Take the **Secrets and configmaps** link, 
    
    **Registry secret**
    - Select **Create**
    - Select **Registry secret**, then **Next**
    - Enter a secret name, like `build-secret`
    - For **Target registry** choose `Other`
    - For **Registry server** enter `us.icr.io`
    - For **Password** enter your IBM Cloud API Key 
    - Select **Create**

    If your git repo is private, create an **SSH secret**
    - Select **Create**
    - Select **SSH secret**, then **Next**
    - Enter a secret name, like `my-ssh`
    - Enter the contents of your SSH **private** key, generated on your local machine using the `ssh keygen -t rsa` command. Note you have to have created an SSH key on your [github.ibm.com](github.ibm.com) (or other GHE repository) user (go into **Settings** -> **SSH and GPG Keys** on your github user profile. Add a new SSH key with your `id_rsa.pub` contents)
    - Select **Create**

1. Create an Application

    Navigate to the **Applications** tab within **Code Engine** on the left side and click **Create**.

    - Provide a name for the Application, i.e. `milvus-rag-service`
    - Choose **Build container image from source code**
    - Choose **Specify build details**
    - Under the **Source** tab:
        - **Name**: something like `milvus-rag-service`
        - **Code repo URL**:
            - if repo is private, use the SSH repo format i.e. `git@github.com:<org>/milvus-rag-service`
            - if repo is public, use HTTPS repo format, i.e. `https://github.com/<org>/milvus-rag-service`
        - **SSH Secret**
            - if repo is private, choose the SSH secret you created in step above,
            - if repo is public, choose "None"
        - **Branch name**: the branch that contains the source code, usually `main`
        - **Context directory**: add `application`
        - Select **Next**
    - Under the **Strategy** tab:
        - Choose name of **Dockerfile**
        - Choose timeout value (we used 15m)
        - Choose Build resources (we used XL)
        - Select **Next**
    - Under **Output** tab
        - Enter `us.icr.io` for the **Registry server**
        - Set **Registry secret** to the **Registry secret** created in step above
        - Set **Namespace** to the container registry namespace you created in step 3 above
        - Add a name for **Repository** like `milvus-rag-service`
        - Optional, add a Tag like `latest`
        - Select **Done**
    - Change the **Ephemeral storage** to 2.04
    - Limit the Autonscaling to 1 and 1
    - Select **Domain mappings** to **Public**.
    - Under the **Optional settings**, **Environment variables**, create the variables with the credentials based on the [env](../application/env) file
    - Under **Optional settings**, **Image start options** change the **Listening port** to 4050
    - Finally click **Create**
  
