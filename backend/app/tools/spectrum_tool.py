import os
from typing import Dict, Any
from rdkit import Chem
from .base import BaseTool
from ..services.llm_service import LLMService

class SpectrumAnalysisTool(BaseTool):
    name = "spectrum_analysis"
    description = "Analyzes chemical spectra (NMR, IR, MS) images to identify compounds and properties."

    def __init__(self):
        self.llm_service = LLMService()

    async def extract_peaks(self, image_path: str) -> list:
        """Extracts peak list from NMR image using VLM."""
        try:
            prompt = """
            You are an expert chemist. Analyze this 13C NMR spectrum image.
            Extract the chemical shifts (peaks) as a list of numbers (ppm).
            Return ONLY the list of numbers in JSON format, e.g., [170.5, 130.2, 25.4].
            Do not include any other text or markdown formatting.
            """
            response = await self.llm_service.analyze_image(image_path, prompt)
            
            # Clean up response
            import json
            import re
            
            # Remove markdown code blocks if present
            clean_response = re.sub(r'```json|```', '', response).strip()
            
            # Try to find a list pattern
            match = re.search(r'\[.*?\]', clean_response, re.DOTALL)
            if match:
                json_str = match.group(0)
                peaks = json.loads(json_str)
                return [float(p) for p in peaks if isinstance(p, (int, float, str)) and str(p).replace('.','',1).isdigit()]
            
            return []
        except Exception as e:
            print(f"Error extracting peaks: {e}")
            return []

    def predict_13c_signals(self, smiles: str) -> int:
        """Predicts the number of unique 13C NMR signals using RDKit symmetry."""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if not mol: return 0
            # Use canonical rank to find unique atoms
            # breakTies=False ensures symmetrically equivalent atoms get same rank
            ranks = list(Chem.CanonicalRankAtoms(mol, breakTies=False))
            
            # Filter for Carbons (atomic num 6)
            carbon_ranks = set()
            for i, atom in enumerate(mol.GetAtoms()):
                if atom.GetAtomicNum() == 6:
                    carbon_ranks.add(ranks[i])
            return len(carbon_ranks)
        except Exception as e:
            print(f"Error predicting signals: {e}")
            return 0

    async def verify_structure(self, smiles: str, experimental_peaks: list, tolerance: int = 2) -> dict:
        """
        Verifies if a structure is consistent with experimental peaks.
        Currently checks signal count consistency.
        """
        predicted_count = self.predict_13c_signals(smiles)
        experimental_count = len(experimental_peaks)
        
        # Simple check: Number of signals should be roughly equal
        # Note: Experimental peaks might overlap or be missing, so we allow tolerance
        diff = abs(predicted_count - experimental_count)
        is_consistent = diff <= tolerance
        
        return {
            "is_consistent": is_consistent,
            "predicted_signal_count": predicted_count,
            "experimental_signal_count": experimental_count,
            "difference": diff,
            "reason": f"Predicted {predicted_count} unique carbons, found {experimental_count} peaks."
        }


    async def propose_candidates(self, peaks: list, user_hint: str = "") -> list:
        """Asks LLM to propose structures based on peaks and user hints."""
        try:
            hint_text = f"\nUser Hint/Context: {user_hint}" if user_hint else ""
            
            prompt = f"""
            You are an expert organic chemist.
            I have a 13C NMR peak list (ppm): {peaks}
            {hint_text}
            
            Please propose 3 likely chemical structures (SMILES) that would produce this spectrum.
            Focus on small to medium organic molecules.
            If the user provided a formula or partial structure, ensure your proposals match it.
            
            Return ONLY a JSON list of SMILES strings.
            Example: ["CCO", "CC(=O)O", "c1ccccc1"]
            Do not include any other text.
            """
            response = await self.llm_service.generate_response(prompt)
            
            import json
            import re
            clean_response = re.sub(r'```json|```', '', response).strip()
            match = re.search(r'\[.*?\]', clean_response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return []
        except Exception as e:
            print(f"Error proposing candidates: {e}")
            return []

    async def analyze_peaks_from_text(self, peaks: list, user_hint: str = "") -> Dict[str, Any]:
        """Analyzes spectrum from text-based peak list using Agentic Flow."""
        try:
            from app.models.cmgnet.inference import validate_candidates
            
            # 1. Propose candidates
            candidates = await self.propose_candidates(peaks, user_hint)
            if not candidates:
                 return {
                    "status": "error",
                    "error": "LLM could not propose valid candidates.",
                    "tool_used": "Agentic NMR Analyst (Text Mode)"
                }
                
            # 2. Validate candidates
            validation = validate_candidates(candidates, peaks)
            
            if not validation.get("success"):
                return {
                    "status": "error",
                    "error": validation.get("error"),
                    "tool_used": "Agentic NMR Analyst (Text Mode)"
                }
                
            best = validation.get("best_candidate")
            return {
                "status": "success",
                "analysis": f"**Agentic NMR Analysis (Text Mode)**\n\n"
                            f"**Input Peaks:** {peaks}\n\n"
                            f"**User Hint:** {user_hint if user_hint else 'None'}\n"
                            f"**Best Candidate:** `{best['smiles']}`\n"
                            f"**Confidence Score:** {best['score']:.2f}\n"
                            f"**Reasoning:** Predicted {best['predicted_peak_count']} unique carbons vs {best['observed_peak_count']} observed peaks.\n\n"
                            f"**Other Candidates:**\n" + 
                            "\n".join([f"- `{c['smiles']}` (Score: {c['score']:.2f})" for c in validation.get('all_candidates', [])[1:]]),
                "data": validation,
                "tool_used": "Agentic NMR Analyst (Text Mode)"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Text analysis error: {str(e)}",
                "tool_used": "Agentic NMR Analyst (Text Mode)"
            }

    async def run(self, image_path: str, mode: str = "auto", user_hint: str = "") -> Dict[str, Any]:
        """
        Analyzes a spectrum image.
        
        Args:
            image_path: Path to the image file.
            mode: 'auto', 'cmgnet', or 'vlm'.
            user_hint: Additional context provided by the user (e.g. formula).
        """
        if not os.path.exists(image_path):
            return {"error": "Image file not found."}

        if mode == 'cmgnet':
            try:
                from app.models.cmgnet.inference import predict_structure, validate_candidates
                
                # 1. Extract peaks using VLM
                peaks = await self.extract_peaks(image_path)
                
                if not peaks:
                    return {
                        "status": "error",
                        "error": "Could not extract peaks from image using VLM.",
                        "tool_used": "CMG-Net (Peak Extraction Failed)"
                    }
                
                # 2. Try CMG-Net (or Agentic Flow)
                result = predict_structure(peaks)
                
                if result.get("requires_agentic_flow"):
                    # Fallback to Agentic Analysis
                    candidates = await self.propose_candidates(peaks, user_hint)
                    if not candidates:
                         return {
                            "status": "error",
                            "error": "LLM could not propose valid candidates.",
                            "tool_used": "Agentic NMR Analyst"
                        }
                        
                    validation = validate_candidates(candidates, peaks)
                    
                    if not validation.get("success"):
                        return {
                            "status": "error",
                            "error": validation.get("error"),
                            "tool_used": "Agentic NMR Analyst"
                        }
                        
                    best = validation.get("best_candidate")
                    return {
                        "status": "success",
                        "analysis": f"**Agentic NMR Analysis**\n\n"
                                    f"**Extracted Peaks:** {peaks}\n\n"
                                    f"**User Hint:** {user_hint if user_hint else 'None'}\n"
                                    f"**Best Candidate:** `{best['smiles']}`\n"
                                    f"**Confidence Score:** {best['score']:.2f}\n"
                                    f"**Reasoning:** Predicted {best['predicted_peak_count']} unique carbons vs {best['observed_peak_count']} observed peaks.\n\n"
                                    f"**Other Candidates:**\n" + 
                                    "\n".join([f"- `{c['smiles']}` (Score: {c['score']:.2f})" for c in validation.get('all_candidates', [])[1:]]),
                        "data": validation,
                        "tool_used": "Agentic NMR Analyst (VLM + RDKit)"
                    }

                # Normal CMG-Net path (if weights existed)
                if not result.get("success"):
                     return {
                        "status": "error", 
                        "error": result.get("error"),
                        "tool_used": "CMG-Net"
                    }

                return {
                    "status": "success",
                    "analysis": f"Predicted Structure (SMILES): {result.get('predicted_smiles')}\nConfidence: {result.get('confidence')}",
                    "data": result,
                    "tool_used": "CMG-Net"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"CMG-Net integration error: {str(e)}",
                    "tool_used": "CMG-Net"
                }

        # Default to VLM (GLM-4V)
        try:
            # We use the LLM service's vision capabilities directly
            # This bypasses the rigid Pydantic validation that was failing before
            prompt = """
                You are an expert chemist. Analyze this spectrum image.
                1. Identify the type of spectrum (NMR, IR, MS, etc.).
                2. List the main peaks and their values if visible.
                3. Suggest possible functional groups or structural fragments.
                4. If possible, propose a molecular structure or formula.
                5. Assess the quality of the image.
                
                Provide the output in a clear, structured Markdown format.
                """
            
            if user_hint:
                prompt += f"\n\nAdditional Context provided by user: {user_hint}\nPlease take this context into account during your analysis."

            analysis_result = await self.llm_service.analyze_image(
                image_path=image_path,
                prompt=prompt
            )
            
            return {
                "status": "success",
                "analysis": analysis_result,
                "tool_used": "GLM-4V (Fallback for CMG-Net)"
            }
            
        except Exception as e:
            return {"error": str(e)}
