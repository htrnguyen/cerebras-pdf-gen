import io
import zipfile
import requests
import datetime
from typing import List, Tuple


class StorageService:
    @staticmethod
    def upload_pdfs_as_zip(generated_pdf_data: List[Tuple[str, bytes]]) -> str:
        """
        Packs the tuples of (filename, bytes) into an in-memory ZIP and uploads it.
        Returns the direct download URL.
        """
        if not generated_pdf_data:
            raise ValueError("No files to zip")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"generated_pdfs_{timestamp}.zip"
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for filename, file_bytes in generated_pdf_data:
                zipf.writestr(filename, file_bytes)

        # Free memory of original list objects early
        generated_pdf_data.clear()

        zip_buffer.seek(0)
        response = requests.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": (zip_filename, zip_buffer)},
        )
        zip_buffer.close()

        if response.status_code == 200:
            data = response.json()
            direct_url = data["data"]["url"].replace(
                "tmpfiles.org/", "tmpfiles.org/dl/"
            )
            return direct_url
        else:
            raise ConnectionError(
                f"Upload failed: API returned status {response.status_code}"
            )
