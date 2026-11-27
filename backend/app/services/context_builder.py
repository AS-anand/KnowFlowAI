
import json



class ContextBuilder:

    def build(self, chunks: list[dict]) -> str:
        context_sources = []

        for index, chunk in enumerate(chunks, start=1):
            context_sources.append({
                "source_number": index,
                "document_id": chunk["document_id"],
                "file_name": chunk["file_name"],
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"]
            })

        return json.dumps(
            context_sources,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    def build_conversation_history(
        self,
        messages: list[dict]
    ) -> str:
        """
        Serialize previous conversation messages.

        This history helps resolve conversational references.
        It is not a source of factual evidence for document Q&A.
        """
        history = []

        for message in messages:
            role = message["role"]

            if role not in ("user", "assistant"):
                continue

            history.append({
                "role": role,
                "content": message["content"]
            })

        return json.dumps(
            history,
            ensure_ascii=False,
            indent=2
        )
