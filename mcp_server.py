from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.server.fastmcp.prompts import base


mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_document(
    doc_id: str = Field(description="ID of the document to read"),
):
    """
    Reads the contents of a document by its ID.
    """
    if doc_id in docs:
        return docs[doc_id]
    else:
        raise ValueError(f"Document with ID '{doc_id}' not found.")


@mcp.tool(
    name="edit_doc",
    description="Edit a document by replacing a string in the document with another string.",
)
def edit_document(
    doc_id: str = Field(description="ID of the document to edit"),
    old_string: str = Field(
        description="String to be replaced in the document. The text must match exactly including whitespace."
    ),
    new_string: str = Field(
        description="New text to insert in place of the old text in the document"
    ),
):
    """
    Edits a document by replacing a string with another string.
    """
    if doc_id in docs:
        if old_string in docs[doc_id]:
            docs[doc_id] = docs[doc_id].replace(old_string, new_string)
            return f"Document '{doc_id}' updated successfully."
        else:
            raise ValueError(
                f"String '{old_string}' not found in document '{doc_id}'."
            )
    else:
        raise ValueError(f"Document with ID '{doc_id}' not found.")


@mcp.resource(
    "docs://documents",
    mime_type="application/json",
)
def list_docs() -> list[str]:
    """
    Lists all document IDs available in the folder.
    """
    return list(docs.keys())


@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain",
)
def get_doc(doc_id: str) -> str:
    """
    Returns the contents of a specific document by its ID.
    """
    if doc_id in docs:
        return docs[doc_id]
    else:
        raise ValueError(f"Document with ID '{doc_id}' not found.")


@mcp.prompt(
    name="format",
    description="Rewrites the contents of a document in Markdown format.",
)
def format_doc(
    doc_id: str = Field(description="ID of the document to format"),
) -> list[base.Message]:
    prompt = f"""
            Your goal is to reformat a document to be written with markdown syntax.

            The id of the document you need to reformat is:
            <document_id>
            {doc_id}
            </document_id>

            Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
            Use the 'edit_document' tool to edit the document. After the document has been reformatted...
            
            """

    return [base.UserMessage(prompt)]


# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
