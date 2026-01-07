import asyncio
from pathlib import Path
import time

import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests
from vector_db import QdrantStorage

load_dotenv()

# ============================================================================
# CONSTANTS - Timeout settings
# ============================================================================
DEFAULT_QUERY_TIMEOUT_SECONDS = 600.0  # Timeout per query LLM (10 minuti) - modelli locali possono essere lenti
DEFAULT_POLL_INTERVAL_SECONDS = 2.0  # Intervallo tra controlli dello stato durante polling (secondi)
DEFAULT_WAIT_TIMEOUT_SECONDS = 300.0  # Timeout generico per attesa operazioni (5 minuti)
DEFAULT_POLL_INTERVAL_WAIT_SECONDS = 1.0  # Intervallo polling per wait_for_run_output (secondi)

# ============================================================================
# CONSTANTS - Query settings
# ============================================================================
DEFAULT_TOP_K_MIN = 1  # Numero minimo di chunk da recuperare
DEFAULT_TOP_K_MAX = 20  # Numero massimo di chunk da recuperare
DEFAULT_TOP_K_VALUE = 5  # Valore di default per top_k (numero chunk)

# ============================================================================
# CONSTANTS - UI settings
# ============================================================================
DEFAULT_CHUNKS_PREVIEW_LIMIT = 20  # Numero massimo di chunk da mostrare nell'anteprima
DEFAULT_CHUNK_TEXT_AREA_HEIGHT = 100  # Altezza in pixel dell'area di testo per i chunk
PROGRESS_BAR_CAP = 0.95  # Valore massimo della progress bar prima del completamento (0-1)
CHUNK_ID_PREVIEW_LENGTH = 20  # Lunghezza caratteri per preview ID chunk

# ============================================================================
# CONSTANTS - API endpoints
# ============================================================================
INNGEST_API_BASE_DEFAULT = "http://127.0.0.1:8288/v1"  # URL base API Inngest
INNGEST_DASHBOARD_URL = "http://localhost:8288"  # URL dashboard Inngest

st.set_page_config(page_title="RAG Ingest PDF", page_icon="📄", layout="wide")


@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="rag_app", is_production=False)


def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_bytes = file.getbuffer()
    file_path.write_bytes(file_bytes)
    return file_path


async def send_rag_ingest_event(pdf_path: Path) -> None:
    client = get_inngest_client()
    await client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )


# Helper functions (defined outside page blocks)
async def send_rag_query_event(question: str, top_k: int) -> None:
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/query_pdf_ai",
            data={
                "question": question,
                "top_k": top_k,
            },
        )
    )

    return result[0]


def _inngest_api_base() -> str:
    # Local dev server default; configurable via env
    return os.getenv("INNGEST_API_BASE", INNGEST_API_BASE_DEFAULT)


def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def wait_for_run_output(
    event_id: str, timeout_s: float = DEFAULT_WAIT_TIMEOUT_SECONDS, poll_interval_s: float = DEFAULT_POLL_INTERVAL_WAIT_SECONDS
) -> dict:
    """
    Wait for Inngest function to complete.

    Args:
        event_id: The event ID to wait for
        timeout_s: Maximum time to wait in seconds (default 5 minutes for LLM queries)
        poll_interval_s: How often to check status in seconds
    """
    start = time.time()
    last_status = None
    last_error = None

    while True:
        try:
            runs = fetch_runs(event_id)
            if runs:
                run = runs[0]
                status = run.get("status")
                last_status = status or last_status

                # Check for errors in the run
                if "error" in run:
                    last_error = run.get("error", "Unknown error")

                if status in ("Completed", "Succeeded", "Success", "Finished"):
                    output = run.get("output") or {}
                    # Check if there's an error in the output
                    if "error" in output:
                        raise RuntimeError(
                            f"Function completed with error: {output.get('error')}"
                        )
                    return output

                if status in ("Failed", "Cancelled"):
                    error_msg = last_error or "Unknown error"
                    raise RuntimeError(f"Function run {status}: {error_msg}")
        except requests.exceptions.RequestException as e:
            # If we can't fetch runs, continue polling but log the error
            pass

        elapsed = time.time() - start
        if elapsed > timeout_s:
            error_msg = f"Timed out after {timeout_s:.0f} seconds"
            if last_status:
                error_msg += f" (last status: {last_status})"
            if last_error:
                error_msg += f" (error: {last_error})"
            raise TimeoutError(error_msg)

        time.sleep(poll_interval_s)


# Sidebar navigation
st.sidebar.title("Navigation")

# Initialize session state for page navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "Upload & Query"

# Navigation buttons
if st.sidebar.button(
    "📤 Upload & Query",
    use_container_width=True,
    type=(
        "primary" if st.session_state.current_page == "Upload & Query" else "secondary"
    ),
):
    st.session_state.current_page = "Upload & Query"
    st.rerun()

if st.sidebar.button(
    "📚 Embedded Files",
    use_container_width=True,
    type=(
        "primary" if st.session_state.current_page == "Embedded Files" else "secondary"
    ),
):
    st.session_state.current_page = "Embedded Files"
    st.rerun()

page = st.session_state.current_page

if page == "Upload & Query":
    # ============================================
    # PAGE 1: Upload & Query
    # ============================================
    st.title("Upload a PDF to Ingest")
    uploaded = st.file_uploader(
        "Choose a PDF", type=["pdf"], accept_multiple_files=False
    )

    if uploaded is not None:
        with st.spinner("Uploading and triggering ingestion..."):
            path = save_uploaded_pdf(uploaded)
            # Kick off the event and block until the send completes
            asyncio.run(send_rag_ingest_event(path))
            # Small pause for user feedback continuity
            time.sleep(0.3)
        st.success(f"Triggered ingestion for: {path.name}")
        st.caption("You can upload another PDF if you like.")

    st.divider()
    st.title("Ask a question about your PDFs")

    with st.form("rag_query_form"):
        question = st.text_input("Your question")
        top_k = st.number_input(
            "How many chunks to retrieve",
            min_value=DEFAULT_TOP_K_MIN,
            max_value=DEFAULT_TOP_K_MAX,
            value=DEFAULT_TOP_K_VALUE,
            step=1,
        )
        submitted = st.form_submit_button("Ask")

        if submitted and question.strip():
            try:
                with st.spinner("Sending event and generating answer..."):
                    # Fire-and-forget event to Inngest for observability/workflow
                    event_id = asyncio.run(
                        send_rag_query_event(question.strip(), int(top_k))
                    )

                # Show progress while waiting
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Poll the local Inngest API for the run's output with longer timeout
                # LLM queries can take time, especially with local models like Ollama
                try:
                    # Custom polling with progress updates
                    start_time = time.time()
                    timeout_s = DEFAULT_QUERY_TIMEOUT_SECONDS  # 10 minutes for LLM queries
                    poll_interval = DEFAULT_POLL_INTERVAL_SECONDS  # Check every 2 seconds
                    last_status = None

                    while True:
                        elapsed = time.time() - start_time
                        progress = min(
                            elapsed / timeout_s, PROGRESS_BAR_CAP
                        )  # Cap at 95% until done
                        progress_bar.progress(progress)

                        try:
                            runs = fetch_runs(event_id)
                            if runs:
                                run = runs[0]
                                status = run.get("status", "Unknown")
                                last_status = status

                                if status == "Running":
                                    status_text.text(
                                        f"⏳ Processing... ({int(elapsed)}s)"
                                    )
                                elif status in (
                                    "Completed",
                                    "Succeeded",
                                    "Success",
                                    "Finished",
                                ):
                                    progress_bar.progress(1.0)
                                    status_text.text("✅ Complete!")
                                    output = run.get("output") or {}
                                    if "error" in output:
                                        raise RuntimeError(
                                            f"Function completed with error: {output.get('error')}"
                                        )

                                    progress_bar.empty()
                                    status_text.empty()

                                    answer = output.get("answer", "")
                                    sources = output.get("sources", [])

                                    st.subheader("Answer")
                                    st.write(answer or "(No answer)")
                                    if sources:
                                        st.caption("Sources")
                                        for s in sources:
                                            st.write(f"- {s}")
                                    break

                                elif status in ("Failed", "Cancelled"):
                                    error_msg = run.get("error", "Unknown error")
                                    raise RuntimeError(
                                        f"Function run {status}: {error_msg}"
                                    )
                        except requests.exceptions.RequestException:
                            # Continue polling even if one request fails
                            pass

                        if elapsed > timeout_s:
                            raise TimeoutError(
                                f"Timed out after {timeout_s:.0f} seconds"
                                + (
                                    f" (last status: {last_status})"
                                    if last_status
                                    else ""
                                )
                            )

                        time.sleep(poll_interval)

                except TimeoutError as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"⏱️ Query timeout: {str(e)}")
                    st.info(
                        "💡 **Tip:** LLM queries can take time, especially with local models like Ollama. "
                        f"The query might still be processing. Try refreshing the page or check the Inngest dashboard at {INNGEST_DASHBOARD_URL}"
                    )
                except RuntimeError as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ Error during query: {str(e)}")

            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.exception(e)


if page == "Embedded Files":
    # ============================================
    # PAGE 2: Embedded Files
    # ============================================
    st.title("📚 Embedded Files")
    st.caption("View all files that have been embedded in the vector database")

    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    try:
        # Get storage instance
        storage = QdrantStorage()

        # Get all sources
        with st.spinner("Loading embedded files..."):
            sources_data = storage.get_all_sources()

        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Files", sources_data["total_sources"])
        with col2:
            st.metric("Total Chunks", sources_data["total_chunks"])
        with col3:
            avg_chunks = (
                sources_data["total_chunks"] / sources_data["total_sources"]
                if sources_data["total_sources"] > 0
                else 0
            )
            st.metric("Avg Chunks/File", f"{avg_chunks:.1f}")

        st.divider()

        # Display files list
        if sources_data["total_sources"] == 0:
            st.info(
                "No files have been embedded yet. Upload a PDF in the 'Upload & Query' page to get started."
            )
        else:
            st.subheader("Files List")

            # Sort by chunk count (descending)
            sorted_sources = sorted(
                sources_data["sources"].items(), key=lambda x: x[1], reverse=True
            )

            # Display each file
            for source_id, chunk_count in sorted_sources:
                with st.expander(
                    f"📄 {source_id} ({chunk_count} chunks)", expanded=False
                ):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Source ID:** {source_id}")
                        st.write(f"**Number of chunks:** {chunk_count}")

                    with col2:
                        if st.button(
                            "View Chunks",
                            key=f"view_{source_id}",
                            use_container_width=True,
                        ):
                            st.session_state[f"show_chunks_{source_id}"] = True

                    # Show chunks if requested
                    if st.session_state.get(f"show_chunks_{source_id}", False):
                        st.write("---")
                        st.write(f"**Chunks preview (first {DEFAULT_CHUNKS_PREVIEW_LIMIT}):**")

                        with st.spinner(f"Loading chunks for {source_id}..."):
                            chunks = storage.get_chunks_by_source(source_id, limit=DEFAULT_CHUNKS_PREVIEW_LIMIT)

                        if chunks:
                            for i, chunk in enumerate(chunks, 1):
                                with st.container():
                                    st.write(
                                        f"**Chunk {i}** (ID: {chunk['id'][:CHUNK_ID_PREVIEW_LENGTH]}...)"
                                    )
                                    st.text_area(
                                        "Text",
                                        value=chunk["text"],
                                        height=DEFAULT_CHUNK_TEXT_AREA_HEIGHT,
                                        key=f"chunk_{source_id}_{i}",
                                        disabled=True,
                                    )
                                    st.write("---")

                            if len(chunks) == DEFAULT_CHUNKS_PREVIEW_LIMIT:
                                st.info(
                                    f"Showing first {DEFAULT_CHUNKS_PREVIEW_LIMIT} chunks. Total chunks: {chunk_count}"
                                )
                        else:
                            st.warning("No chunks found for this source.")

                        if st.button("Hide Chunks", key=f"hide_{source_id}"):
                            st.session_state[f"show_chunks_{source_id}"] = False
                            st.rerun()

    except Exception as e:
        st.error(f"Error loading embedded files: {str(e)}")
        st.exception(e)
