import traceback
import io
from app.models.state import global_state
from app.services.ai_service import AIService
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService

class DocumentGenerationWorkflow:
    @staticmethod
    def run(api_key: str, num_files: int):
        """Background task to sequence the generator calls."""
        global_state.start_generation(num_files)
        
        try:
            ai_service = AIService(api_key=api_key)

            global_state.add_message(f"Asking AI to invent {num_files} distinct topics...")
            topic_areas = ai_service.generate_topics(num_files)
            global_state.add_message(f"Successfully drew {len(topic_areas)} distinct topics from AI.")

            for i in range(1, num_files + 1):
                if not global_state.is_currently_running:
                    break

                current_topic = topic_areas[i - 1]
                global_state.add_message(f"Generating file {i}/{num_files}: {current_topic}...")

                try:
                    full_topic, base_filename, content = ai_service.generate_single_document_content(current_topic)
                    
                    pdf_buffer = io.BytesIO()
                    success = PDFService.create_pdf(pdf_buffer, content)
                    
                    if success:
                        pdf_bytes = pdf_buffer.getvalue()
                        pdf_buffer.close()
                        
                        global_state.increment_completed(f"{base_filename}.pdf", pdf_bytes)
                        global_state.add_message(f"[{i}] Created: {base_filename}.pdf")
                    else:
                        raise RuntimeError("PDF writing failed internally")
                        
                except Exception as e:
                    error_msg = str(e)
                    traceback.print_exc()
                    global_state.increment_failed()
                    global_state.add_message(f"[{i}] Failed: {error_msg[:100]}")

            # Upload phase if at least one file succeeded
            status = global_state.get_public_status()
            if status["completed"] > 0:
                global_state.add_message(f"Zipping {status['completed']} files in memory...")
                
                try:
                    pdf_data = global_state.get_and_clear_pdf_data()
                    download_url = StorageService.upload_pdfs_as_zip(pdf_data)
                    global_state.set_download_url(download_url)
                    global_state.add_message(f"Upload successful! Direct URL: {download_url}")
                except Exception as upload_err:
                    global_state.add_message(f"Upload logic failed: {str(upload_err)}")

        except Exception as e:
            traceback.print_exc()
            global_state.add_message(f"Fatal error initializing workflow: {str(e)}")
        finally:
            global_state.stop_generation()
            global_state.add_message("Process finished.")
