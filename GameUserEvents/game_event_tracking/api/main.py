from fastapi import FastAPI, HTTPException
from .models import models import InstallEventModel, PurchaseEventModel
from .firehose_client import firehose_client import FirehoseClient

STRICT_MODE = False  # optional strict validation toggle - the approach will be explained in readme.

app = FastAPI()
firehose = FirehoseClient(stream_name="game-events-firehose")


def strict_purchase_validation(event: PurchaseEventModel):
    """
    This procedure is kind of a placeholder only to do the very basic and mandatory API side validations.
    We intend to do the core business validations in side Snowflake. The error handling will have to be
    implemented appropriately in production. This proc is not called anywhere in the main program. 
    """
    errors = []

    if event.amount <= 0:
        errors.append("amount must be positive")

    if len(event.currency) != 3:
        errors.append("currency must be a standard 3 letter keyword")

    return errors


@app.post("/events/install", status_code=202)
async def install_event(event: InstallEventModel):
    try:
        firehose.send(event.model_dump())
        return {"status": "ok", "event_id": event.event_id}
    except Exception as e:
        # In production, we might log this and return a 500
        # For now, we print to stdout
        print(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")

@app.post("/events/purchase", status_code=202)
async def purchase_event(event: PurchaseEventModel):

    if STRICT_MODE:
        errors = strict_purchase_validation(event)
        if errors:
            raise HTTPException(status_code=400, detail=errors)
    try:
        firehose.send(event.model_dump())
    except Exception as e:
        # In production, we might log this and return a 500
        # For now, we print to stdout
        print(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")

    return {"status": "ok", "event_id": event.event_id}

# -----------------------
# Dev server entry point
# -----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )