
import os

import httpx
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Indian Legal Compliance Assistant",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Indian Legal Compliance Assistant")
st.caption(
    "Ask questions about Indian legal and business compliance "
    "using the documents indexed in the knowledge base."
)

with st.sidebar:
    st.header("📊 Knowledge Base")

    if st.button("Refresh statistics"):
        st.rerun()

    try:
        response = httpx.get(f"{API_URL}/stats", timeout=10)
        response.raise_for_status()
        stats = response.json()
        st.metric("Indexed chunks", stats.get("total_chunks", 0))
        st.caption(f"Collection: {stats.get('collection', 'unknown')}")
    except httpx.HTTPError:
        st.warning("The backend API is unavailable.")
        st.caption(f"API endpoint: {API_URL}")

st.subheader("Ask a legal compliance question")

query = st.text_area(
    "Your question",
    height=120,
    placeholder="Ask a question about the documents in the knowledge base.",
)

top_k = st.slider("Number of relevant passages", 1, 10, 5)

if st.button("🔎 Search and generate answer", type="primary"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving passages and generating an answer..."):
            try:
                response = httpx.post(
                    f"{API_URL}/query",
                    json={"query": query.strip(), "top_k": top_k},
                    timeout=120,
                )

                if response.is_error:
                    try:
                        detail = response.json().get("detail", "Request failed.")
                    except ValueError:
                        detail = "Unexpected response from the backend."
                    st.error(f"Request failed ({response.status_code}): {detail}")
                else:
                    data = response.json()

                    st.subheader("📝 Answer")
                    st.write(data.get("answer", "No answer was returned."))

                    st.subheader("📚 Sources")
                    sources = data.get("sources", [])
                    if sources:
                        for source in sources:
                            st.write(f"- {source}")
                    else:
                        st.info("No source labels were returned.")

                    with st.expander("View retrieved passages"):
                        chunks = data.get("retrieved_chunks", [])
                        if not chunks:
                            st.info("No passages were returned.")
                        for index, chunk in enumerate(chunks, start=1):
                            st.markdown(
                                f"**Passage {index}** — "
                                f"Score: `{chunk.get('score', 'N/A')}`"
                            )
                            st.caption(
                                chunk.get("legal_address")
                                or chunk.get("source")
                                or "Unknown source"
                            )
                            st.write(chunk.get("text", ""))
                            st.divider()

            except httpx.TimeoutException:
                st.error("The request timed out. Please try again.")
            except httpx.HTTPError as exc:
                st.error(f"Could not communicate with the backend: {exc}")
            except ValueError:
                st.error("The backend returned invalid JSON.")
