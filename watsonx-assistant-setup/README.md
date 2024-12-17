# Steps to Connect this Application to watsonx Assistant

You connect your assistant by using the api specification to add a custom extension.

### Download the api specification

Download the [milvus-service-openapi.json](./milvus-service-openapi.json) specification file. 

Use this specification file to create and add the extension to your assistant.

### Build and add extension

1.  In your assistant, on the **Integrations** page, click **Build custom extension** and use the `milvus-service-openapi.json` specification file to build a custom extension named `Milvus Service App`. For general instructions on building any custom extension, see [Building the custom extension](https://cloud.ibm.com/docs/watson-assistant?topic=watson-assistant-build-custom-extension#building-the-custom-extension).

1.  After you build the extension, and it appears on your **Integrations** page, click **Add** to add it to your assistant. For general instructions on adding any custom extension, see [Adding an extension to your assistant](https://cloud.ibm.com/docs/watson-assistant?topic=watson-assistant-add-custom-extension).

1.  In **Authentication**, choose **OAuth 2.0**. Select **Custom apikey** as the grant type in the next dropdown, and then copy and paste the value you set for **RAG_APP_API_KEY** in your environment variables.

1.  In **Servers**, under **Server Variables**, add the url (without the https) for your hosted application as `llm_route`. 

If you add apis and capabilities to this application, feel free to add them to the openapi specification. The application is intended to be an example of how to get started. If you add APIs after the Actions have been loaded, you will need to download your Actions, upload the new Open API spec and re-upload your Actions.

## Upload sample actions

This utility includes [a JSON file with sample actions](./milvus-service-app-actions.json) that are configured to use the `rag-app` extension.

Use **Actions Global Settings** (see wheel icon top right of **Actions** page) to upload the `milvus-service-app-actions.json` to your assistant. For more information, see [Uploading](https://cloud.ibm.com/docs/watson-assistant?topic=watson-assistant-admin-backup-restore#backup-restore-import). You may also need to refresh the action **Preview** chat, after uploading, to get all the session variables initialized before these actions will work correctly.


**NOTE**: If you import the actions _before_ configuring the extension, you will see errors on the actions because it could not find the extension. Configure the extension (as described [above](#prerequisites)), and re-import the action JSON file.

| Action                        | Description                                                                                                                                                                                   |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Query Milvus + LLM | Connects to the `queryLLM` API which queries Milvus using user inputted question and passes resulting documents into LLM for a natural language response. |
| No Action Matches | This is created by watsonx Assistant, but for this starter kit it is configured to trigger the "Query ES + LLM" as a sub-action using the defaults and the user input. |


### Session variables

These are the session variables used in this example.


### Additional Action Files
