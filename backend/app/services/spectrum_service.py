from typing import Dict, Any, Optional
from pathlib import Path
import asyncio
from typing import Optional, Dict, Any
from loguru import logger
from app.services.llm_service import LLMService
from app.core.config import settings
import os

class SpectrumAnalysisService:
    """光谱分析服务 - 专门处理化学光谱识别"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        self.supported_spectrum_types = ['IR', 'NMR', 'UV', '红外', '核磁', '紫外']
    
    async def analyze_spectrum(
        self,
        image_path: str,
        spectrum_type: str,
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """分析光谱图像"""
        try:
            logger.info(f"开始分析{spectrum_type}光谱: {image_path}")
            
            # 验证输入
            validation_result = await self._validate_input(image_path, spectrum_type)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'spectrum_type': spectrum_type
                }
            
            # 尝试使用CMG-Net进行核磁共振分析
            if spectrum_type.upper() in ['NMR', '13C NMR', 'CARBON NMR', '核磁']:
                try:
                    from app.tools.spectrum_tool import SpectrumAnalysisTool
                    tool = SpectrumAnalysisTool()
                    tool_result = await tool.run(image_path, mode='cmgnet')
                    
                    if tool_result.get('status') == 'success' and tool_result.get('tool_used') == 'CMG-Net':
                        logger.info("CMG-Net分析成功")
                        return {
                            'success': True,
                            'spectrum_type': spectrum_type,
                            'raw_analysis': tool_result.get('analysis'),
                            'parsed_result': {
                                'spectrum_type': spectrum_type,
                                'analysis_sections': {'Structure Prediction': [tool_result.get('analysis')]},
                                'key_findings': [{'type': 'Structure', 'content': [tool_result.get('analysis')]}],
                                'confidence_level': 'high'
                            },
                            'image_path': image_path
                        }
                except Exception as e:
                    logger.warning(f"CMG-Net分析尝试失败，回退到通用LLM分析: {e}")

                # 尝试基于RDKit的验证流程 (Verification Workflow)
                try:
                    logger.info("尝试使用RDKit验证流程")
                    # 确保工具已初始化
                    if 'tool' not in locals():
                        from app.tools.spectrum_tool import SpectrumAnalysisTool
                        tool = SpectrumAnalysisTool()

                    peaks = await tool.extract_peaks(image_path)
                    if peaks:
                        logger.info(f"提取到的峰值: {peaks}")
                        prompt = f"""
                        Based on these 13C NMR peaks (ppm): {peaks}, propose 3 possible chemical structures (SMILES).
                        Return ONLY a JSON list of SMILES strings, e.g., ["C1CCCCC1", "CCO"].
                        Do not include any other text.
                        """
                        candidates_response = await self.llm_service.generate_response(prompt)
                        
                        import json
                        import re
                        clean_response = re.sub(r'```json|```', '', candidates_response).strip()
                        match = re.search(r'\[.*?\]', clean_response, re.DOTALL)
                        
                        best_candidate = None
                        best_score = -1
                        
                        if match:
                            candidates = json.loads(match.group(0))
                            logger.info(f"LLM提出的候选结构: {candidates}")
                            
                            for smiles in candidates:
                                verification = await tool.verify_structure(smiles, peaks)
                                if verification['is_consistent']:
                                    # Simple scoring: lower difference is better
                                    score = 100 - verification['difference']
                                    if score > best_score:
                                        best_score = score
                                        best_candidate = {
                                            'smiles': smiles,
                                            'verification': verification
                                        }
                        
                        if best_candidate:
                            logger.info(f"找到最佳候选结构: {best_candidate['smiles']}")
                            return {
                                'success': True,
                                'spectrum_type': spectrum_type,
                                'raw_analysis': f"Predicted Structure: {best_candidate['smiles']}\nVerification: {best_candidate['verification']}",
                                'parsed_result': {
                                    'spectrum_type': spectrum_type,
                                    'analysis_sections': {'Structure Prediction': [f"Proposed Structure: {best_candidate['smiles']}", f"Verification: {best_candidate['verification']}"]},
                                    'key_findings': [{'type': 'Structure', 'content': [f"Proposed Structure: {best_candidate['smiles']}"]}],
                                    'confidence_level': 'medium'
                                },
                                'image_path': image_path
                            }
                except Exception as e:
                    logger.warning(f"RDKit验证流程失败: {e}")

            # 使用LLM进行光谱分析
            analysis_result = await self.llm_service.analyze_spectrum_image(
                image_path=image_path,
                spectrum_type=spectrum_type,
                additional_context=additional_info or ""
            )
            
            # 解析分析结果
            parsed_result = await self._parse_analysis_result(
                analysis_result, spectrum_type
            )
            
            logger.info(f"{spectrum_type}光谱分析完成")
            
            return {
                'success': True,
                'spectrum_type': spectrum_type,
                'raw_analysis': analysis_result,
                'parsed_result': parsed_result,
                'image_path': image_path
            }
            
        except Exception as e:
            logger.error(f"光谱分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'spectrum_type': spectrum_type,
                'image_path': image_path
            }
    
    async def batch_analyze_spectra(
        self,
        image_paths: list,
        spectrum_types: list,
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """批量分析多个光谱"""
        try:
            if len(image_paths) != len(spectrum_types):
                raise ValueError("图像路径和光谱类型数量不匹配")
            
            results = []
            for image_path, spectrum_type in zip(image_paths, spectrum_types):
                result = await self.analyze_spectrum(
                    image_path, spectrum_type, additional_info
                )
                results.append(result)
            
            return {
                'success': True,
                'batch_results': results,
                'total_count': len(results),
                'success_count': sum(1 for r in results if r['success'])
            }
            
        except Exception as e:
            logger.error(f"批量光谱分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _validate_input(self, image_path: str, spectrum_type: str) -> Dict[str, Any]:
        """验证输入参数"""
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return {
                'valid': False,
                'error': f"图像文件不存在: {image_path}"
            }
        
        # 检查文件格式
        file_ext = Path(image_path).suffix.lower()
        if file_ext not in self.supported_formats:
            return {
                'valid': False,
                'error': f"不支持的图像格式: {file_ext}。支持的格式: {', '.join(self.supported_formats)}"
            }
        
        # 检查光谱类型（允许auto自动识别）
        if spectrum_type.lower() != "auto" and spectrum_type.upper() not in [t.upper() for t in self.supported_spectrum_types]:
            return {
                'valid': False,
                'error': f"不支持的光谱类型: {spectrum_type}。支持的类型: auto(自动识别), {', '.join(self.supported_spectrum_types)}"
            }
        
        # 检查文件大小
        file_size = os.path.getsize(image_path)
        max_size = getattr(settings, 'MAX_IMAGE_SIZE', 10 * 1024 * 1024)  # 默认10MB
        if file_size > max_size:
            return {
                'valid': False,
                'error': f"图像文件过大: {file_size / 1024 / 1024:.1f}MB，最大允许: {max_size / 1024 / 1024:.1f}MB"
            }
        
        return {'valid': True}
    
    async def _parse_analysis_result(
        self,
        raw_result: str,
        spectrum_type: str
    ) -> Dict[str, Any]:
        """解析分析结果，提取结构化信息"""
        try:
            # 基础解析
            parsed = {
                'spectrum_type': spectrum_type,
                'analysis_sections': {},
                'key_findings': [],
                'confidence_level': 'medium'  # 默认置信度
            }
            
            # 按段落分割结果
            sections = raw_result.split('\n\n')
            current_section = None
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                # 识别标题
                if section.startswith('**') and section.endswith('**'):
                    current_section = section.strip('*').strip()
                    parsed['analysis_sections'][current_section] = []
                elif current_section:
                    parsed['analysis_sections'][current_section].append(section)
                else:
                    # 没有明确标题的内容
                    if 'general' not in parsed['analysis_sections']:
                        parsed['analysis_sections']['general'] = []
                    parsed['analysis_sections']['general'].append(section)
            
            # 提取关键发现
            parsed['key_findings'] = await self._extract_key_findings(
                raw_result, spectrum_type
            )
            
            return parsed
            
        except Exception as e:
            logger.error(f"解析分析结果失败: {str(e)}")
            return {
                'spectrum_type': spectrum_type,
                'raw_content': raw_result,
                'parse_error': str(e)
            }
    
    async def _extract_key_findings(
        self,
        analysis_text: str,
        spectrum_type: str
    ) -> list:
        """从分析文本中提取关键发现"""
        key_findings = []
        
        try:
            # 根据光谱类型提取不同的关键信息
            if spectrum_type.upper() == 'IR' or '红外' in spectrum_type:
                # 提取官能团信息
                import re
                functional_groups = re.findall(
                    r'([A-Z]-[A-Z]|C=O|O-H|N-H|C-H|C=C|C≡C)',
                    analysis_text
                )
                if functional_groups:
                    key_findings.append({
                        'type': 'functional_groups',
                        'content': list(set(functional_groups))
                    })
                
                # 提取波数信息
                wavenumbers = re.findall(r'(\d{3,4})\s*cm⁻¹', analysis_text)
                if wavenumbers:
                    key_findings.append({
                        'type': 'wavenumbers',
                        'content': wavenumbers
                    })
            
            elif spectrum_type.upper() == 'NMR' or '核磁' in spectrum_type:
                # 提取化学位移信息
                import re
                chemical_shifts = re.findall(r'δ\s*(\d+\.\d+)', analysis_text)
                if chemical_shifts:
                    key_findings.append({
                        'type': 'chemical_shifts',
                        'content': chemical_shifts
                    })
                
                # 提取偶合信息
                coupling_patterns = re.findall(
                    r'(单峰|双峰|三重峰|四重峰|多重峰|singlet|doublet|triplet|quartet|multiplet)',
                    analysis_text
                )
                if coupling_patterns:
                    key_findings.append({
                        'type': 'coupling_patterns',
                        'content': list(set(coupling_patterns))
                    })
            
            elif spectrum_type.upper() == 'UV' or '紫外' in spectrum_type:
                # 提取波长信息
                import re
                wavelengths = re.findall(r'(\d{3})\s*nm', analysis_text)
                if wavelengths:
                    key_findings.append({
                        'type': 'wavelengths',
                        'content': wavelengths
                    })
        
        except Exception as e:
            logger.error(f"提取关键发现失败: {str(e)}")
        
        return key_findings
    
    def get_supported_spectrum_types(self) -> list:
        """获取支持的光谱类型"""
        return self.supported_spectrum_types.copy()
    
    def get_supported_formats(self) -> list:
        """获取支持的图像格式"""
        return self.supported_formats.copy()
    
    async def format_analysis_for_visualization(self, analysis_data: dict) -> dict:
        """
        使用DeepSeek模型将分析结果格式化为可视化内容
        
        Args:
            analysis_data: 包含分析结果的JSON数据
        
        Returns:
            格式化后的可视化分析结果
        """
        try:
            logger.info("开始格式化分析结果为可视化内容")
            
            # 构建提示词，让DeepSeek生成结构化的可视化内容
            visualization_prompt = f"""
请将以下光谱分析结果转换为结构化的可视化展示内容。请生成包含以下部分的JSON格式结果：

1. summary: 分析结果的简要总结
2. key_findings: 关键发现列表，每个发现包含标题和描述
3. detailed_analysis: 详细分析内容，包含多个分析段落
4. chemical_info: 化学信息，如化学位移、官能团、波数等
5. recommendations: 建议和结论

原始分析数据：
{analysis_data}

请确保输出是有效的JSON格式，内容要专业、准确、易于理解。
"""
            
            # 使用LLM服务格式化结果
            if hasattr(self.llm_service, 'text_client') and self.llm_service.text_client:
                formatted_result = await self.llm_service._analyze_spectrum_with_deepseek(
                    vision_description="",
                    spectrum_type="visualization",
                    additional_context=visualization_prompt
                )
                
                # 尝试解析JSON结果
                import json
                try:
                    visualization_json = json.loads(formatted_result)
                    return visualization_json
                except json.JSONDecodeError:
                    # 如果不是有效JSON，返回格式化的文本
                    return {
                        "summary": "分析结果可视化",
                        "formatted_content": formatted_result,
                        "raw_data": analysis_data
                    }
            else:
                # 如果DeepSeek不可用，返回基本格式化结果
                return {
                    "summary": "分析结果展示",
                    "message": "DeepSeek模型不可用，显示原始分析结果",
                    "raw_data": analysis_data
                }
                
        except Exception as e:
            logger.error(f"分析结果可视化格式化失败: {str(e)}")
            return {
                "summary": "格式化失败",
                "error": str(e),
                "raw_data": analysis_data
            }