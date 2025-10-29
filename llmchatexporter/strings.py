# user-facing strings for LLM Chat Exporter
# command line interface strings
APP_NAME = "LLM Chat Exporter"
DESCRIPTION = "A tool to extract and export chats from various LLM platforms."
CONTENT_CONVERTED_SAVED = "Converted content written to {arg0}."
ARG_INPUT_HELP = "Path to the input HTML file containing the chat."
ARG_OUTPUT_HELP = "Path to the output file where the exported chat will be saved."

# adapter strings
WARNING_EMPTY_TEXT_NODE = "Warning: Encountered an empty text node during parsing."
WARNING_IMG_NO_SRC = "Warning: Image tag without a source attribute found."
WARNING_ANCHOR_NO_HREF = "Warning: Anchor tag without an href attribute found."
WARNING_TABLE_NO_ROWS = "Warning: Table element contains no rows."
WARNING_TABLE_NO_COLUMNS = "Warning: Table row contains no columns."
WARNING_TABLE_INCONSISTENT_COLUMNS = (
    "Warning: Inconsistent number of columns found in table rows."
)
WARNING_UNHANDLED_NODE_TYPE = (
    "Warning: Unhandled node type {arg0} encountered during parsing."
)

# builder strings
WARNING_INVALID_TABLE_ATTRIBUTES = (
    "Warning: Table contains invalid attributes that may affect rendering."
)
WARNING_INVALID_TABLE_ROW = "Warning: Table row contains invalid data."
WARNING_LIST_ITEM_OUTSIDE_LIST = "Warning: List item found outside of a list context."
WARNING_UNHANDLED_TOKEN_TYPE = "Warning: Unhandled token type {arg0} with attributes {arg1} encountered during building."
