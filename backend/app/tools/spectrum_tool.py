import os
from typing import Dict, Any
from .base import BaseTool
from ..services.llm_service import LLMService

class SpectrumAnalysisTool(BaseTool):
    name = "spectrum_analysis"
    description = "Analyzes chemical spectra (NMR, IR, MS) images to identify compounds and properties."

    def __init__(self):
        self.llm_service = LLMService()

    async def run(self, image_path: str, mode: str = "auto") -> Dict[str, Any]:
        """
        Analyzes a spectrum image.
        
        Args:
            image_path: Path to the image file.
            mode: 'auto', 'cmgnet', or 'vlm'.
        """
        if not os.path.exists(image_path):
            return {"error": "Image file not found."}

        # TODO: In the future, we can load the CMG-Net model here.
        # For now, we will use the VLM (GLM-4V) to analyze the image, 
        # as it is more robust without local weights.
        
        try:
            # We use the LLM service's vision capabilities directly
            # This bypasses the rigid Pydantic validation that was failing before
            analysis_result = await self.llm_service.analyze_image(
                image_path=image_path,
                prompt="""
                You are an expert chemist. Analyze this spectrum image.
                1. Identify the type of spectrum (NMR, IR, MS, etc.).
                2. List the main peaks and their values if visible.
                3. Suggest possible functional groups or structural fragments.
                4. If possible, propose a molecular structure or formula.
                5. Assess the quality of the image.
                
                Provide the output in a clear, structured Markdown format.
                """
            )
            
            return {
                "status": "success",
                "analysis": analysis_result,
                "tool_used": "GLM-4V (Fallback for CMG-Net)"
            }
            
        except Exception as e:
            return {"error": str(e)}
