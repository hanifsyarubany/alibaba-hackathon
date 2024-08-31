import time
import traceback

from py_app_service.database import mongo_instance
from py_app_service.services import (
    gtm_strategy,
    overview_builder,
    market_expansion_opportunities,
funding_community,
update_kbs
)
from py_app_service.models import OnboardModel
import asyncio

mongo_tabel = mongo_instance["business"]


async def prompting_worker():
    while True:
        try:
            # Fetch a single document where 'success' is None and 'failed' is None, ordered by 'created_at'
            _data = await mongo_tabel.find_one(
                {"success": None, "failed": None},
                sort=[("created_at", 1)],  # Sort by 'created_at' in ascending order
            )

            if _data:
                # Store the document's _id for later use
                document_id = _data["_id"]

                # Convert the document to OnboardModel, excluding _id field
                del _data["_id"]
                data = OnboardModel(**_data)

                try:
                    # Process the document
                    if not data.overview:
                        _overview = overview_builder(data.business_id, data.data)
                        _data["overview"] = _overview

                        await mongo_tabel.update_one(
                            {"_id": document_id}, {"$set": _data}
                        )

                        time.sleep(2.5)

                    if not data.market_opportunity:
                        _me = market_expansion_opportunities(
                            data.business_id, data.data
                        )
                        _data["market_opportunity"] = _me

                        await mongo_tabel.update_one(
                            {"_id": document_id}, {"$set": _data}
                        )

                        time.sleep(2.5)

                    if not data.gtm:
                        _gtm = gtm_strategy(data.business_id, data.data)
                        _data["gtm"] = _gtm
                        await mongo_tabel.update_one({"_id": document_id}, {"$set": _data})

                        time.sleep(2.5)

                    if not data.funding_community:
                        _fc = funding_community(data.business_id, data.data)
                        _data["funding_community"] = _fc
                        time.sleep(2.5)


                    # running KBS
                    update_kbs(data.business_id, data.data)

                    # Mark the document as successfully processed
                    _data["success"] = True
                    _data["failed"] = None

                    # Update the document in MongoDB
                    await mongo_tabel.update_one({"_id": document_id}, {"$set": _data})

                    print(
                        f"Document with ID {document_id} successfully processed and updated."
                    )

                except Exception as e:
                    # If an error occurs during processing, mark the document as failed
                    print(
                        f"An error occurred while processing document with ID {document_id}: {e}"
                    )
                    await mongo_tabel.update_one(
                        {"_id": document_id},
                        {"$set": {"failed": True, "error_message": str(e)}},
                    )
                    traceback.print_exc()

            else:
                # No data found, sleep for 15 seconds before checking again
                print("No matching document found. Sleeping for 10 seconds...")
                await asyncio.sleep(10)
        except Exception as e:
            print("something wrong happened - will back after 10 secs sleep: ", e)
            await asyncio.sleep(10)


def run_prompting():
    asyncio.run(prompting_worker())


if __name__ == "__main__":
    run_prompting()
