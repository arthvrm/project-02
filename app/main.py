import logging

from app.models import ClassifiedRequest
from app.services.classifier import RequestClassifier
from app.services.report import generate_report
from app.utils.config import (
    INPUT_FILE,
    LLM_MODEL,
    GEMINI_API_KEY,
    MAX_RETRIES,
    OUTPUT_FILE,
    REPORT_FILE,
)
from app.utils.file_handler import read_requests, save_json
from app.utils.logger import setup_logger


def main() -> None:
    logger = setup_logger()

    logger.info("Starting request classification pipeline")

    requests = read_requests(INPUT_FILE)

    if not requests:
        logger.warning("No requests found in CSV file.")
        return

    classifier = RequestClassifier(
        model_name=LLM_MODEL,
        api_key=GEMINI_API_KEY,
        max_retries=MAX_RETRIES,
        logger=logger,
    )

    results: list[ClassifiedRequest] = []
    failed_requests = []

    for request in requests:
        logger.info(
            "Processing request %s",
            request.id,
        )

        classification = classifier.classify(
            request.raw_text
        )

        if classification is None:
            logger.error(
                "Failed to classify request %s",
                request.id,
            )
            failed_requests.append(request)
            continue

        results.append(
            ClassifiedRequest(
                id=request.id,
                **classification.model_dump(),
            )
        )

    save_json(
        [
            result.model_dump(mode="json")
            for result in results
        ],
        OUTPUT_FILE,
    )

    generate_report(
        results=results,
        failed_requests=failed_requests,
        total_requests=len(requests),
        file_path=REPORT_FILE,
    )

    logger.info(
        "Processing completed: %d/%d requests classified",
        len(results),
        len(requests),
    )
    logger.info(
        "Output saved to %s",
        OUTPUT_FILE,
    )
    logger.info(
        "Report saved to %s",
        REPORT_FILE,
    )


if __name__ == "__main__":
    main()