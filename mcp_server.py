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
            You are a document conversion specialist tasked with rewriting documents in Markdown format. Your goal is to take the content of a given document and convert it into well-structured Markdown, preserving the original meaning and enhancing readability.

            Here is the identifier of the document you need to convert:
            <document id>
            {{doc_id}}
            </document id>

            Instructions:
            1. Retrieve the content of the document associated with the given document_id.
            2. Analyze the structure and content of the document.
            3. Convert the document to Markdown format, following these guidelines:
            - Use appropriate header levels (# for main titles, ## for subtitles, etc.)
            - Properly format lists (both ordered and unordered)
            - Use emphasis (*italic* or **bold**) where appropriate
            - Add links and images using Markdown syntax if present in the original document
            - Preserve any special formatting or structure that's important to the document's meaning

            Before providing the final Markdown output, in <document analysis> tags:
            - Identify the main sections and subsections of the document
            - Count the number of sections and subsections to ensure proper nesting of headers

            This will help ensure a thorough and well-organized conversion.

            After your analysis, present the converted document in Markdown format. Use triple backticks (```) to denote the beginning and end of the Markdown content.

            Example output structure:
            <document analysis>
            <Your analysis of the document structure and conversion plan>
            </document analysis>

            ```markdown
            # Document Title

            ## Section 1
            Content of section 1...

            ## Section 2
            Content of section 2...

            - List item 1
            - List item 2

            [Link text](https://example.com)  
            ![Image description](image-url.jpg)
            ```
            Please proceed with your analysis and conversion of the document.
        """

    return [base.UserMessage(prompt)]


@mcp.prompt(
    name="summarize",
    description="Summarizes the contents of a document.",
)
def summarize_doc(
    doc_id: str = Field(description="ID of the document to summarize"),
) -> list[base.Message]:
    prompt = f"""
            You are a professional document analyst and summarization expert. Your task is to read the document associated with the given identifier and produce a clear, structured summary that captures the core ideas and major takeaways.

            Here is the identifier of the document you need to summarize:
            <document id>
            {doc_id}
            </document id>

            Instructions:
            1. Retrieve the content of the document using the provided document_id.
            2. Read and understand the structure, tone, and purpose of the document.
            3. Create a summary that highlights the key points, sections, and arguments in your own words, while preserving the original intent.

            Before presenting the summary, include a breakdown in <document structure> tags:
            - List the main sections of the document
            - For each section, briefly state its purpose or focus
            - Include a section and subsection count to confirm document complexity

            Then provide the actual summary inside <document summary> tags.
            - Keep the tone neutral and informative
            - Use bullet points or paragraphs based on the original format
            - Focus on clarity and readability
            - Avoid copying full sentences unless absolutely necessary

            Example output structure:
            <document structure>
            - Section 1: Introduction - sets context for the topic
            - Section 2: Analysis - presents main arguments and supporting data
            - Section 3: Conclusion - summarizes insights and implications

            Sections: 3
            Subsections: 5
            </document structure>

            <document summary>
            - This document discusses...
            - It identifies three major challenges...
            - The author concludes by recommending...

            (etc.)
            </document summary>

            Please proceed with your document analysis and structured summary.
        """

    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
