# standards
import logging
import os
from dotenv import load_dotenv

from openai import OpenAI

# customs
from openaimcp import create_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OpenAI configuration
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

# Initialize OpenAI client
openai_client = OpenAI()


def main():
    """Main function to start the MCP server."""
    # Verify OpenAI client is initialized
    if not openai_client:
        logger.error(
            "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
        )
        raise ValueError("OpenAI API key is required")

    logger.info(f"Using vector store: {VECTOR_STORE_ID}")

    # Create the MCP server
    server = create_server()

    # Configure and start the server
    logger.info("Starting MCP server on 0.0.0.0:8000")
    logger.info("Server will be accessible via SSE transport")

    try:
        # Use FastMCP's built-in run method with SSE transport
        server.run(transport="sse", host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()