import azure.functions as func
import logging
import requests
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("sharepoint_download triggered")
    LOGIC_APP_URL = "https://prod-16.southcentralus.logic.azure.com:443/workflows/b62ef267419d4d34b103a56b7060ae53/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=yLVEybUg5j4cOnSMzmqMSfFOJ5P-KJRNGd6sh2CJpLk"
    # ---- 1. read filePath ----
    file_path = req.params.get("filePath")
    if not file_path:
        try:
            file_path = req.get_json().get("filePath")
        except Exception:
            return func.HttpResponse("Missing filePath", status_code=400)

    # ---- 2. POST to Logic App ----
    la_resp = requests.post(LOGIC_APP_URL, json={
                            "filePath": file_path}, stream=True)

    if la_resp.status_code != 200:
        return func.HttpResponse(
            f"Logic App error {la_resp.status_code}", status_code=la_resp.status_code
        )

    # ---- 3. send bytes back to caller ----
    filename = file_path.split("/")[-1]
    return func.HttpResponse(
        body=la_resp.content,
        status_code=200,
        headers={
            # If your Logic App already sets Content‑Type, you can forward it:
            "Content-Type": la_resp.headers.get("Content-Type", "application/pdf"),
            # Force a download; remove “attachment;” to open inline
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
